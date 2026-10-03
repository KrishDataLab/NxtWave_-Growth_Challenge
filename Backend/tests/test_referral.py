def test_referral_generation_and_attribution(client):
    # Register User A (referrer)
    user_a_payload = {
        "full_name": "User Alpha",
        "email": "alpha@example.com",
        "phone": "9876543210",
        "college_name": "IIT Bombay",
        "branch": "CSE",
        "graduation_year": 2026
    }
    res_a = client.post("/api/v1/registrations", json=user_a_payload)
    assert res_a.status_code == 201
    user_a_code = res_a.json()["referral_code"]

    # Register User B using User A's referral code
    user_b_payload = {
        "full_name": "User Beta",
        "email": "beta@example.com",
        "phone": "9876543211",
        "college_name": "IIT Bombay",
        "branch": "EE",
        "graduation_year": 2026,
        "referral_code": user_a_code  # User B arrived via ?ref=user_a_code
    }
    res_b = client.post("/api/v1/registrations", json=user_b_payload)
    assert res_b.status_code == 201
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
