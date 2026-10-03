import sys
import os

# Ensure Backend module is discoverable by Python Serverless Function
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.main import app
except Exception as e:
    import traceback
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    err_msg = str(e)
    err_tb = traceback.format_exc().splitlines()
    app = FastAPI()
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"])
    def init_error_fallback(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Backend initialization failed",
                "detail": err_msg,
                "traceback": err_tb
            }
        )
