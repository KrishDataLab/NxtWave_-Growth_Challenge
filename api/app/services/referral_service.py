import secrets
import string
from sqlalchemy.orm import Session
from app.db.models import RegistrationModel

def generate_unique_referral_code(db: Session) -> str:
    """
    Generates a unique, short, URL-safe referral code in the format: AI60-XXXX
    """
    chars = string.ascii_uppercase + string.digits
    for _ in range(100):  # Retry loop to guarantee uniqueness
        suffix = "".join(secrets.choice(chars) for _ in range(4))
        code = f"AI60-{suffix}"
        existing = db.query(RegistrationModel).filter(
            RegistrationModel.referral_code == code
        ).first()
        if not existing:
            return code
    # Fallback to 6 characters if 4 char space gets congested
    suffix = "".join(secrets.choice(chars) for _ in range(6))
    return f"AI60-{suffix}"

def get_referral_stats(db: Session, referral_code: str) -> dict:
    """
    Queries total referred registrations for a given referral code without exposing personal details.
    """
    code_clean = referral_code.strip().upper()
    
    # Check if referral code exists as owner's code or as a referred_by code
    registration = db.query(RegistrationModel).filter(
        RegistrationModel.referral_code == code_clean
    ).first()

    if not registration:
        # Check if there are any registrations referred by this code even if owner model isn't found
        count = db.query(RegistrationModel).filter(
            RegistrationModel.referred_by == code_clean
        ).count()
        if count == 0:
            return None

    total_referred = db.query(RegistrationModel).filter(
        RegistrationModel.referred_by == code_clean
    ).count()

    return {
        "referral_code": code_clean,
        "total_referred_registrations": total_referred
    }
