from fastapi import APIRouter
from app.core.config import settings
from app.services.email_service import get_email_provider, mask_email

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/health/email_status")
def email_status_check():
    provider = get_email_provider()
    has_pwd = bool(settings.SMTP_PASSWORD and len(settings.SMTP_PASSWORD.strip()) > 0)
    return {
        "provider_name": provider.__class__.__name__,
        "configured_provider": settings.EMAIL_PROVIDER,
        "smtp_host": settings.SMTP_HOST,
        "smtp_port": settings.SMTP_PORT,
        "smtp_user_masked": mask_email(settings.SMTP_USER),
        "smtp_from_email_masked": mask_email(settings.SMTP_FROM_EMAIL),
        "has_smtp_password": has_pwd,
        "smtp_tls": settings.SMTP_TLS
    }
