import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.db.models import RegistrationModel, RegistrationVerificationModel, AnalyticsEventModel

DEMO_STUDENTS_COUNT = 85

DEMO_COLLEGES = [
    "Demo Institute of Technology",
    "Simulated Engineering College",
    "Fictional University of AI & Tech",
    "Demo National Institute of Science",
    "Synthetic College of Engineering"
]

DEMO_BRANCHES = ["CSE", "ECE", "AI & DS", "Mechanical", "EEE"]

SOURCES = ["whatsapp", "community", "instagram", "direct"]
MEDIUMS = {
    "whatsapp": "wa_group",
    "community": "campus_lead",
    "instagram": "paid_ad",
    "direct": "none"
}

def seed_demo_data(db: Session = None) -> int:
    close_session = False
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        close_session = True

    try:
        # Idempotent cleanup of existing demo data
        db.query(RegistrationModel).filter(RegistrationModel.is_demo == True).delete()
        db.query(RegistrationVerificationModel).filter(RegistrationVerificationModel.is_demo == True).delete()
        db.query(AnalyticsEventModel).filter(AnalyticsEventModel.is_demo == True).delete()
        db.commit()

        now = datetime.now(timezone.utc)
        random.seed(42)

        demo_referral_codes = ["DEMO-REF-101", "DEMO-REF-102", "DEMO-REF-103", "DEMO-REF-104", "DEMO-REF-105"]

        registrations_to_add = []
        verifications_to_add = []
        analytics_to_add = []

        for i in range(1, DEMO_STUDENTS_COUNT + 1):
            student_num = f"{i:02d}"
            name = f"Demo Student {student_num}"
            email = f"demo{student_num}@example.com"
            phone = f"555-01{student_num}"
            college = DEMO_COLLEGES[i % len(DEMO_COLLEGES)]
            branch = DEMO_BRANCHES[i % len(DEMO_BRANCHES)]
            source = SOURCES[i % len(SOURCES)]
            medium = MEDIUMS[source]
            campaign = "ai60_demo"
            days_ago = random.randint(0, 6)
            created_at = now - timedelta(days=days_ago, hours=random.randint(1, 12), minutes=random.randint(0, 59))
            
            ref_code = f"DEMO-AI60-{student_num}"
            referred_by = random.choice(demo_referral_codes) if i % 3 == 0 else None

            method = "magic_link" if i % 2 == 0 else "otp"

            reg = RegistrationModel(
                full_name=name,
                email=email,
                phone=phone,
                college_name=college,
                branch=branch,
                graduation_year=2026,
                source=source,
                medium=medium,
                campaign=campaign,
                referral_code=ref_code,
                referred_by=referred_by,
                email_verified=True,
                whatsapp_opt_in=(i % 2 == 0),
                verification_method=method,
                verified_at=created_at + timedelta(seconds=45),
                is_demo=True,
                created_at=created_at
            )
            registrations_to_add.append(reg)

            verif = RegistrationVerificationModel(
                verification_id=f"demo-verif-{student_num}",
                magic_token=f"demo-magic-token-{student_num}",
                full_name=name,
                email=email,
                phone=phone,
                college_name=college,
                branch=branch,
                graduation_year=2026,
                source=source,
                medium=medium,
                campaign=campaign,
                referral_code=ref_code,
                whatsapp_opt_in=(i % 2 == 0),
                otp_hash="demo_hash",
                otp_expires_at=created_at + timedelta(minutes=15),
                verification_status="verified",
                verification_method=method,
                is_demo=True,
                created_at=created_at,
                verified_at=created_at + timedelta(seconds=45)
            )
            verifications_to_add.append(verif)

            analytics_to_add.append(AnalyticsEventModel(
                event_name="hero_cta_click",
                source=source,
                medium=medium,
                campaign=campaign,
                is_demo=True,
                created_at=created_at - timedelta(minutes=2)
            ))
            analytics_to_add.append(AnalyticsEventModel(
                event_name="registration_started",
                session_id=f"demo-sess-{student_num}",
                source=source,
                medium=medium,
                campaign=campaign,
                is_demo=True,
                created_at=created_at - timedelta(minutes=1)
            ))
            analytics_to_add.append(AnalyticsEventModel(
                event_name="registration_completed",
                session_id=f"demo-sess-{student_num}",
                source=source,
                medium=medium,
                campaign=campaign,
                referral_code=ref_code,
                is_demo=True,
                created_at=created_at
            ))

            if method == "magic_link":
                analytics_to_add.append(AnalyticsEventModel(
                    event_name="magic_link_verified",
                    source=source,
                    campaign=campaign,
                    is_demo=True,
                    created_at=created_at + timedelta(seconds=45)
                ))

            if i % 4 == 0:
                analytics_to_add.append(AnalyticsEventModel(
                    event_name="whatsapp_share",
                    source=source,
                    campaign=campaign,
                    is_demo=True,
                    created_at=created_at + timedelta(minutes=5)
                ))

        db.add_all(registrations_to_add)
        db.add_all(verifications_to_add)
        db.add_all(analytics_to_add)
        db.commit()

        return DEMO_STUDENTS_COUNT
    finally:
        if close_session:
            db.close()

if __name__ == "__main__":
    count = seed_demo_data()
    print(f"Successfully seeded {count} idempotent demo records.")
