import pytest
from app.db.models import RegistrationModel, RegistrationVerificationModel, AnalyticsEventModel

def test_magic_link_auto_verification_flow(client, db_session):
    start_payload = {
        "full_name": "Magic User",
        "email": "magic@example.com",
        "phone": "9876543210",
        "college_name": "IIT Madras",
        "branch": "CSE",
        "graduation_year": 2026
    }
    start_res = client.post("/api/v1/registrations/start", json=start_payload)
    assert start_res.status_code == 200
    m_token = start_res.json().get("magic_token")
    assert m_token is not None

    # Auto-verify via magic token
    verify_res = client.post("/api/v1/registrations/verify-magic", json={"magic_token": m_token})
    assert verify_res.status_code == 200
    data = verify_res.json()
    assert data["success"] is True
    assert data["email_verified"] is True
    assert data["verification_method"] == "magic_link"
    assert data["referral_code"].startswith("AI60-")

    # Confirm DB row created with verification_method='magic_link'
    reg_db = db_session.query(RegistrationModel).filter_by(email="magic@example.com").first()
    assert reg_db is not None
    assert reg_db.verification_method == "magic_link"

def test_admin_login_and_unauthorized_access(client):
    # Bad login
    res1 = client.post("/api/v1/admin/login", json={"password": "wrongpassword"})
    assert res1.status_code == 401

    # Good login
    res2 = client.post("/api/v1/admin/login", json={"password": "nxtwave_admin_2026"})
    assert res2.status_code == 200
    token = res2.json()["token"]
    assert token.startswith("admin_session_")

    # Dashboard without token -> 401
    dash_unauth = client.get("/api/v1/admin/dashboard")
    assert dash_unauth.status_code == 401

    # Dashboard with token -> 200
    dash_auth = client.get("/api/v1/admin/dashboard", headers={"X-Admin-Token": token})
    assert dash_auth.status_code == 200
    dash_data = dash_auth.json()
    assert "summary" in dash_data
    assert "channel_performance" in dash_data
    assert "budget_optimization" in dash_data["channel_performance"]

def test_admin_export_csv(client, db_session):
    # Perform 1 registration first
    reg = RegistrationModel(
        full_name="Export User",
        email="export@example.com",
        phone="9876543210",
        college_name="IIT Delhi",
        branch="ECE",
        graduation_year=2026,
        referral_code="AI60-EX1",
        email_verified=True,
        verification_method="magic_link"
    )
    db_session.add(reg)
    db_session.commit()

    login_res = client.post("/api/v1/admin/login", json={"password": "nxtwave_admin_2026"})
    token = login_res.json()["token"]

    csv_res = client.get("/api/v1/admin/export-csv", headers={"X-Admin-Token": token})
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    content = csv_res.text
    assert "Export User" in content
    assert "export@example.com" in content
    assert "AI60-EX1" in content
    assert "magic_link" in content
