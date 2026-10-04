from typing import Any, Dict, List
from pydantic import BaseModel

class MetricsSummaryResponse(BaseModel):
    total_registrations: int
    registrations_today: int
    registrations_by_source: Dict[str, int]
    registrations_by_medium: Dict[str, int]
    registrations_by_campaign: Dict[str, int]
    registrations_by_college: Dict[str, int]
    registrations_by_branch: Dict[str, int]
    total_referral_registrations: int
    top_referral_codes: List[Dict[str, Any]]
    cta_events: int
    registration_started: int
    registration_completed: int
    whatsapp_share_events: int
    registration_conversion_rate: float
    referral_share_rate: float
    referral_registration_rate: float
