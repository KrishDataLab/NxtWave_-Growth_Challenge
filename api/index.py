import sys
import os
import traceback

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.main import app
except BaseException as err:
    err_msg = str(err)
    tb = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()
    
    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
    def catch_all(full_path: str = ""):
        return JSONResponse(
            status_code=500,
            content={"error": err_msg, "traceback": tb}
        )
