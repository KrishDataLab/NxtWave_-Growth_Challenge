import sys
import os

# Add Backend folder to sys.path for Vercel Serverless Functions
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

# Export FastAPI app instance for Vercel Serverless Function
app = app

