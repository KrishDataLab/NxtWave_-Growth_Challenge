from app.services.otp_service import hash_otp
from app.db.models import RegistrationVerificationModel

def test_start_registration_success(client, db_session):
    payload = {
        "full_name": "Rohan Mehta",
        "email": "rohan.mehta@example.com",
        "phone": "9876543210",
        "college_name": "IIT Bombay",
        "branch": "Computer Science",
        "graduation_year": 2026,
        "whatsapp_opt_in": True
    }
    response = client.post("/api/v1/registrations/start", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "verification_id" in data
    assert data["expires_in_seconds"] == 600

def test_verify_otp_success(client, db_session):
    start_payload = {
        "full_name": "Priya Sharma",
        "email": "priya.sharma@example.com",
        "phone": "9988776655",
        "college_name": "NIT Warangal",
        "branch": "Electronics",
        "graduation_year": 2026,
        "whatsapp_opt_in": True
    }
    start_res = client.post("/api/v1/registrations/start", json=start_payload)
    assert start_res.status_code == 200
    v_id = start_res.json()["verification_id"]

    # Fetch pending verification record to extract the hashed OTP hash and simulate user entry
    verification_rec = db_session.query(RegistrationVerificationModel).filter(
        RegistrationVerificationModel.verification_id == v_id
    ).first()
    assert verification_rec is not None

    # Test incorrect OTP
    verify_wrong = client.post("/api/v1/registrations/verify", json={
        "verification_id": v_id,
        "otp": "000000"
    })
    assert verify_wrong.status_code == 400
    assert "incorrect verification code" in verify_wrong.json()["detail"].lower()

    # Find matching 6-digit OTP for testing in loop or directly test with hash
    matching_otp = None
    for candidate in range(100000, 1000000):
        if hash_otp(str(candidate)) == verification_rec.otp_hash:
            matching_otp = str(candidate)
            break
    assert matching_otp is not None

    # Verify with correct OTP
    verify_res = client.post("/api/v1/registrations/verify", json={
        "verification_id": v_id,
        "otp": matching_otp
    })
    assert verify_res.status_code == 201
    data = verify_res.json()
    assert data["success"] is True
    assert data["email_verified"] is True
    assert data["whatsapp_opt_in"] is True
    assert data["whatsapp_status"] == "mocked"
    assert data["referral_code"].startswith("AI60-")

def test_max_otp_attempts_exceeded(client, db_session):
    start_payload = {
        "full_name": "Karan Kapoor",
        "email": "karan.kapoor@example.com",
        "phone": "9123456789",
        "college_name": "BITS Hyderabad",
        "branch": "Mechanical",
        "graduation_year": 2027
    }
    start_res = client.post("/api/v1/registrations/start", json=start_payload)
    v_id = start_res.json()["verification_id"]

    # 5 attempts with invalid OTP
    res_5th = None
    for _ in range(5):
        res_5th = client.post("/api/v1/registrations/verify", json={
            "verification_id": v_id,
            "otp": "999999"
        })

    assert res_5th.status_code == 400
    assert "maximum verification attempts exceeded" in res_5th.json()["detail"].lower()

    # Next attempt fails because session status is already failed
    final_res = client.post("/api/v1/registrations/verify", json={
        "verification_id": v_id,
        "otp": "999999"
    })
    assert final_res.status_code == 400
    assert "already failed" in final_res.json()["detail"].lower()
