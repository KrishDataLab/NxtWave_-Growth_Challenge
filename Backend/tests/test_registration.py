def test_registration_success(client):
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
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "registration_id" in data
    assert data["referral_code"].startswith("AI60-")
    assert data["message"] == "Registration successful"

def test_duplicate_registration(client):
    payload = {
        "full_name": "Anita Roy",
        "email": "anita.roy@example.com",
        "phone": "9998887776",
        "college_name": "BITS Pilani",
        "branch": "ECE",
        "graduation_year": 2026
    }
    # First registration
    res1 = client.post("/api/v1/registrations", json=payload)
    assert res1.status_code == 201

    # Duplicate registration attempt
    res2 = client.post("/api/v1/registrations", json=payload)
    assert res2.status_code == 400
    assert "already registered" in res2.json()["detail"].lower()

def test_invalid_email(client):
    payload = {
        "full_name": "John Doe",
        "email": "invalid-email-string",
        "phone": "9998887776",
        "college_name": "NIT Trichy",
        "branch": "Mechanical",
        "graduation_year": 2026
    }
    response = client.post("/api/v1/registrations", json=payload)
    assert response.status_code == 422

def test_missing_required_fields(client):
    payload = {
        "email": "missing.name@example.com"
    }
    response = client.post("/api/v1/registrations", json=payload)
    assert response.status_code == 422
