from datetime import datetime, timezone
from sqlalchemy import func, String
from sqlalchemy.orm import Session
from app.db.models import RegistrationModel, AnalyticsEventModel
from app.schemas.metrics import MetricsSummaryResponse

def get_growth_metrics_summary(db: Session, mode: str = "real") -> MetricsSummaryResponse:
    # Filter setup for demo vs real vs combined data
    if mode == "demo":
        reg_base = db.query(RegistrationModel).filter(RegistrationModel.is_demo == True)
        event_base = db.query(AnalyticsEventModel).filter(AnalyticsEventModel.is_demo == True)
    elif mode == "combined":
        reg_base = db.query(RegistrationModel)
        event_base = db.query(AnalyticsEventModel)
    else:  # "real" mode by default
        reg_base = db.query(RegistrationModel).filter(RegistrationModel.is_demo.isnot(True))
        event_base = db.query(AnalyticsEventModel).filter(AnalyticsEventModel.is_demo.isnot(True))

    # Total Registrations
    total_registrations = reg_base.count()

    # Registrations Today (UTC)
    now_utc = datetime.now(timezone.utc)
    today_start = datetime(now_utc.year, now_utc.month, now_utc.day, tzinfo=timezone.utc)
    registrations_today = reg_base.filter(
        RegistrationModel.created_at >= today_start
    ).count()

    # Breakdown by Source
    source_query = reg_base.with_entities(
        RegistrationModel.source, func.count(RegistrationModel.id)
    ).group_by(RegistrationModel.source).all()
    registrations_by_source = {
        (s or "direct"): count for s, count in source_query
    }

    # Breakdown by Medium
    medium_query = reg_base.with_entities(
        RegistrationModel.medium, func.count(RegistrationModel.id)
    ).group_by(RegistrationModel.medium).all()
    registrations_by_medium = {
        (m or "none"): count for m, count in medium_query
    }

    # Breakdown by Campaign
    campaign_query = reg_base.with_entities(
        RegistrationModel.campaign, func.count(RegistrationModel.id)
    ).group_by(RegistrationModel.campaign).all()
    registrations_by_campaign = {
        (c or "none"): count for c, count in campaign_query
    }

    # Breakdown by College
    college_query = reg_base.with_entities(
        RegistrationModel.college_name, func.count(RegistrationModel.id)
    ).group_by(RegistrationModel.college_name).all()
    registrations_by_college = {
        (col or "unknown"): count for col, count in college_query
    }

    # Breakdown by Branch
    branch_query = reg_base.with_entities(
        RegistrationModel.branch, func.count(RegistrationModel.id)
    ).group_by(RegistrationModel.branch).all()
    registrations_by_branch = {
        (b or "unknown"): count for b, count in branch_query
    }

    # Registrations with referred_by
    total_referral_registrations = reg_base.filter(
        RegistrationModel.referred_by.isnot(None),
        RegistrationModel.referred_by != ""
    ).count()

    # Top Referral Codes by count of referred registrations
    top_referrals_query = reg_base.with_entities(
        RegistrationModel.referred_by, func.count(RegistrationModel.id).label("count")
    ).filter(
        RegistrationModel.referred_by.isnot(None),
        RegistrationModel.referred_by != ""
    ).group_by(
        RegistrationModel.referred_by
    ).order_by(
        func.count(RegistrationModel.id).desc()
    ).limit(10).all()

    top_referral_codes = [
        {"referral_code": code, "count": count} for code, count in top_referrals_query
    ]

    # Analytics Events Counters
    cta_events = event_base.filter(
        AnalyticsEventModel.event_name == "hero_cta_click"
    ).count()

    raw_started_unique = event_base.with_entities(
        func.count(func.distinct(func.coalesce(AnalyticsEventModel.session_id, func.cast(AnalyticsEventModel.id, String))))
    ).filter(
        AnalyticsEventModel.event_name == "registration_started"
    ).scalar() or 0

    raw_completed_unique = event_base.with_entities(
        func.count(func.distinct(func.coalesce(AnalyticsEventModel.session_id, func.cast(AnalyticsEventModel.id, String))))
    ).filter(
        AnalyticsEventModel.event_name == "registration_completed"
    ).scalar() or 0

    registration_completed = max(raw_completed_unique, total_registrations)
    registration_started = max(raw_started_unique, registration_completed)

    whatsapp_share_events = event_base.filter(
        AnalyticsEventModel.event_name == "whatsapp_share"
    ).count()

    # Formulas:
    if registration_started > 0:
        registration_conversion_rate = round((registration_completed / registration_started) * 100.0, 2)
    else:
        registration_conversion_rate = 0.0

    if registration_completed > 0:
        referral_share_rate = round((whatsapp_share_events / registration_completed) * 100.0, 2)
    else:
        referral_share_rate = 0.0

    if total_registrations > 0:
        referral_registration_rate = round((total_referral_registrations / total_registrations) * 100.0, 2)
    else:
        referral_registration_rate = 0.0

    return MetricsSummaryResponse(
        total_registrations=total_registrations,
        registrations_today=registrations_today,
        registrations_by_source=registrations_by_source,
        registrations_by_medium=registrations_by_medium,
        registrations_by_campaign=registrations_by_campaign,
        registrations_by_college=registrations_by_college,
        registrations_by_branch=registrations_by_branch,
        total_referral_registrations=total_referral_registrations,
        top_referral_codes=top_referral_codes,
        cta_events=cta_events,
        registration_started=registration_started,
        registration_completed=registration_completed,
        whatsapp_share_events=whatsapp_share_events,
        registration_conversion_rate=registration_conversion_rate,
        referral_share_rate=referral_share_rate,
        referral_registration_rate=referral_registration_rate
    )
