def test_direct_registration_bypass_blocked(client):
    payload = {
        "full_name": "Rahul Sharma",
        "email": "rahul.sharma@example.com",
        "phone": "+91 9876543210",
        "college_name": "IIT Hyderabad",
        "branch": "Computer Science",
        "graduation_year": 2026,
        "source": "whatsapp",
        "medium": "community",
        "campaign": "ai60",
        "content": "college-group",
        "referral_code": "AI60-REF1"
    }
    response = client.post("/api/v1/registrations", json=payload)
    assert response.status_code == 400
    assert "direct unverified registration is disabled" in response.json()["detail"].lower()

def test_invalid_email(client):
    payload = {
        "full_name": "John Doe",
        "email": "invalid-email-string",
        "phone": "9998887776",
        "college_name": "NIT Trichy",
        "branch": "Mechanical",
        "graduation_year": 2026
    }
    response = client.post("/api/v1/registrations/start", json=payload)
    assert response.status_code == 422

def test_missing_required_fields(client):
    payload = {
        "email": "missing.name@example.com"
    }
    response = client.post("/api/v1/registrations/start", json=payload)
    assert response.status_code == 422
