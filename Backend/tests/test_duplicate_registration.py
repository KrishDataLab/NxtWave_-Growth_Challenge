import pytest
from datetime import datetime, timezone, timedelta
from app.db.models import RegistrationModel, RegistrationVerificationModel, AnalyticsEventModel
from app.services.otp_service import normalize_email, hash_otp, create_pending_verification
from app.schemas.registration import RegistrationStartCreate
from app.core.rate_limiter import registration_rate_limiter
from sqlalchemy.exc import IntegrityError

def test_normalization_helper():
    assert normalize_email("  Krish@Gmail.com  ") == "krish@gmail.com"
    assert normalize_email("KRISH@GMAIL.COM") == "krish@gmail.com"
    assert normalize_email(" test.user@nxtwave.tech ") == "test.user@nxtwave.tech"

def find_otp_for_verification(verif_rec):
    for candidate in range(100000, 1000000):
        if hash_otp(str(candidate)) == verif_rec.otp_hash:
            return str(candidate)
    return None

def test_case_a_first_registration_success(client, db_session):
    """Test A: First registration -> created -> OTP verified -> success."""
    payload = {
        "full_name": "Test User A",
        "email": "userA@example.com",
        "phone": "9876543210",
        "college_name": "IIT Hyderabad",
        "branch": "CSE",
        "graduation_year": 2026
    }
    # 1. Start registration
    res1 = client.post("/api/v1/registrations/start", json=payload)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["success"] is True
    assert data1["already_registered"] is False
    verif_id = data1["verification_id"]

    # 2. Find matching OTP from DB
    verif = db_session.query(RegistrationVerificationModel).filter_by(verification_id=verif_id).first()
    assert verif is not None
    otp = find_otp_for_verification(verif)
    assert otp is not None

    # 3. Verify OTP (returns 201 Created)
    res2 = client.post("/api/v1/registrations/verify", json={"verification_id": verif_id, "otp": otp})
    assert res2.status_code == 201
    data2 = res2.json()
    assert data2["success"] is True
    assert data2["email_verified"] is True
    assert data2["referral_code"].startswith("AI60-")

    # Check DB
    reg_count = db_session.query(RegistrationModel).filter_by(email="usera@example.com").count()
    assert reg_count == 1

