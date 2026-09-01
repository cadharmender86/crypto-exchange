from fastapi import APIRouter

from app.api.v1.admin.dashboard import router as dashboard_router
from app.api.v1.admin.audit_logs import router as audit_logs_router
from app.api.v1.admin.fiat_deposits import router as fiat_deposit_router
from app.api.v1.admin.users import router as users_router

router = APIRouter(prefix="/admin", tags=["Admin"])

router.include_router(dashboard_router)
router.include_router(audit_logs_router)
router.include_router(fiat_deposit_router)
router.include_router(users_router)