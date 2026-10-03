import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

test_app = FastAPI()

@test_app.get("/api/v1/health")
def health_test():
    return {"status": "ok", "source": "minimal_index"}

@test_app.api_route("/api/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
def route_to_backend(request: Request, path: str):
    try:
        from app.main import app as real_app
        # If import succeeds, return success info
        return {"status": "imported", "path": path}
    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "traceback": traceback.format_exc().splitlines()}
        )

app = test_app
