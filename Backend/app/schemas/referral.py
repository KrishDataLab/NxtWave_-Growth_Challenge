from pydantic import BaseModel

class ReferralResponse(BaseModel):
    referral_code: str
    total_referred_registrations: int