def test_case_b_same_email_duplicate_response(client, db_session):
    """Test B: Same email second attempt returns duplicate response & no second row."""
    payload = {
        "full_name": "Test User B",
        "email": "userB@example.com",
        "phone": "9876543210",
        "college_name": "IIT Madras",
        "branch": "ECE",
        "graduation_year": 2026
    }
    # Create first verified registration directly
    reg = RegistrationModel(
        email="userb@example.com",
        full_name="Test User B",
        phone="9876543210",
        college_name="IIT Madras",
        branch="ECE",
        graduation_year=2026,
        referral_code="AI60-TESTB",
        email_verified=True
    )
    db_session.add(reg)
    db_session.commit()

    # Try starting registration again with same email
    res = client.post("/api/v1/registrations/start", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["already_registered"] is True
    assert data["referral_code"] == "AI60-TESTB"

    # Verify no second row was created
    count = db_session.query(RegistrationModel).filter_by(email="userb@example.com").count()
    assert count == 1

def test_case_c_d_case_and_whitespace_duplicate(client, db_session):
    """Test C & D: Case-insensitive and whitespace email duplicates are treated identically."""
    reg = RegistrationModel(
        email="testuser@gmail.com",
        full_name="Case User",
        phone="9876543210",
        college_name="BITS",
        branch="EEE",
        graduation_year=2027,
        referral_code="AI60-CASE1",
        email_verified=True
    )
    db_session.add(reg)
    db_session.commit()

    test_emails = [
        "TestUser@Gmail.com",
        " TESTUSER@GMAIL.COM ",
        "  testuser@gmail.com  "
    ]

    for em in test_emails:
        payload = {
            "full_name": "Duplicate User",
            "email": em,
            "phone": "9876543210",
            "college_name": "BITS",
            "branch": "EEE",
            "graduation_year": 2027
        }
        res = client.post("/api/v1/registrations/start", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["already_registered"] is True
        assert data["referral_code"] == "AI60-CASE1"

    assert db_session.query(RegistrationModel).filter_by(email="testuser@gmail.com").count() == 1

def test_case_e_pending_registration_reuse(client, db_session):
    """Test E: Pending registration request again reuses pending verification and does not create a second row."""
    payload = {
        "full_name": "Pending User",
        "email": "pending@example.com",
        "phone": "9876543210",
        "college_name": "NIT",
        "branch": "Mech",
        "graduation_year": 2026
    }
    # First start
    res1 = client.post("/api/v1/registrations/start", json=payload)
    assert res1.status_code == 200
    v_id1 = res1.json()["verification_id"]

    # Clear rate limiter and age created_at past 30s cooldown
    registration_rate_limiter.requests.clear()
    verif = db_session.query(RegistrationVerificationModel).filter_by(verification_id=v_id1).first()
    verif.created_at = datetime.now(timezone.utc) - timedelta(seconds=35)
    db_session.commit()

    # Second start with same email before verifying
    res2 = client.post("/api/v1/registrations/start", json=payload)
    assert res2.status_code == 200
    v_id2 = res2.json()["verification_id"]
    assert v_id1 == v_id2

    verifs = db_session.query(RegistrationVerificationModel).filter_by(email="pending@example.com").all()
    assert len(verifs) == 1

def test_case_f_repeated_verification_idempotent(client, db_session):
    """Test F: Repeated verification returns existing registration & referral code."""
    payload = {
        "full_name": "Repeat User",
        "email": "repeat@example.com",
        "phone": "9876543210",
        "college_name": "IIIT",
        "branch": "IT",
        "graduation_year": 2026
    }
    res1 = client.post("/api/v1/registrations/start", json=payload)
    v_id = res1.json()["verification_id"]

    verif = db_session.query(RegistrationVerificationModel).filter_by(verification_id=v_id).first()
    otp = find_otp_for_verification(verif)

    # First verification
    v_res1 = client.post("/api/v1/registrations/verify", json={"verification_id": v_id, "otp": otp})
    assert v_res1.status_code == 201
    code1 = v_res1.json()["referral_code"]

    # Second verification on same v_id
    v_res2 = client.post("/api/v1/registrations/verify", json={"verification_id": v_id, "otp": otp})
    assert v_res2.status_code == 201
    code2 = v_res2.json()["referral_code"]

    assert code1 == code2
    assert db_session.query(RegistrationModel).filter_by(email="repeat@example.com").count() == 1

def test_case_g_concurrent_duplicate_requests(db_session):
    """Test G: Test database uniqueness and race-condition handling for duplicate requests."""
    reg_in = RegistrationStartCreate(
        full_name="Concurrent User",
        email="concurrent@example.com",
        phone="9876543210",
        college_name="JNTU",
        branch="CSE",
        graduation_year=2026
    )

    # First call creates pending verification
    res1 = create_pending_verification(db_session, reg_in)
    assert res1.already_registered is False

    # Simulate registration becoming verified in DB
    existing_reg = RegistrationModel(
        email="concurrent@example.com",
        full_name="Concurrent User",
        phone="9876543210",
        college_name="JNTU",
        branch="CSE",
        graduation_year=2026,
        referral_code="AI60-CONC1",
        email_verified=True
    )
    db_session.add(existing_reg)
    db_session.commit()

    # Call create_pending_verification again for same normalized email
    res2 = create_pending_verification(db_session, reg_in)
    assert res2.already_registered is True
    assert res2.referral_code == "AI60-CONC1"

    regs = db_session.query(RegistrationModel).filter_by(email="concurrent@example.com").all()
    assert len(regs) == 1

def test_case_h_referral_uniqueness(db_session):
    """Test H: Unique constraint on referral_code prevents duplicates."""
    reg1 = RegistrationModel(
        email="ref1@example.com",
        full_name="User 1",
        phone="9876543210",
        college_name="C1",
        branch="B1",
        graduation_year=2026,
        referral_code="AI60-UNIQUE",
        email_verified=True
    )
    db_session.add(reg1)
    db_session.commit()

    reg2 = RegistrationModel(
        email="ref2@example.com",
        full_name="User 2",
        phone="9876543210",
        college_name="C2",
        branch="B2",
        graduation_year=2026,
        referral_code="AI60-UNIQUE",
        email_verified=True
    )
    db_session.add(reg2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_case_i_analytics_tracking(client, db_session):
    """Test I: registration_completed occurs exactly once per verified registration; duplicate attempts tracked separately."""
    payload = {
        "full_name": "Analytics User",
        "email": "analytics@example.com",
        "phone": "9876543210",
        "college_name": "IIT Bombay",
        "branch": "CSE",
        "graduation_year": 2026
    }
    # 1. Start
    res1 = client.post("/api/v1/registrations/start", json=payload)
    v_id = res1.json()["verification_id"]

    # 2. Verify OTP
    verif = db_session.query(RegistrationVerificationModel).filter_by(verification_id=v_id).first()
    otp = find_otp_for_verification(verif)

    client.post("/api/v1/registrations/verify", json={"verification_id": v_id, "otp": otp})

    # 3. Duplicate start attempt after verify
    client.post("/api/v1/registrations/start", json=payload)

    # Verify event counts
    completed_events = db_session.query(AnalyticsEventModel).filter_by(event_name="registration_completed").all()
    dup_events = db_session.query(AnalyticsEventModel).filter_by(event_name="duplicate_registration_attempt").all()

    assert len(completed_events) == 1
    assert len(dup_events) >= 1
