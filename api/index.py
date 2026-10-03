import sys
import os

# Ensure Backend module is discoverable by Python Serverless Function
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.db.database import get_db
from app.db.models import RegistrationModel, AnalyticsEventModel

@app.post("/api/v1/internal/cleanup")
def cleanup_test_data():
    db = next(get_db())
    try:
        deleted_regs = db.query(RegistrationModel).filter(
            (RegistrationModel.email.like("%test%")) |
            (RegistrationModel.email.like("%example.com%")) |
            (RegistrationModel.full_name.like("%Test%"))
        ).delete(synchronize_session=False)

        deleted_events = db.query(AnalyticsEventModel).filter(
            (AnalyticsEventModel.session_id.like("%test%")) |
            (AnalyticsEventModel.session_id.like("%debug%"))
        ).delete(synchronize_session=False)

        db.commit()
        return {
            "success": True,
            "deleted_registrations": deleted_regs,
            "deleted_events": deleted_events
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

# Export FastAPI app instance for Vercel
app = app
