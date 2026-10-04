import os
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Header, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.db.models import RegistrationModel, AnalyticsEventModel, RegistrationVerificationModel
from app.services.metrics_service import get_growth_metrics_summary

router = APIRouter(prefix="/admin", tags=["Admin Growth Dashboard"])

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "nxtwave_admin_2026")

class AdminLoginRequest(BaseModel):
    password: str

@router.post("/login")
def admin_login(body: AdminLoginRequest):
    if body.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password"
        )
    return {"success": True, "token": "admin_session_nxtwave_growth_2026", "message": "Admin authenticated"}

def verify_admin_token(x_admin_token: str | None = Header(default=None, alias="X-Admin-Token")):
    if not x_admin_token or "admin_session" not in x_admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required"
        )

@router.get("/dashboard")
def get_admin_dashboard(db: Session = Depends(get_db), _: None = Depends(verify_admin_token)):
    metrics = get_growth_metrics_summary(db)
    
    # 1. Acquisition Channel Performance & ₹2,000 Budget Optimization Analysis
    total_regs = metrics.total_registrations or 1
    source_counts = metrics.registrations_by_source or {}

    wa_cnt = source_counts.get("whatsapp", 0) + source_counts.get("wa", 0)
    comm_cnt = source_counts.get("community", 0) + source_counts.get("friend", 0) + source_counts.get("college club", 0)
    paid_cnt = source_counts.get("instagram", 0) + source_counts.get("linkedin", 0) + source_counts.get("paid", 0)
    direct_cnt = source_counts.get("direct", 0) + source_counts.get("other", 0)

    # Budget optimization simulation for ₹2,000 allocation
    budget_total = 2000
    if paid_cnt > comm_cnt and paid_cnt > wa_cnt:
        allocated = {"paid_amplification": 1200, "whatsapp": 500, "student_communities": 300}
        top_channel = "Paid Amplification"
    elif comm_cnt >= wa_cnt:
        allocated = {"student_communities": 1100, "whatsapp": 600, "paid_amplification": 300}
        top_channel = "Student Communities"
    else:
        allocated = {"whatsapp": 1200, "student_communities": 500, "paid_amplification": 300}
        top_channel = "WhatsApp Communities"

    channel_performance = {
        "whatsapp": {"registrations": wa_cnt, "percentage": round((wa_cnt / total_regs) * 100, 1)},
        "student_communities": {"registrations": comm_cnt, "percentage": round((comm_cnt / total_regs) * 100, 1)},
        "paid_amplification": {"registrations": paid_cnt, "percentage": round((paid_cnt / total_regs) * 100, 1)},
        "direct_other": {"registrations": direct_cnt, "percentage": round((direct_cnt / total_regs) * 100, 1)},
        "budget_optimization": {
            "total_budget": budget_total,
            "recommended_allocation": allocated,
            "highest_converting_source": top_channel
        }
    }

    # 2. Verification Friction Analysis: OTP vs Magic Link
    otp_count = db.query(RegistrationModel).filter(
        (RegistrationModel.verification_method == "otp") | (RegistrationModel.verification_method.is_(None))
    ).count()

    magic_count = db.query(RegistrationModel).filter(
        RegistrationModel.verification_method == "magic_link"
    ).count()

    verification_friction_analysis = {
        "otp_verified_registrations": otp_count,
        "magic_link_verified_registrations": magic_count,
        "magic_link_adoption_pct": round((magic_count / total_regs) * 100, 1) if total_regs > 0 else 0,
        "estimated_time_saved_seconds": magic_count * 25  # ~25s saved per magic link click vs entering 6 digits
    }

    return {
        "summary": metrics,
        "channel_performance": channel_performance,
        "verification_friction_analysis": verification_friction_analysis
    }

@router.get("/export-csv")
def export_registrations_csv(db: Session = Depends(get_db), _: None = Depends(verify_admin_token)):
    registrations = db.query(RegistrationModel).order_by(RegistrationModel.id.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write CSV Header
    writer.writerow([
        "ID", "Full Name", "Email", "Phone", "College Name", "Branch", 
        "Graduation Year", "Source", "Medium", "Campaign", "Referral Code", 
        "Referred By", "Verification Method", "Created At"
    ])

    for reg in registrations:
        writer.writerow([
            reg.id,
            reg.full_name,
            reg.email,
            reg.phone,
            reg.college_name,
            reg.branch,
            reg.graduation_year,
            reg.source or "direct",
            reg.medium or "community",
            reg.campaign or "ai60",
            reg.referral_code,
            reg.referred_by or "",
            getattr(reg, "verification_method", "otp") or "otp",
            reg.created_at.isoformat() if reg.created_at else ""
        ])

    csv_data = output.getvalue()

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=nxtwave_registrations_export.csv"}
    )
