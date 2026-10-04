import hashlib
import logging
import random
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import RegistrationModel, RegistrationVerificationModel, AnalyticsEventModel, utc_now
from app.schemas.registration import RegistrationStartCreate, RegistrationStartResponse, RegistrationResponse
from app.services.referral_service import generate_unique_referral_code
from app.services.whatsapp_service import get_whatsapp_service
from app.services.email_service import get_email_provider, mask_email

logger = logging.getLogger("nxtwave_growth_backend")

OTP_SECRET_SALT = "nxtwave_ai60_otp_salt_2026"
OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 5

def normalize_email(email: str) -> str:
    """Consistent email normalization helper: trim whitespace and convert to lowercase."""
    if not email:
        return ""
    return email.strip().lower()

def hash_otp(otp: str) -> str:
    """Computes SHA-256 hash of OTP with salt so plaintext is never stored in DB."""
    return hashlib.sha256(f"{otp}:{OTP_SECRET_SALT}".encode("utf-8")).hexdigest()

def generate_6digit_otp() -> str:
    """Generates a secure 6-digit numeric OTP string."""
    return f"{random.randint(100000, 999999)}"

def create_pending_verification(db: Session, reg_in: RegistrationStartCreate) -> RegistrationStartResponse:
    normalized_email = normalize_email(reg_in.email)
    email_hash = hashlib.sha256(normalized_email.encode("utf-8")).hexdigest()

    # 1. DUPLICATE VERIFIED REGISTRATION CHECK
    existing = db.query(RegistrationModel).filter(
        RegistrationModel.email == normalized_email
    ).first()

    if existing:
        # Record analytics: duplicate_registration_attempt (DO NOT record registration_completed)
        db.add(AnalyticsEventModel(
            event_name="duplicate_registration_attempt",
            source=reg_in.source,
            medium=reg_in.medium,
            campaign=reg_in.campaign,
            content=reg_in.content,
            referral_code=existing.referral_code,
            metadata_json={
                "email_hash": email_hash,
                "registration_id": str(existing.id)
            }
        ))
        db.commit()

        return RegistrationStartResponse(
            success=True,
            already_registered=True,
            verification_id="",
            referral_code=existing.referral_code,
            message="You're already registered! Your seat is already booked."
        )

    now = utc_now()

    # 2. PENDING REGISTRATION REUSE
    recent_pending = db.query(RegistrationVerificationModel).filter(
        RegistrationVerificationModel.email == normalized_email,
        RegistrationVerificationModel.verification_status == "pending"
    ).order_by(RegistrationVerificationModel.created_at.desc()).first()

    if recent_pending and recent_pending.created_at:
        created_at = recent_pending.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if (now - created_at).total_seconds() < 30:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Verification code was recently sent. Please wait 30 seconds before requesting a new code."
            )

    raw_otp = generate_6digit_otp()
    otp_hash = hash_otp(raw_otp)
    expires_at = now + timedelta(minutes=OTP_EXPIRY_MINUTES)
    referred_by_code = reg_in.referral_code.strip().upper() if reg_in.referral_code else None

    if recent_pending:
        # Reuse existing pending verification record
        verification_record = recent_pending
        verification_record.full_name = reg_in.full_name
        verification_record.phone = reg_in.phone
        verification_record.college_name = reg_in.college_name
        verification_record.branch = reg_in.branch
        verification_record.graduation_year = reg_in.graduation_year
        verification_record.source = reg_in.source
        verification_record.medium = reg_in.medium
        verification_record.campaign = reg_in.campaign
        verification_record.content = reg_in.content
        verification_record.referral_code = referred_by_code
        verification_record.whatsapp_opt_in = reg_in.whatsapp_opt_in
        verification_record.otp_hash = otp_hash
        verification_record.otp_expires_at = expires_at
        verification_record.otp_attempts = 0
        verification_id = verification_record.verification_id
    else:
        # Create new pending verification record
        verification_id = str(uuid.uuid4())
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

    # Record analytics: otp_sent
    db.add(AnalyticsEventModel(
        event_name="otp_sent",
        source=reg_in.source,
        medium=reg_in.medium,
        campaign=reg_in.campaign,
        content=reg_in.content,
        referral_code=referred_by_code,
        metadata_json={
            "verification_id": verification_id,
            "email_hash": email_hash
        }
    ))
    db.commit()

    # Trigger Email Provider
    email_provider = get_email_provider()
    email_result = email_provider.send_otp_email(normalized_email, raw_otp)

    logger.info(
        f"[OTP Service] OTP email dispatch result for '{mask_email(normalized_email)}': {email_result.detail}"
    )

    return RegistrationStartResponse(
        success=True,
        already_registered=False,
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

    normalized_email = normalize_email(verification_record.email)

    # 1. REPEATED / IDEMPOTENT VERIFICATION CHECK
    existing_reg = db.query(RegistrationModel).filter(
        RegistrationModel.email == normalized_email
    ).first()

    if existing_reg:
        if verification_record.verification_status == "pending":
            verification_record.verification_status = "verified"
            verification_record.verified_at = utc_now()
            db.commit()

        return RegistrationResponse(
            success=True,
            already_registered=True,
            registration_id=str(existing_reg.id),
            referral_code=existing_reg.referral_code,
            email_verified=True,
            whatsapp_opt_in=existing_reg.whatsapp_opt_in,
            whatsapp_status="already_registered",
            message="You're already registered! Your seat is already booked."
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

    new_referral_code = generate_unique_referral_code(db)

    new_reg = RegistrationModel(
        full_name=verification_record.full_name,
        email=normalized_email,
        phone=verification_record.phone,
        college_name=verification_record.college_name,
        branch=verification_record.branch,
        graduation_year=verification_record.graduation_year,
        source=verification_record.source,
        medium=verification_record.medium,
        campaign=verification_record.campaign,
        content=verification_record.content,
        referral_code=new_referral_code,
        referred_by=verification_record.referral_code,
        email_verified=True,
        whatsapp_opt_in=verification_record.whatsapp_opt_in,
        verification_id=verification_id,
        verified_at=now
    )

    try:
        db.add(new_reg)
        db.commit()
        db.refresh(new_reg)
    except IntegrityError:
        db.rollback()
        concurrent_reg = db.query(RegistrationModel).filter(
            RegistrationModel.email == normalized_email
        ).first()
        if concurrent_reg:
            return RegistrationResponse(
                success=True,
                already_registered=True,
                registration_id=str(concurrent_reg.id),
                referral_code=concurrent_reg.referral_code,
                email_verified=True,
                whatsapp_opt_in=concurrent_reg.whatsapp_opt_in,
                whatsapp_status="already_registered",
                message="You're already registered! Your seat is already booked."
            )
        raise

    # Dispatch confirmation email to user upon genuinely new verified registration
    try:
        email_provider = get_email_provider()
        email_provider.send_confirmation_email(new_reg.email, new_referral_code)
    except Exception as email_err:
        logger.error(f"[OTP Service] Failed to send confirmation email to '{mask_email(new_reg.email)}': {email_err}")

    email_hash = hashlib.sha256(normalized_email.encode("utf-8")).hexdigest()

    # Record analytics: otp_verified
    db.add(AnalyticsEventModel(
        event_name="otp_verified",
        source=verification_record.source,
        medium=verification_record.medium,
        campaign=verification_record.campaign,
        content=verification_record.content,
        referral_code=verification_record.referral_code,
        metadata_json={
            "verification_id": verification_id,
            "email_hash": email_hash
        }
    ))

    # Record analytics: registration_completed (EXACTLY ONCE PER NEW REGISTRATION!)
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
            "email_verified": True,
            "email_hash": email_hash
        }
    ))
    db.commit()

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
        already_registered=False,
        registration_id=str(new_reg.id),
        referral_code=new_referral_code,
        email_verified=True,
        whatsapp_opt_in=verification_record.whatsapp_opt_in,
        whatsapp_status=whatsapp_status,
        message="Registration verified successfully"
    )
