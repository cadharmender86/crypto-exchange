from fastapi import APIRouter

from app.api.v1.accounts import router as accounts_router
from app.api.v1.assets import router as assets_router
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.internal import router as internal_router
from app.api.v1.ledger import router as ledger_router
from app.api.v1.transfers import router as transfers_router
from app.api.v1.users import router as users_router
from app.api.v1.wallets import router as wallets_router
from app.api.v1.wallet_addresses import router as wallet_addresses_router
from app.api.v1.deposits import router as deposits_router
from app.api.v1.withdrawals import router as withdrawals_router
from app.api.v1.orders import router as orders_router
from app.api.v1.trades import router as trades_router
from app.api.v1.market import router as market_router
from app.api.v1.admin_auth import router as admin_auth_router
from app.api.v1.admin import router as admin_router
from app.api.v1.admin_kyc import router as admin_kyc_router
from app.api.v1.admin_deposits import router as admin_deposits_router
from app.api.v1.admin_withdrawals import router as admin_withdrawals_router
from app.api.v1.admin_rbac import router as admin_rbac_router


api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(accounts_router)
api_router.include_router(deposits_router)
api_router.include_router(withdrawals_router)
api_router.include_router(ledger_router)
api_router.include_router(transfers_router)
api_router.include_router(assets_router)
api_router.include_router(health_router)
api_router.include_router(internal_router)
api_router.include_router(users_router)
api_router.include_router(wallets_router)
api_router.include_router(wallet_addresses_router)
api_router.include_router(withdrawals_router)
api_router.include_router(orders_router)
api_router.include_router(trades_router)
api_router.include_router(market_router)
api_router.include_router(admin_auth_router)
api_router.include_router(admin_router)
api_router.include_router(admin_kyc_router)
api_router.include_router(admin_withdrawals_router)
api_router.include_router(admin_rbac_router)
api_router.include_router(admin_deposits_router)
