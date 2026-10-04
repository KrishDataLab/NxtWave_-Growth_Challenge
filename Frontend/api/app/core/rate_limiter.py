import time
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, Request, status

import os
import json
import urllib.request
import urllib.error

class SimpleRateLimiter:
    """
    Hybrid distributed rate limiter:
    1. Uses Upstash Redis REST API if UPSTASH_REDIS_REST_URL is set.
    2. Falls back seamlessly to in-memory sliding window per IP.
    """
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def check_rate_limit(self, request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        redis_url = os.environ.get("UPSTASH_REDIS_REST_URL")
        redis_token = os.environ.get("UPSTASH_REDIS_REST_TOKEN")

        if redis_url and redis_token:
            try:
                # Upstash REST INCR API
                key = f"rate_limit:{client_ip}:{int(now // 60)}"
                req_url = f"{redis_url.rstrip('/')}/incr/{key}"
                req = urllib.request.Request(
                    req_url,
                    headers={"Authorization": f"Bearer {redis_token}"}
                )
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    count = data.get("result", 1)
                    if count == 1:
                        # Set 60s expiration on new key
                        exp_url = f"{redis_url.rstrip('/')}/expire/{key}/60"
                        exp_req = urllib.request.Request(
                            exp_url,
                            headers={"Authorization": f"Bearer {redis_token}"}
                        )
                        urllib.request.urlopen(exp_req, timeout=2.0)

                    if count > self.requests_per_minute:
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Too many registration attempts. Please wait a minute before trying again."
                        )
                return
            except HTTPException:
                raise
            except Exception:
                pass  # Fall back to in-memory on Redis error

        # In-memory fallback
        window_start = now - 60.0
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if ts > window_start
        ]

        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many registration attempts. Please wait a minute before trying again."
            )

        self.requests[client_ip].append(now)

registration_rate_limiter = SimpleRateLimiter(requests_per_minute=10)
