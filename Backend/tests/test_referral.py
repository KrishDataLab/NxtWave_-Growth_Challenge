from app.db.models import RegistrationVerificationModel
from app.services.otp_service import hash_otp

def register_user_with_otp(client, db_session, payload):
    start_res = client.post("/api/v1/registrations/start", json=payload)
    assert start_res.status_code == 200
    v_id = start_res.json()["verification_id"]

    v_rec = db_session.query(RegistrationVerificationModel).filter(
        RegistrationVerificationModel.verification_id == v_id
    ).first()

    matching_otp = None
    for candidate in range(100000, 1000000):
        if hash_otp(str(candidate)) == v_rec.otp_hash:
            matching_otp = str(candidate)
            break

    verify_res = client.post("/api/v1/registrations/verify", json={
        "verification_id": v_id,
        "otp": matching_otp
    })
    assert verify_res.status_code == 201
    return verify_res

def test_referral_generation_and_attribution(client, db_session):
    # Register User A (referrer)
    res_a = register_user_with_otp(client, db_session, {
        "full_name": "User Alpha",
        "email": "alpha@example.com",
        "phone": "9876543210",
        "college_name": "IIT Bombay",
        "branch": "CSE",
        "graduation_year": 2026
    })
    user_a_code = res_a.json()["referral_code"]

    # Register User B using User A's referral code
    res_b = register_user_with_otp(client, db_session, {
        "full_name": "User Beta",
        "email": "beta@example.com",
        "phone": "9876543211",
        "college_name": "IIT Bombay",
        "branch": "EE",
        "graduation_year": 2026,
        "referral_code": user_a_code  # User B arrived via ?ref=user_a_code
    })
    user_b_code = res_b.json()["referral_code"]
    assert user_b_code != user_a_code

    # Check User A's referral stats via GET /api/v1/referrals/{referral_code}
    ref_res = client.get(f"/api/v1/referrals/{user_a_code}")
    assert ref_res.status_code == 200
    ref_data = ref_res.json()
    assert ref_data["referral_code"] == user_a_code
    assert ref_data["total_referred_registrations"] == 1
    assert "owner_registration_id" not in ref_data

def test_nonexistent_referral_code(client):
    res = client.get("/api/v1/referrals/AI60-NONEXIST")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()
