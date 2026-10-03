from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.analytics import AnalyticsEventCreate, AnalyticsEventResponse
from app.services.analytics_service import record_analytics_event

router = APIRouter(tags=["Analytics Events"])

@router.post("/events", response_model=AnalyticsEventResponse, status_code=201)
def track_event(
    event_in: AnalyticsEventCreate,
    db: Session = Depends(get_db)
):
    return record_analytics_event(db, event_in)
