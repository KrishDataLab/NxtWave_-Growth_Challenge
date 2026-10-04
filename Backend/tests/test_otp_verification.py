from app.services.otp_service import hash_otp
from app.db.models import RegistrationVerificationModel, RegistrationModel
from app.services.whatsapp_service import get_whatsapp_service

def test_start_registration_security_otp_not_in_api(client, db_session):
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
    assert "otp" not in data
    assert "raw_otp" not in data

    # Confirm unverified registration does not exist in confirmed registrations table
    unverified_reg = db_session.query(RegistrationModel).filter(
        RegistrationModel.email == "rohan.mehta@example.com"
    ).first()
    assert unverified_reg is None

def test_resend_cooldown_rate_limit(client, db_session):
    payload = {
        "full_name": "Siddharth Verma",
        "email": "siddharth.verma@example.com",
        "phone": "9876543211",
        "college_name": "IIT Delhi",
        "branch": "Electrical",
        "graduation_year": 2026
    }
    res1 = client.post("/api/v1/registrations/start", json=payload)
    assert res1.status_code == 200

    # Rapid resend within 30 seconds should trigger cooldown HTTP 429
    res2 = client.post("/api/v1/registrations/start", json=payload)
    assert res2.status_code == 429
    assert "recently sent" in res2.json()["detail"].lower()

def test_verify_otp_success_and_email_verified(client, db_session):
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

    verification_rec = db_session.query(RegistrationVerificationModel).filter(
        RegistrationVerificationModel.verification_id == v_id
    ).first()
    assert verification_rec is not None

    # Find matching 6-digit OTP
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

    # Confirm in DB that confirmed registration record has email_verified=True
    reg_db = db_session.query(RegistrationModel).filter(
        RegistrationModel.email == "priya.sharma@example.com"
    ).first()
    assert reg_db is not None
    assert reg_db.email_verified is True
    assert reg_db.whatsapp_opt_in is True

def test_incorrect_otp_rejected(client, db_session):
    start_payload = {
        "full_name": "Aman Gupta",
        "email": "aman.gupta@example.com",
        "phone": "9811223344",
        "college_name": "DTU Delhi",
        "branch": "IT",
        "graduation_year": 2026
    }
    start_res = client.post("/api/v1/registrations/start", json=start_payload)
    v_id = start_res.json()["verification_id"]

    verify_res = client.post("/api/v1/registrations/verify", json={
        "verification_id": v_id,
        "otp": "000000"
    })
    assert verify_res.status_code == 400
    assert "incorrect verification code" in verify_res.json()["detail"].lower()

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

def test_mock_whatsapp_service_simulation(client, db_session):
    wa_service = get_whatsapp_service()
    res = wa_service.send_whatsapp_confirmation(
        phone="9876543210",
        full_name="Test Student",
        referral_code="AI60-TEST"
    )
    assert res.status == "mocked"
    assert res.delivered is False
    assert "AI60-TEST" in res.message_preview
