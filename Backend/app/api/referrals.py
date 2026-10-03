from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.referral import ReferralResponse
from app.services.referral_service import get_referral_stats

router = APIRouter(prefix="/referrals", tags=["Referrals"])

@router.get("/{referral_code}", response_model=ReferralResponse)
def get_referral_details(
    referral_code: str,
    db: Session = Depends(get_db)
):
    stats = get_referral_stats(db, referral_code)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral code not found"
        )
    return stats
