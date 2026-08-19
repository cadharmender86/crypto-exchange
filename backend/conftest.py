import httpx
import pytest_asyncio

from app.core.database import AsyncSessionLocal, engine


@pytest_asyncio.fixture
async def db():
    async with AsyncSessionLocal() as session:
        yield session

    # Prevent asyncpg connections from being reused across pytest event loops.
    await engine.dispose()


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(
        base_url="http://127.0.0.1:8000"
    ) as client:
        yield client
