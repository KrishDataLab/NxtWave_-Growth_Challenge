import sys
import os

# Add Backend directory to sys.path so Vercel Serverless Function can locate app module
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

# Export FastAPI app instance for Vercel
app = app
