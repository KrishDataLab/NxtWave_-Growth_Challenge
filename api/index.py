import sys
import os
import traceback

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_dir in sys.path:
    sys.path.remove(backend_dir)
sys.path.insert(0, backend_dir)

try:
    from app.main import app as _app
    app = _app
except Exception as init_err:
    tb_str = traceback.format_exc()
    print(f"[VERCEL INIT ERROR]: {tb_str}")
    
    # Create emergency FastAPI fallback app to expose the exact traceback
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="Vercel Emergency Diagnostic")
    
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    def diagnostic_fallback(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Backend Initialization Failed",
                "exception": str(init_err),
                "traceback": tb_str
            }
        )
