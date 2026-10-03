from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.models import RegistrationModel, AnalyticsEventModel
from app.schemas.metrics import MetricsSummaryResponse

def get_growth_metrics_summary(db: Session) -> MetricsSummaryResponse:
    # Total Registrations
    total_registrations = db.query(RegistrationModel).count()

    # Registrations Today (UTC)
    now_utc = datetime.now(timezone.utc)
    today_start = datetime(now_utc.year, now_utc.month, now_utc.day, tzinfo=timezone.utc)
    registrations_today = db.query(RegistrationModel).filter(
        RegistrationModel.created_at >= today_start
    ).count()

    # Breakdown by Source
    source_query = db.query(
        RegistrationModel.source, func.count(RegistrationModel.id)
    ).group_by(RegistrationModel.source).all()
    registrations_by_source = {
        (s or "direct"): count for s, count in source_query
    }

    # Breakdown by Medium
    medium_query = db.query(
        RegistrationModel.medium, func.count(RegistrationModel.id)
    ).group_by(RegistrationModel.medium).all()
    registrations_by_medium = {
        (m or "none"): count for m, count in medium_query
    }

    # Breakdown by Campaign
    campaign_query = db.query(
        RegistrationModel.campaign, func.count(RegistrationModel.id)
    ).group_by(RegistrationModel.campaign).all()
    registrations_by_campaign = {
        (c or "none"): count for c, count in campaign_query
    }

    # Breakdown by College
    college_query = db.query(
        RegistrationModel.college_name, func.count(RegistrationModel.id)
    ).group_by(RegistrationModel.college_name).all()
    registrations_by_college = {
        (col or "unknown"): count for col, count in college_query
    }

    # Breakdown by Branch
    branch_query = db.query(
        RegistrationModel.branch, func.count(RegistrationModel.id)
    ).group_by(RegistrationModel.branch).all()
    registrations_by_branch = {
        (b or "unknown"): count for b, count in branch_query
    }

    # Registrations with referred_by
    total_referral_registrations = db.query(RegistrationModel).filter(
        RegistrationModel.referred_by.isnot(None),
        RegistrationModel.referred_by != ""
    ).count()

    # Top Referral Codes by count of referred registrations
    top_referrals_query = db.query(
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
    cta_events = db.query(AnalyticsEventModel).filter(
        AnalyticsEventModel.event_name == "hero_cta_click"
    ).count()

    registration_started = db.query(AnalyticsEventModel).filter(
        AnalyticsEventModel.event_name == "registration_started"
    ).count()

    registration_completed = db.query(AnalyticsEventModel).filter(
        AnalyticsEventModel.event_name == "registration_completed"
    ).count()

    whatsapp_share_events = db.query(AnalyticsEventModel).filter(
        AnalyticsEventModel.event_name == "whatsapp_share"
    ).count()

    # Formulas:
    # 1. registration_conversion_rate = registration_completed / registration_started * 100
    if registration_started > 0:
        registration_conversion_rate = round((registration_completed / registration_started) * 100.0, 2)
    else:
        registration_conversion_rate = 0.0

    # 2. referral_share_rate = whatsapp_share / registration_completed * 100
    if registration_completed > 0:
        referral_share_rate = round((whatsapp_share_events / registration_completed) * 100.0, 2)
    else:
        referral_share_rate = 0.0

    # 3. referral_registration_rate = registrations_with_referred_by / total_registrations * 100
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
