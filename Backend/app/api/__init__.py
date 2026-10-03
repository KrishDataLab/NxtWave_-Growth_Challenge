from fastapi import APIRouter
from app.api.registrations import router as registrations_router
from app.api.referrals import router as referrals_router
from app.api.analytics import router as analytics_router
from app.api.metrics import router as metrics_router
from app.api.health import router as health_router

api_router = APIRouter()
api_router.include_router(registrations_router)
api_router.include_router(referrals_router)
api_router.include_router(analytics_router)
api_router.include_router(metrics_router)
api_router.include_router(health_router)

__all__ = ["api_router"]
