from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from app.db.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class RegistrationModel(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(50), nullable=False)
    college_name = Column(String(255), nullable=False)
    branch = Column(String(255), nullable=False)
    graduation_year = Column(Integer, nullable=False)
    source = Column(String(100), nullable=True)
    medium = Column(String(100), nullable=True)
    campaign = Column(String(100), nullable=True)
    content = Column(String(100), nullable=True)
    referral_code = Column(String(50), nullable=False, unique=True, index=True)
    referred_by = Column(String(50), nullable=True, index=True)
    email_verified = Column(Boolean, default=False)
    whatsapp_opt_in = Column(Boolean, default=False)
    verification_id = Column(String(64), nullable=True)
    verification_method = Column(String(50), default="otp")
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

class RegistrationVerificationModel(Base):
    __tablename__ = "registration_verifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    verification_id = Column(String(64), nullable=False, unique=True, index=True)
    magic_token = Column(String(64), nullable=True, unique=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    college_name = Column(String(255), nullable=False)
    branch = Column(String(255), nullable=False)
    graduation_year = Column(Integer, nullable=False)
    source = Column(String(100), nullable=True)
    medium = Column(String(100), nullable=True)
    campaign = Column(String(100), nullable=True)
    content = Column(String(100), nullable=True)
    referral_code = Column(String(50), nullable=True)
    whatsapp_opt_in = Column(Boolean, default=False)
    otp_hash = Column(String(255), nullable=False)
    otp_expires_at = Column(DateTime(timezone=True), nullable=False)
    otp_attempts = Column(Integer, default=0)
    verification_status = Column(String(50), default="pending")
    verification_method = Column(String(50), default="otp")
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

class AnalyticsEventModel(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_name = Column(String(100), nullable=False, index=True)
    session_id = Column(String(255), nullable=True)
    anonymous_id = Column(String(255), nullable=True)
    source = Column(String(100), nullable=True)
    medium = Column(String(100), nullable=True)
    campaign = Column(String(100), nullable=True)
    content = Column(String(100), nullable=True)
    referral_code = Column(String(50), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

