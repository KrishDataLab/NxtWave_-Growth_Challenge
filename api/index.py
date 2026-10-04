import sys
import os

# Add all potential Backend module paths for Vercel serverless execution
current_dir = os.path.dirname(__file__)
cwd = os.getcwd()

candidate_paths = [
    os.path.abspath(os.path.join(current_dir, "..", "Backend")),
    os.path.abspath(os.path.join(current_dir, "Backend")),
    os.path.abspath(os.path.join(cwd, "Backend")),
    os.path.abspath(cwd),
]

for p in candidate_paths:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

from app.main import app

app = app
