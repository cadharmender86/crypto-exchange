from fastapi import APIRouter

from app.api.v1.admin.fiat_deposits import router as fiat_deposit_router

router = APIRouter(prefix="/admin", tags=["Admin"])

router.include_router(fiat_deposit_router)