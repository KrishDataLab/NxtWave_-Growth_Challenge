import sys
import os

# Ensure Backend module is discoverable by Python Serverless Function
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

# Export FastAPI app instance for Vercel
app = app
