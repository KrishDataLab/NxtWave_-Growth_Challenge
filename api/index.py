import sys
import os

# Add Backend folder to sys.path for Vercel Serverless Functions
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.main import app
except Exception as e:
    import traceback
    err_str = traceback.format_exc()
    print(f"CRITICAL INIT ERROR: {err_str}", flush=True)
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"])
    def debug_error_fallback(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Backend initialization failed",
                "detail": str(e),
                "traceback": err_str.splitlines()
            }
        )


