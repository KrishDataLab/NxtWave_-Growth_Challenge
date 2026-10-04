import logging
import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings

logger = logging.getLogger("nxtwave_growth_backend")

@dataclass
class EmailSendResult:
    success: bool
    provider: str
    delivered: bool
    detail: Optional[str] = None

class BaseEmailProvider(ABC):
    @abstractmethod
    def send_otp_email(self, to_email: str, otp: str) -> EmailSendResult:
        """Sends verification code OTP to recipient email address."""
        pass

class ConsoleEmailProvider(BaseEmailProvider):
    """Development / Testing / Demo provider that safely logs outgoing OTP emails."""
    def send_otp_email(self, to_email: str, otp: str) -> EmailSendResult:
        subject = "Verify your NxtWave workshop registration"
        body = (
            f"Your NxtWave workshop verification code is: {otp}\n\n"
            f"This code expires in 10 minutes.\n\n"
            f"Do not share this code with anyone."
        )

        logger.info(
            f"[Console Email Provider] Outgoing Email to <{to_email}>:\n"
            f"Subject: {subject}\n"
            f"Body:\n{body}"
        )

        return EmailSendResult(
            success=True,
            provider="console",
            delivered=False,
            detail="OTP logged to console/logs safely (development mode)."
        )

class SMTPEmailProvider(BaseEmailProvider):
    """Production provider using standard SMTP/TLS to deliver real emails."""
    def send_otp_email(self, to_email: str, otp: str) -> EmailSendResult:
        if not settings.SMTP_HOST:
            logger.warning("[SMTPEmailProvider] SMTP_HOST not configured, falling back to Console log")
            return ConsoleEmailProvider().send_otp_email(to_email, otp)

        subject = "Verify your NxtWave workshop registration"
        body = (
            f"Your NxtWave workshop verification code is: {otp}\n\n"
            f"This code expires in 10 minutes.\n\n"
            f"Do not share this code with anyone."
        )

        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM_EMAIL, [to_email], msg.as_string())

            logger.info(f"[SMTPEmailProvider] Real OTP email successfully delivered to <{to_email}> via SMTP ({settings.SMTP_HOST})")
            return EmailSendResult(
                success=True,
                provider="smtp",
                delivered=True,
                detail=f"Real OTP email sent to {to_email} via SMTP"
            )
        except Exception as err:
            logger.error(f"[SMTPEmailProvider] Failed to send email to <{to_email}>: {err}")
            return EmailSendResult(
                success=False,
                provider="smtp",
                delivered=False,
                detail=f"SMTP Delivery Error: {str(err)}"
            )

def get_email_provider() -> BaseEmailProvider:
    provider_type = getattr(settings, "EMAIL_PROVIDER", "console").lower()
    if provider_type == "smtp" or bool(settings.SMTP_HOST):
        return SMTPEmailProvider()
    return ConsoleEmailProvider()
