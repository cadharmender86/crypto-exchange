from fastapi import APIRouter

from app.api.v1 import assets, health, users
from app.api.v1 import auth
from app.api.v1 import assets
from app.api.v1 import accounts
from app.api.v1 import ledger
from app.api.v1 import transfers


api_router = APIRouter()

api_router.include_router(
    health.router,
)

api_router.include_router(
    users.router,
)

api_router.include_router(
    assets.router,
)

api_router.include_router(
    auth.router,
)

api_router.include_router(
    accounts.router
)

api_router.include_router(
    ledger.router
)

api_router.include_router(
    transfers.router
)