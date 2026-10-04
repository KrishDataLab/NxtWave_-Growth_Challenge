import logging
import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings

logger = logging.getLogger("nxtwave_growth_backend")

def mask_email(email: str) -> str:
    if not email or "@" not in email:
        return "***"
    parts = email.split("@", 1)
    name, domain = parts[0], parts[1]
    if len(name) <= 2:
        masked_name = name[0] + "*"
    else:
        masked_name = name[0] + "***" + name[-1]
    return f"{masked_name}@{domain}"

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

    @abstractmethod
    def send_confirmation_email(self, to_email: str, referral_code: str) -> EmailSendResult:
        """Sends seat booking confirmation email to recipient after verification."""
        pass

class ConsoleEmailProvider(BaseEmailProvider):
    """Development / Testing / Demo provider that safely logs outgoing OTP and confirmation emails."""
    def send_otp_email(self, to_email: str, otp: str) -> EmailSendResult:
        subject = "Verify your NxtWave workshop registration"
        body = (
            f"Your NxtWave workshop verification code is: {otp}\n\n"
            f"This code expires in 10 minutes.\n\n"
            f"Do not share this code with anyone."
        )

        logger.info(
            f"[Console Email Provider] Outgoing Email to <{mask_email(to_email)}>:\n"
            f"Subject: {subject}\n"
            f"Body:\n{body}"
        )

        return EmailSendResult(
            success=True,
            provider="console",
            delivered=False,
            detail="OTP logged to console/logs safely (development mode)."
        )

    def send_confirmation_email(self, to_email: str, referral_code: str) -> EmailSendResult:
        subject = "Congratulations! Your seat is booked - NxtWave Workshop"
        share_url = f"https://nxt-wave-growth-challenge.vercel.app/?ref={referral_code}"
        body = (
            "Congratulations! Your seat is booked for NxtWave's "
            "Build Your First AI Project in 60 Minutes workshop.\n\n"
            f"Your referral code is: {referral_code}\n\n"
            f"Share link: {share_url}\n\n"
            "We'll share workshop updates and access links with you here."
        )

        logger.info(
            f"[Console Email Provider] Outgoing Confirmation Email to <{mask_email(to_email)}>:\n"
            f"Subject: {subject}\n"
            f"Body:\n{body}"
        )

        return EmailSendResult(
            success=True,
            provider="console",
            delivered=False,
            detail="Confirmation email logged to console/logs safely (development mode)."
        )

class SMTPEmailProvider(BaseEmailProvider):
    """Production provider using standard SMTP/TLS to deliver real emails."""
    def send_otp_email(self, to_email: str, otp: str) -> EmailSendResult:
        host = settings.SMTP_HOST or "smtp.gmail.com"
        port = settings.SMTP_PORT or 587
        user = settings.SMTP_USER or "kunchalamohank@gmail.com"
        from_email = settings.SMTP_FROM_EMAIL or user
        password = settings.SMTP_PASSWORD or ""
        has_password = bool(password and len(password.strip()) > 0)

        logger.info(
            f"[SMTP Diagnostic] Attempting OTP send:\n"
            f"  Host: {host}:{port}\n"
            f"  User: {mask_email(user)}\n"
            f"  From: {mask_email(from_email)}\n"
            f"  To: {mask_email(to_email)}\n"
            f"  Has Password: {has_password}\n"
            f"  TLS: {settings.SMTP_TLS}"
        )

        if not has_password:
            logger.warning("[SMTP Diagnostic] SMTP_PASSWORD is not set in environment variables! Gmail SMTP requires an App Password.")
            return EmailSendResult(
                success=False,
                provider="smtp",
                delivered=False,
                detail="SMTP_PASSWORD missing in Vercel Environment Variables. Gmail SMTP requires an App Password."
            )

        subject = "Verify your NxtWave workshop registration"
        body = (
            f"Your NxtWave workshop verification code is: {otp}\n\n"
            f"This code expires in 10 minutes.\n\n"
            f"Do not share this code with anyone."
        )

        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(host, port, timeout=12) as server:
                server.ehlo()
                if settings.SMTP_TLS:
                    server.starttls()
                    server.ehlo()
                if user and password:
                    server.login(user, password)
                server.sendmail(from_email, [to_email], msg.as_string())

            logger.info(f"[SMTP Diagnostic] SUCCESS: Real OTP email delivered to <{mask_email(to_email)}> via {host}:{port}")
            return EmailSendResult(
                success=True,
                provider="smtp",
                delivered=True,
                detail=f"Email accepted by {host}:{port} for recipient"
            )
        except smtplib.SMTPAuthenticationError as auth_err:
            clean_err = str(auth_err).replace(password, "***") if password else str(auth_err)
            logger.error(f"[SMTP Diagnostic] AUTH ERROR: {clean_err}")
            return EmailSendResult(
                success=False,
                provider="smtp",
                delivered=False,
                detail=f"SMTP Auth Error (535): {clean_err}"
            )
        except Exception as err:
            clean_err = str(err).replace(password, "***") if password else str(err)
            logger.error(f"[SMTP Diagnostic] ERROR: {clean_err}")
            return EmailSendResult(
                success=False,
                provider="smtp",
                delivered=False,
                detail=f"SMTP Error: {clean_err}"
            )

    def send_confirmation_email(self, to_email: str, referral_code: str) -> EmailSendResult:
        host = settings.SMTP_HOST or "smtp.gmail.com"
        port = settings.SMTP_PORT or 587
        user = settings.SMTP_USER or "kunchalamohank@gmail.com"
        from_email = settings.SMTP_FROM_EMAIL or user
        password = settings.SMTP_PASSWORD or ""
        has_password = bool(password and len(password.strip()) > 0)

        if not has_password:
            logger.warning("[SMTP Diagnostic] SMTP_PASSWORD is not set in environment variables!")
            return EmailSendResult(
                success=False,
                provider="smtp",
                delivered=False,
                detail="SMTP_PASSWORD missing in Vercel Environment Variables."
            )

        subject = "Congratulations! Your seat is booked - NxtWave Workshop"
        share_url = f"https://nxt-wave-growth-challenge.vercel.app/?ref={referral_code}"
        body = (
            "Congratulations! Your seat is booked for NxtWave's "
            "Build Your First AI Project in 60 Minutes workshop.\n\n"
            f"Your referral code is: {referral_code}\n\n"
            f"Share link: {share_url}\n\n"
            "We'll share workshop updates and access links with you here."
        )

        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(host, port, timeout=12) as server:
                server.ehlo()
                if settings.SMTP_TLS:
                    server.starttls()
                    server.ehlo()
                if user and password:
                    server.login(user, password)
                server.sendmail(from_email, [to_email], msg.as_string())

            logger.info(f"[SMTP Diagnostic] SUCCESS: Seat booking confirmation email delivered to <{mask_email(to_email)}> via {host}:{port}")
            return EmailSendResult(
                success=True,
                provider="smtp",
                delivered=True,
                detail=f"Confirmation email accepted by {host}:{port}"
            )
        except Exception as err:
            clean_err = str(err).replace(password, "***") if password else str(err)
            logger.error(f"[SMTP Diagnostic] Confirmation Email ERROR: {clean_err}")
            return EmailSendResult(
                success=False,
                provider="smtp",
                delivered=False,
                detail=f"SMTP Confirmation Email Error: {clean_err}"
            )

def get_email_provider() -> BaseEmailProvider:
    provider_type = getattr(settings, "EMAIL_PROVIDER", "smtp").lower()
    if provider_type == "smtp" or bool(settings.SMTP_HOST):
        return SMTPEmailProvider()
    return ConsoleEmailProvider()
