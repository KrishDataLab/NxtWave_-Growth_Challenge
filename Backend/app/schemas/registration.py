from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

class RegistrationCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    college_name: str
    branch: str
    graduation_year: int
    source: Optional[str] = None
    medium: Optional[str] = None
    campaign: Optional[str] = None
    content: Optional[str] = None
    referral_code: Optional[str] = None  # Incoming referrer code (who referred this user)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("full_name", "college_name", "branch", "phone", mode="before")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

class RegistrationStartCreate(RegistrationCreate):
    whatsapp_opt_in: bool = True

class RegistrationStartResponse(BaseModel):
    success: bool = True
    verification_id: str
    expires_in_seconds: int = 600
    message: str = "Verification code sent to email"

class OTPVerifyRequest(BaseModel):
    verification_id: str
    otp: str

    @field_validator("otp", mode="before")
    @classmethod
    def clean_otp(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

class RegistrationResponse(BaseModel):
    success: bool = True
    registration_id: str
    referral_code: str  # The newly generated referral code for this registrant
    email_verified: bool = True
    whatsapp_opt_in: bool = False
    whatsapp_status: Optional[str] = None
    message: str = "Registration successful"

