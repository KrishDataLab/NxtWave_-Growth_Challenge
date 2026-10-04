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

def test_metrics_summary_empty(client):
    res = client.get("/api/v1/metrics/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_registrations"] == 0
    assert data["registrations_today"] == 0
    assert data["registration_conversion_rate"] == 0.0
    assert data["referral_share_rate"] == 0.0
    assert data["referral_registration_rate"] == 0.0

def test_metrics_summary_with_data(client, db_session):
    # Perform 2 verified registrations (1 organic, 1 referred)
    reg1_res = register_user_with_otp(client, db_session, {
        "full_name": "Org Registrant",
        "email": "org@example.com",
        "phone": "9990001112",
        "college_name": "IIT Madras",
        "branch": "CS",
        "graduation_year": 2026,
        "source": "google",
        "medium": "search"
    })
    code1 = reg1_res.json()["referral_code"]

    client.post("/api/v1/events", json={"event_name": "whatsapp_share"})

    register_user_with_otp(client, db_session, {
        "full_name": "Referred Registrant",
        "email": "ref@example.com",
        "phone": "9990001113",
        "college_name": "IIT Madras",
        "branch": "CS",
        "graduation_year": 2026,
        "source": "whatsapp",
        "medium": "community",
        "referral_code": code1
    })

    # Fetch Metrics
    res = client.get("/api/v1/metrics/summary")
    assert res.status_code == 200
    data = res.json()

    assert data["total_registrations"] == 2
    assert data["total_referral_registrations"] == 1
    assert data["registration_started"] == 2
    assert data["registration_completed"] == 2
    assert data["whatsapp_share_events"] == 1
    assert data["registration_conversion_rate"] == 100.0
    assert data["referral_share_rate"] == 50.0
    assert data["referral_registration_rate"] == 50.0
    assert len(data["top_referral_codes"]) == 1
    assert data["top_referral_codes"][0]["referral_code"] == code1
    assert data["top_referral_codes"][0]["count"] == 1
