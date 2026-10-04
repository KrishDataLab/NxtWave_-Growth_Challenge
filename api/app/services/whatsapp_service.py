import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from app.core.config import settings

logger = logging.getLogger("nxtwave_growth_backend")

@dataclass
class WhatsAppSendResult:
    status: str  # "mocked", "sent", "failed", "skipped"
    delivered: bool
    message_id: Optional[str] = None
    message_preview: Optional[str] = None
    detail: Optional[str] = None

class BaseWhatsAppService(ABC):
    @abstractmethod
    def send_whatsapp_confirmation(
        self, phone: str, full_name: str, referral_code: str
    ) -> WhatsAppSendResult:
        """Sends or simulates a WhatsApp confirmation message."""
        pass

class MockWhatsAppService(BaseWhatsAppService):
    def send_whatsapp_confirmation(
        self, phone: str, full_name: str, referral_code: str
    ) -> WhatsAppSendResult:
        # Formatted template message (exact prompt specification, zero invented dates/times)
        template_message = (
            f"Congratulations! Your seat is booked for NxtWave's "
            f"Build Your First AI Project in 60 Minutes workshop.\n\n"
            f"Your referral code is {referral_code}.\n\n"
            f"We'll share workshop updates with you here."
        )

        # Mask phone number for privacy in logs (e.g. +91 ***** 43210 or 98*****210)
        masked_phone = phone
        if len(phone) >= 10:
            masked_phone = f"{phone[:3]}******{phone[-3:]}"

        logger.info(
            f"[WhatsApp Mock Service] Simulated message for {full_name} ({masked_phone}):\n{template_message}"
        )

        return WhatsAppSendResult(
            status="mocked",
            delivered=False,
            message_id=f"mock_wa_{referral_code}",
            message_preview=template_message,
            detail="Mock WhatsApp message delivery simulated successfully for challenge demonstration."
        )

def get_whatsapp_service() -> BaseWhatsAppService:
    # Pluggable service factory (defaulting to MockWhatsAppService for challenge simulation)
    provider = getattr(settings, "WHATSAPP_PROVIDER", "mock").lower()
    if provider == "mock":
        return MockWhatsAppService()
    # Placeholder where MetaWhatsAppService or SMS/WhatsApp gateway can be plugged in
    return MockWhatsAppService()
