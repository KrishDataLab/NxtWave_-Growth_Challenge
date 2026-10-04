import hashlib
import logging
import random
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import RegistrationModel, RegistrationVerificationModel, AnalyticsEventModel, utc_now
from app.schemas.registration import RegistrationStartCreate, RegistrationStartResponse, RegistrationResponse
from app.services.referral_service import generate_unique_referral_code
from app.services.whatsapp_service import get_whatsapp_service
from app.services.email_service import get_email_provider

logger = logging.getLogger("nxtwave_growth_backend")

OTP_SECRET_SALT = "nxtwave_ai60_otp_salt_2026"
OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 5

def hash_otp(otp: str) -> str:
    """Computes SHA-256 hash of OTP with salt so plaintext is never stored in DB."""
    return hashlib.sha256(f"{otp}:{OTP_SECRET_SALT}".encode("utf-8")).hexdigest()

def generate_6digit_otp() -> str:
    """Generates a secure 6-digit numeric OTP string."""
    return f"{random.randint(100000, 999999)}"

def create_pending_verification(db: Session, reg_in: RegistrationStartCreate) -> RegistrationStartResponse:
    normalized_email = reg_in.email.strip().lower()

    # Prevent duplicate registration if email is already confirmed in registrations table
    existing = db.query(RegistrationModel).filter(
        RegistrationModel.email == normalized_email
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    # Check for recent active pending verification to rate-limit aggressive resends (within 30 seconds)
    recent_pending = db.query(RegistrationVerificationModel).filter(
        RegistrationVerificationModel.email == normalized_email,
        RegistrationVerificationModel.verification_status == "pending"
    ).order_by(RegistrationVerificationModel.created_at.desc()).first()

    now = utc_now()
    if recent_pending and recent_pending.created_at:
        created_at = recent_pending.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if (now - created_at).total_seconds() < 30:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Verification code was recently sent. Please wait 30 seconds before requesting a new code."
            )

    # Generate 6-digit OTP and hash it immediately
    raw_otp = generate_6digit_otp()
    otp_hash = hash_otp(raw_otp)
    verification_id = str(uuid.uuid4())
    expires_at = now + timedelta(minutes=OTP_EXPIRY_MINUTES)

    referred_by_code = reg_in.referral_code.strip().upper() if reg_in.referral_code else None

    # Save pending verification record
    verification_record = RegistrationVerificationModel(
        verification_id=verification_id,
        full_name=reg_in.full_name,
        email=normalized_email,
        phone=reg_in.phone,
        college_name=reg_in.college_name,
        branch=reg_in.branch,
        graduation_year=reg_in.graduation_year,
        source=reg_in.source,
        medium=reg_in.medium,
        campaign=reg_in.campaign,
        content=reg_in.content,
        referral_code=referred_by_code,
        whatsapp_opt_in=reg_in.whatsapp_opt_in,
        otp_hash=otp_hash,
        otp_expires_at=expires_at,
        otp_attempts=0,
        verification_status="pending"
    )

    db.add(verification_record)

    # Record analytics event: otp_sent
    otp_sent_event = AnalyticsEventModel(
        event_name="otp_sent",
        source=reg_in.source,
        medium=reg_in.medium,
        campaign=reg_in.campaign,
        content=reg_in.content,
        referral_code=referred_by_code,
        metadata_json={
            "verification_id": verification_id,
            "email": normalized_email
        }
    )
    db.add(otp_sent_event)

    db.commit()

    # Trigger configured Email Delivery Provider (Console / SMTP)
    email_provider = get_email_provider()
    email_result = email_provider.send_otp_email(normalized_email, raw_otp)

    logger.info(
        f"[OTP Service] OTP email dispatch result for '{normalized_email}': {email_result.detail}"
    )

    return RegistrationStartResponse(
        success=True,
        verification_id=verification_id,
        expires_in_seconds=OTP_EXPIRY_MINUTES * 60,
        message="Verification code sent to email"
    )

