from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.registration import (
    RegistrationCreate,
    RegistrationStartCreate,
    RegistrationStartResponse,
    OTPVerifyRequest,
    RegistrationResponse
)
from app.services.registration_service import create_registration
from app.services.otp_service import create_pending_verification, verify_otp_and_register
from app.core.rate_limiter import registration_rate_limiter

router = APIRouter(prefix="/registrations", tags=["Registrations"])

@router.post("/start", response_model=RegistrationStartResponse, status_code=200)
def start_registration(
    request: Request,
    reg_in: RegistrationStartCreate,
    db: Session = Depends(get_db)
):
    registration_rate_limiter.check_rate_limit(request)
    return create_pending_verification(db, reg_in)

@router.post("/verify", response_model=RegistrationResponse, status_code=201)
def verify_registration(
    request: Request,
    verify_in: OTPVerifyRequest,
    db: Session = Depends(get_db)
):
    registration_rate_limiter.check_rate_limit(request)
    return verify_otp_and_register(db, verify_in.verification_id, verify_in.otp)

@router.post("", response_model=RegistrationResponse, status_code=201)
def register_user(
    request: Request,
    registration_in: RegistrationCreate,
    db: Session = Depends(get_db)
):
    # Apply basic rate limiting protection against repeated request abuse
    registration_rate_limiter.check_rate_limit(request)
    
    return create_registration(db, registration_in)

