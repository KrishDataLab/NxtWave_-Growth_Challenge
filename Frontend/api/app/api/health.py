from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from app.core.config import settings
from app.db.database import get_db
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

@router.get("/health/db_schema")
def db_schema_check(db: Session = Depends(get_db)):
    bind_engine = db.get_bind()
    dialect_name = bind_engine.dialect.name

    inspector = inspect(bind_engine)
    indexes = inspector.get_indexes("registrations")

    email_idx = [idx for idx in indexes if idx.get("unique") and "email" in idx.get("column_names", [])]
    ref_idx = [idx for idx in indexes if idx.get("unique") and "referral_code" in idx.get("column_names", [])]

    # Safe data violation checks
    dup_email_count = 0
    dup_ref_count = 0
    try:
        dup_email_count = db.execute(text("SELECT COUNT(*) FROM (SELECT email FROM registrations GROUP BY email HAVING COUNT(*) > 1) t")).scalar() or 0
        dup_ref_count = db.execute(text("SELECT COUNT(*) FROM (SELECT referral_code FROM registrations GROUP BY referral_code HAVING COUNT(*) > 1) t")).scalar() or 0
    except Exception:
        pass

    return {
        "dialect": dialect_name,
        "registrations_table_exists": "registrations" in inspector.get_table_names(),
        "email_unique_constraint_active": len(email_idx) > 0,
        "email_index_names": [idx["name"] for idx in email_idx],
        "referral_code_unique_constraint_active": len(ref_idx) > 0,
        "referral_code_index_names": [idx["name"] for idx in ref_idx],
        "duplicate_emails_in_db": dup_email_count,
        "duplicate_referral_codes_in_db": dup_ref_count,
        "all_indexes": [{"name": idx["name"], "unique": idx["unique"], "columns": idx["column_names"]} for idx in indexes]
    }
