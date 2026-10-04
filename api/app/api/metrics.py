from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.metrics import MetricsSummaryResponse
from app.services.metrics_service import get_growth_metrics_summary

router = APIRouter(prefix="/metrics", tags=["Growth Metrics"])

@router.get("/summary", response_model=MetricsSummaryResponse)
def get_metrics_summary(db: Session = Depends(get_db)):
    return get_growth_metrics_summary(db)
