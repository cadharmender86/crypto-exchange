import asyncio

from app.core.database import AsyncSessionLocal
from app.repositories.order_repository import OrderRepository


async def main():
    async with AsyncSessionLocal() as db:

        orders = await OrderRepository.list_open_orders(
            db=db,
            trading_pair_id="REPLACE_UUID",
        )

        print("Open Orders:", len(orders))


if __name__ == "__main__":
    asyncio.run(main())