def verify_otp_and_register(db: Session, verification_id: str, otp: str) -> RegistrationResponse:
    clean_otp = otp.strip()
    if not clean_otp or not clean_otp.isdigit() or len(clean_otp) != 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code must be a 6-digit number"
        )

    verification_record = db.query(RegistrationVerificationModel).filter(
        RegistrationVerificationModel.verification_id == verification_id
    ).first()

    if not verification_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired verification session"
        )

    if verification_record.verification_status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Verification session is already {verification_record.verification_status}"
        )

    now = utc_now()
    expires_at = verification_record.otp_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        verification_record.verification_status = "expired"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new code."
        )

    if verification_record.otp_attempts >= MAX_OTP_ATTEMPTS:
        verification_record.verification_status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum verification attempts exceeded. Please restart registration."
        )

    # Verify Hash
    input_hash = hash_otp(clean_otp)
    if input_hash != verification_record.otp_hash:
        verification_record.otp_attempts += 1
        remaining_attempts = MAX_OTP_ATTEMPTS - verification_record.otp_attempts
        if remaining_attempts <= 0:
            verification_record.verification_status = "failed"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum verification attempts exceeded. Please restart registration."
            )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incorrect verification code. {remaining_attempts} attempts remaining."
        )

    # SUCCESS: Mark verification as verified
    verification_record.verification_status = "verified"
    verification_record.verified_at = now

    # Prevent duplicate registration race condition
    existing_reg = db.query(RegistrationModel).filter(
        RegistrationModel.email == verification_record.email
    ).first()

    if existing_reg:
        db.commit()
        return RegistrationResponse(
            success=True,
            registration_id=str(existing_reg.id),
            referral_code=existing_reg.referral_code,
            email_verified=True,
            whatsapp_opt_in=existing_reg.whatsapp_opt_in,
            whatsapp_status="already_registered",
            message="Email is already registered"
        )

    # Generate new AI60-XXXX referral code
    new_referral_code = generate_unique_referral_code(db)

    # Create confirmed Registration record
    new_reg = RegistrationModel(
        full_name=verification_record.full_name,
        email=verification_record.email,
        phone=verification_record.phone,
        college_name=verification_record.college_name,
        branch=verification_record.branch,
        graduation_year=verification_record.graduation_year,
        source=verification_record.source,
        medium=verification_record.medium,
        campaign=verification_record.campaign,
        content=verification_record.content,
        referral_code=new_referral_code,
        referred_by=verification_record.referral_code, # Referred by attribution
        email_verified=True,
        whatsapp_opt_in=verification_record.whatsapp_opt_in,
        verification_id=verification_id,
        verified_at=now
    )

    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)

    # Dispatch confirmation email to user upon successful OTP verification
    try:
        email_provider = get_email_provider()
        email_provider.send_confirmation_email(new_reg.email, new_referral_code)
    except Exception as email_err:
        logger.error(f"[OTP Service] Failed to send confirmation email to '{new_reg.email}': {email_err}")

    # Record analytics: otp_verified
    db.add(AnalyticsEventModel(
        event_name="otp_verified",
        source=verification_record.source,
        medium=verification_record.medium,
        campaign=verification_record.campaign,
        content=verification_record.content,
        referral_code=verification_record.referral_code,
        metadata_json={"verification_id": verification_id}
    ))

    # Record analytics: registration_completed (happens EXACTLY ONCE upon successful verification!)
    db.add(AnalyticsEventModel(
        event_name="registration_completed",
        source=verification_record.source,
        medium=verification_record.medium,
        campaign=verification_record.campaign,
        content=verification_record.content,
        referral_code=verification_record.referral_code,
        metadata_json={
            "registration_id": str(new_reg.id),
            "college_name": verification_record.college_name,
            "branch": verification_record.branch,
            "email_verified": True
        }
    ))
    db.commit()

    # Trigger Mock WhatsApp Service if opted-in
    whatsapp_status = "skipped"
    if verification_record.whatsapp_opt_in:
        db.add(AnalyticsEventModel(
            event_name="whatsapp_confirmation_requested",
            source=verification_record.source,
            referral_code=verification_record.referral_code,
            metadata_json={"registration_id": str(new_reg.id)}
        ))
        db.commit()

        wa_service = get_whatsapp_service()
        wa_result = wa_service.send_whatsapp_confirmation(
            phone=new_reg.phone,
            full_name=new_reg.full_name,
            referral_code=new_referral_code
        )

        whatsapp_status = wa_result.status

        db.add(AnalyticsEventModel(
            event_name="whatsapp_confirmation_sent",
            source=verification_record.source,
            referral_code=verification_record.referral_code,
            metadata_json={
                "registration_id": str(new_reg.id),
                "whatsapp_status": wa_result.status,
                "delivered": wa_result.delivered
            }
        ))
        db.commit()

    return RegistrationResponse(
        success=True,
        registration_id=str(new_reg.id),
        referral_code=new_referral_code,
        email_verified=True,
        whatsapp_opt_in=verification_record.whatsapp_opt_in,
        whatsapp_status=whatsapp_status,
        message="Registration verified successfully"
    )
