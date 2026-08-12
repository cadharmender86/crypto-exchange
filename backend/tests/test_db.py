import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def main():
    engine = create_async_engine(settings.database_url)

    async with engine.connect() as connection:
        result = await connection.execute(
            text("""
                SELECT
                    current_database(),
                    current_user,
                    inet_server_addr(),
                    inet_server_port()
            """)
        )

        print("DATABASE:", result.fetchone())

    await engine.dispose()


asyncio.run(main())