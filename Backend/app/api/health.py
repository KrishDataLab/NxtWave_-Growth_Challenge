from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import RegistrationModel, AnalyticsEventModel

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/health/cleanup")
def cleanup_test_data(db: Session = Depends(get_db)):
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
