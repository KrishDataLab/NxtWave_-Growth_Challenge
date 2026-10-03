from sqlalchemy.orm import Session
from app.db.models import AnalyticsEventModel
from app.schemas.analytics import AnalyticsEventCreate, AnalyticsEventResponse

def record_analytics_event(db: Session, event_in: AnalyticsEventCreate) -> AnalyticsEventResponse:
    event_model = AnalyticsEventModel(
        event_name=event_in.event_name,
        session_id=event_in.session_id,
        anonymous_id=event_in.anonymous_id,
        source=event_in.source,
        medium=event_in.medium,
        campaign=event_in.campaign,
        content=event_in.content,
        referral_code=event_in.referral_code.strip().upper() if event_in.referral_code else None,
        metadata_json=event_in.metadata or {}
    )

    db.add(event_model)
    db.commit()
    db.refresh(event_model)

    return AnalyticsEventResponse(
        success=True,
        event_id=str(event_model.id),
        message="Event recorded successfully"
    )
