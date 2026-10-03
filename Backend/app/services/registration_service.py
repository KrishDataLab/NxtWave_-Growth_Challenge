from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import RegistrationModel, AnalyticsEventModel
from app.schemas.registration import RegistrationCreate, RegistrationResponse
from app.services.referral_service import generate_unique_referral_code

def create_registration(db: Session, reg_in: RegistrationCreate) -> RegistrationResponse:
    normalized_email = reg_in.email.strip().lower()

    # Prevent obvious duplicate registrations by email
    existing = db.query(RegistrationModel).filter(
        RegistrationModel.email == normalized_email
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    # Generate new referral code for this user (e.g. AI60-XP44)
    new_referral_code = generate_unique_referral_code(db)

    # Incoming referral code in request payload is stored as referred_by
    referred_by_code = reg_in.referral_code.strip().upper() if reg_in.referral_code else None

    # Create registration model
    new_reg = RegistrationModel(
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
        referral_code=new_referral_code,
        referred_by=referred_by_code
    )

    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)

    # Automatically record registration_completed analytics event
    auto_event = AnalyticsEventModel(
        event_name="registration_completed",
        source=reg_in.source,
        medium=reg_in.medium,
        campaign=reg_in.campaign,
        content=reg_in.content,
        referral_code=referred_by_code,
        metadata_json={
            "registration_id": str(new_reg.id),
            "college_name": reg_in.college_name,
            "branch": reg_in.branch
        }
    )
    db.add(auto_event)
    db.commit()

    return RegistrationResponse(
        success=True,
        registration_id=str(new_reg.id),
        referral_code=new_referral_code,
        message="Registration successful"
    )
