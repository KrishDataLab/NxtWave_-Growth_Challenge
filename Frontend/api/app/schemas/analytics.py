from typing import Any, Dict, Optional
from pydantic import BaseModel, field_validator

SUPPORTED_EVENTS = {
    "page_view",
    "hero_cta_click",
    "project_preview_click",
    "registration_started",
    "otp_sent",
    "otp_verified",
    "registration_completed",
    "whatsapp_confirmation_requested",
    "whatsapp_confirmation_sent",
    "whatsapp_confirmation_failed",
    "whatsapp_share",
    "referral_copied",
    "faq_opened"
}

class AnalyticsEventCreate(BaseModel):
    event_name: str
    session_id: Optional[str] = None
    anonymous_id: Optional[str] = None
    source: Optional[str] = None
    medium: Optional[str] = None
    campaign: Optional[str] = None
    content: Optional[str] = None
    referral_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

    @field_validator("event_name")
    @classmethod
    def validate_event_name(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in SUPPORTED_EVENTS:
            raise ValueError(
                f"Unsupported event '{v}'. Must be one of: {', '.join(sorted(SUPPORTED_EVENTS))}"
            )
        return v_clean

class AnalyticsEventResponse(BaseModel):
    success: bool = True
    event_id: str
    message: str = "Event recorded successfully"
