from fastapi import APIRouter

from app.api.v1 import accounts, assets, auth, health, internal, ledger, transfers, users


api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(assets.router)
api_router.include_router(auth.router)
api_router.include_router(accounts.router)
api_router.include_router(ledger.router)
api_router.include_router(transfers.router)
api_router.include_router(internal.router)
