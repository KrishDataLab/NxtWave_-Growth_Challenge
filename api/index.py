import sys
import os
import traceback

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

status_log = []

try:
    status_log.append("1. importing fastapi")
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    status_log.append("2. importing config")
    from app.core.config import settings
    status_log.append("3. importing database")
    from app.db.database import engine, Base
    status_log.append("4. importing main")
    from app.main import app as main_app
    app = main_app
except Exception as err:
    err_tb = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    diagnostic_app = FastAPI()
    @diagnostic_app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
    def diag(full_path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "status_log": status_log,
                "error": str(err),
                "traceback": err_tb
            }
        )
    app = diagnostic_app
