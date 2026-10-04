import time
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, Request, status

class SimpleRateLimiter:
    """
    Lightweight in-memory rate limiter to protect public endpoints against repeated abuse.
    Stores request timestamps per IP address.
    """
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def check_rate_limit(self, request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        window_start = now - 60.0

        # Filter timestamps outside the 1-minute window
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
