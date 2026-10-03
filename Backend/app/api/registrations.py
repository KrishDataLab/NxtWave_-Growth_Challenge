from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.registration import RegistrationCreate, RegistrationResponse
from app.services.registration_service import create_registration
from app.core.rate_limiter import registration_rate_limiter

router = APIRouter(prefix="/registrations", tags=["Registrations"])

@router.post("", response_model=RegistrationResponse, status_code=201)
def register_user(
    request: Request,
    registration_in: RegistrationCreate,
    db: Session = Depends(get_db)
):
    # Apply basic rate limiting protection against repeated request abuse
    registration_rate_limiter.check_rate_limit(request)
    
    return create_registration(db, registration_in)
