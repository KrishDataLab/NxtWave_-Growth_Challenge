import pytest
from app.db.models import RegistrationModel, RegistrationVerificationModel, AnalyticsEventModel
from app.db.seed_demo_data import seed_demo_data
from app.services.metrics_service import get_growth_metrics_summary

def test_demo_data_seeding_and_flag(db_session):
    # Run seeding
    count = seed_demo_data(db_session)
    assert count == 85

    # Confirm demo records exist and are marked is_demo=True
    demo_regs = db_session.query(RegistrationModel).filter(RegistrationModel.is_demo == True).all()
    assert len(demo_regs) == 85
    for reg in demo_regs:
        assert reg.is_demo is True
        assert "demo" in reg.email.lower()
        assert "example.com" in reg.email.lower()
        assert "Demo Student" in reg.full_name

def test_demo_data_exclusion_from_real_counts(db_session):
    # Add 1 real registration
    real_reg = RegistrationModel(
        full_name="Real Campaign Student",
        email="realstudent@gmail.com",
        phone="9876543210",
        college_name="IIT Bombay",
        branch="CSE",
        graduation_year=2026,
        referral_code="AI60-REAL1",
        email_verified=True,
        is_demo=False
    )
    db_session.add(real_reg)
    db_session.commit()

    # Seed demo data
    seed_demo_data(db_session)

    # Real mode summary: must contain only 1 real registration
    real_summary = get_growth_metrics_summary(db_session, mode="real")
    assert real_summary.total_registrations == 1

    # Demo mode summary: must contain 85 demo registrations
    demo_summary = get_growth_metrics_summary(db_session, mode="demo")
    assert demo_summary.total_registrations == 85

    # Combined mode summary: 86 registrations
    combined_summary = get_growth_metrics_summary(db_session, mode="combined")
    assert combined_summary.total_registrations == 86

def test_demo_seeding_is_idempotent(db_session):
    # Run seed script twice
    count1 = seed_demo_data(db_session)
    count2 = seed_demo_data(db_session)

    assert count1 == 85
    assert count2 == 85

    total_demo_regs = db_session.query(RegistrationModel).filter(RegistrationModel.is_demo == True).count()
    assert total_demo_regs == 85

def test_admin_dashboard_api_mode_filter(client, db_session, monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", "secret_pass_123")
    monkeypatch.setenv("ADMIN_SESSION_SECRET", "secret_session_key_32bytes_long")

    seed_demo_data(db_session)

    login_res = client.post("/api/v1/admin/login", json={"password": "secret_pass_123"})
    token = login_res.json()["token"]

    # Test mode=real (returns 0 registrations if no real regs)
    res_real = client.get("/api/v1/admin/dashboard?mode=real", headers={"X-Admin-Token": token})
    assert res_real.status_code == 200
    data_real = res_real.json()
    assert data_real["summary"]["total_registrations"] == 0

    # Test mode=demo (returns 85 registrations)
    res_demo = client.get("/api/v1/admin/dashboard?mode=demo", headers={"X-Admin-Token": token})
    assert res_demo.status_code == 200
    data_demo = res_demo.json()
    assert data_demo["summary"]["total_registrations"] == 85
    assert data_demo["mode"] == "demo"

    # CSV Export in demo mode
    csv_demo = client.get("/api/v1/admin/export-csv?mode=demo", headers={"X-Admin-Token": token})
    assert csv_demo.status_code == 200
    assert "demo01@example.com" in csv_demo.text
    assert "nxtwave_demo_registrations.csv" in csv_demo.headers["content-disposition"]
