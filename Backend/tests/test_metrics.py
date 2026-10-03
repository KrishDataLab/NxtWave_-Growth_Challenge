def test_metrics_summary_empty(client):
    res = client.get("/api/v1/metrics/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_registrations"] == 0
    assert data["registrations_today"] == 0
    assert data["registration_conversion_rate"] == 0.0
    assert data["referral_share_rate"] == 0.0
    assert data["referral_registration_rate"] == 0.0

def test_metrics_summary_with_data(client):
    # 1. Fire events
    client.post("/api/v1/events", json={"event_name": "registration_started"})
    client.post("/api/v1/events", json={"event_name": "registration_started"})
    client.post("/api/v1/events", json={"event_name": "whatsapp_share"})

    # 2. Perform 2 registrations (1 organic, 1 referred)
    reg1_res = client.post("/api/v1/registrations", json={
        "full_name": "Org Registrant",
        "email": "org@example.com",
        "phone": "9990001112",
        "college_name": "IIT Madras",
        "branch": "CS",
        "graduation_year": 2026,
        "source": "google",
        "medium": "search"
    })
    assert reg1_res.status_code == 201
    code1 = reg1_res.json()["referral_code"]

    client.post("/api/v1/registrations", json={
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
    # Each registration automatically creates a registration_completed event
    assert data["registration_completed"] == 2
    assert data["whatsapp_share_events"] == 1

    # Formulas check:
    # conversion rate = 2 / 2 * 100 = 100.0%
    assert data["registration_conversion_rate"] == 100.0
    # referral share rate = 1 / 2 * 100 = 50.0%
    assert data["referral_share_rate"] == 50.0
    # referral registration rate = 1 / 2 * 100 = 50.0%
    assert data["referral_registration_rate"] == 50.0
    # top referral codes check
    assert len(data["top_referral_codes"]) == 1
    assert data["top_referral_codes"][0]["referral_code"] == code1
    assert data["top_referral_codes"][0]["count"] == 1
