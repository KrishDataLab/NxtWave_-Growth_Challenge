import sys
import os

# Add Backend directory to sys.path so app module imports resolve seamlessly
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

# Export FastAPI app instance for Vercel Serverless Python Function
app = app
