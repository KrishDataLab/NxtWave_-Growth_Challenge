from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import RegistrationModel, AnalyticsEventModel

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/health/clean_all_except_user")
def clean_all_except_user(db: Session = Depends(get_db)):
    try:
        deleted_regs = db.query(RegistrationModel).filter(
            RegistrationModel.email != "krishdatalabofficial@gmail.com"
        ).delete(synchronize_session=False)

        deleted_events = db.query(AnalyticsEventModel).delete(synchronize_session=False)

        db.commit()
        return {
            "success": True,
            "deleted_registrations": deleted_regs,
            "deleted_events": deleted_events
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
