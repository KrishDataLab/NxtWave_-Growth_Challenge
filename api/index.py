import sys
import os

api_dir = os.path.dirname(__file__)
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

from app.main import app
from fastapi import Request, Response
from fastapi.responses import JSONResponse

@app.api_route("/api/debug", methods=["GET", "POST"])
@app.api_route("/v1/debug", methods=["GET", "POST"])
@app.api_route("/debug", methods=["GET", "POST"])
def debug_route(request: Request):
    return {
        "url_path": str(request.url.path),
        "scope_path": request.scope.get("path"),
        "routes": [getattr(r, "path", str(r)) for r in app.routes]
    }
