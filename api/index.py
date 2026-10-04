import sys
import os
import traceback

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.main import app
except Exception as e:
    err_msg = str(e)
    err_tb = traceback.format_exc()
    print("CRITICAL VERCEL INIT ERROR:", err_tb, flush=True)
    
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.api_route("/", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
    def catch_all_error(full_path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Backend initialization failed on Vercel",
                "error_details": err_msg,
                "traceback": err_tb
            }
        )
