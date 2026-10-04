from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import RegistrationModel, AnalyticsEventModel
from app.schemas.registration import RegistrationCreate, RegistrationResponse
from app.services.referral_service import generate_unique_referral_code

def create_registration(db: Session, reg_in: RegistrationCreate) -> RegistrationResponse:
    # Direct unverified registration bypass is strictly disabled.
    # Students must go through /registrations/start and /registrations/verify to complete OTP.
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Direct unverified registration is disabled. Please use /api/v1/registrations/start and /api/v1/registrations/verify to complete email OTP verification."
    )
