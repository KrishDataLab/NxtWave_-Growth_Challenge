import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"])
def diagnostic_handler(path: str = ""):
    diag = {}
    
    try:
        from app.core.config import settings
        diag["config"] = "OK"
        diag["env"] = settings.APP_ENV
    except Exception as e:
        diag["config"] = f"FAIL: {e}"

    try:
        from app.db.database import engine, Base
        diag["database"] = "OK"
        diag["db_url_type"] = str(engine.url.drivername)
    except Exception as e:
        diag["database"] = f"FAIL: {e}"

    try:
        from app.api import api_router
        diag["api_router"] = "OK"
    except Exception as e:
        diag["api_router"] = f"FAIL: {e}"

    try:
        from app.main import app as real_app
        diag["main_import"] = "OK"
    except Exception as e:
        import traceback
        diag["main_import"] = f"FAIL: {e}"
        diag["traceback"] = traceback.format_exc().splitlines()

    return JSONResponse(content={"status": "diagnostic", "path": path, "results": diag})
