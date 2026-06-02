import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, patch

from main import app
from models.database import Base, get_db
from core.security import create_access_token

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def client():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.fixture
def access_token():
    return create_access_token({"sub": "testuser"})


@pytest.fixture
def auth_headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def mock_redis_under_limit():
    """Redis мок — лічильник ще не досяг ліміту"""
    mock = AsyncMock()
    mock.incr = AsyncMock(return_value=1)
    mock.expire = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_redis_over_limit_auth():
    """Redis мок — авторизований юзер перевищив ліміт (>10)"""
    mock = AsyncMock()
    mock.incr = AsyncMock(return_value=11)
    mock.expire = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_redis_over_limit_anon():
    """Redis мок — анонімний юзер перевищив ліміт (>2)"""
    mock = AsyncMock()
    mock.incr = AsyncMock(return_value=3)
    mock.expire = AsyncMock(return_value=True)
    return mock