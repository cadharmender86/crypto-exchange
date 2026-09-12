import asyncio
from decimal import Decimal

from app.core.database import AsyncSessionLocal
from app.services.order_validation_service import OrderValidationService


async def main():
    async with AsyncSessionLocal() as db:

        pair, value = await OrderValidationService.validate_limit_order(
            db=db,
            pair_code="BTCUSDT",
            price=Decimal("50000.00"),
            quantity=Decimal("0.0010"),
        )

        print("PAIR:", pair.pair_code)
        print("ORDER VALUE:", value)


if __name__ == "__main__":
    asyncio.run(main())