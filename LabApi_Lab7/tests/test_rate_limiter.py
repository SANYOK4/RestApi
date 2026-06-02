import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException


def make_mock_redis(request_count: int):
    """Створює мок Redis з заданою кількістю запитів у вікні"""
    mock = AsyncMock()
    mock.zremrangebyscore = AsyncMock(return_value=0)
    mock.zcard = AsyncMock(return_value=request_count)
    mock.zadd = AsyncMock(return_value=1)
    mock.expire = AsyncMock(return_value=True)
    return mock


def make_request(token: str = None, ip: str = "127.0.0.1"):
    """Створює мок Request"""
    mock = MagicMock()
    mock.client.host = ip
    if token:
        mock.headers = {"Authorization": f"Bearer {token}"}
    else:
        mock.headers = {}
    return mock


def make_token(username: str) -> str:
    from core.security import create_access_token
    return create_access_token({"sub": username})


# ── Авторизований юзер ────────────────────────────────────────────────────────

async def test_auth_user_under_limit():
    """Авторизований юзер: 5 запитів з 10 → не кидає 429"""
    import core.rate_limiter as rl
    rl.redis_client = make_mock_redis(request_count=5)

    request = make_request(token=make_token("user1"))
    # Не має кидати виняток
    await rl.check_rate_limit(request)


async def test_auth_user_at_limit():
    """Авторизований юзер: рівно 10 запитів → кидає 429"""
    import core.rate_limiter as rl
    rl.redis_client = make_mock_redis(request_count=10)

    request = make_request(token=make_token("user1"))
    with pytest.raises(HTTPException) as exc:
        await rl.check_rate_limit(request)
    assert exc.value.status_code == 429
    assert "Too many requests" in exc.value.detail


# ── Анонімний юзер ────────────────────────────────────────────────────────────

async def test_anon_user_under_limit():
    """Анонімний юзер: 1 запит з 2 → не кидає 429"""
    import core.rate_limiter as rl
    rl.redis_client = make_mock_redis(request_count=1)

    request = make_request()  # без токена
    await rl.check_rate_limit(request)


async def test_anon_user_at_limit():
    """Анонімний юзер: рівно 2 запити → кидає 429"""
    import core.rate_limiter as rl
    rl.redis_client = make_mock_redis(request_count=2)

    request = make_request()  # без токена
    with pytest.raises(HTTPException) as exc:
        await rl.check_rate_limit(request)
    assert exc.value.status_code == 429
    assert "Too many requests" in exc.value.detail


# ── Інтеграційні тести через HTTP ─────────────────────────────────────────────

async def test_auth_user_under_limit_http(client, auth_headers):
    """HTTP: авторизований юзер не досяг ліміту → 200"""
    import core.rate_limiter as rl
    rl.redis_client = make_mock_redis(request_count=5)

    response = await client.get("/books/", headers=auth_headers)
    assert response.status_code == 200


async def test_auth_user_over_limit_http(client, auth_headers):
    """HTTP: авторизований юзер перевищив ліміт → 429"""
    import core.rate_limiter as rl
    rl.redis_client = make_mock_redis(request_count=10)

    response = await client.get("/books/", headers=auth_headers)
    assert response.status_code == 429


async def test_anon_user_under_limit_http(client):
    """HTTP: анонімний юзер не досяг ліміту → 401 (не 429)"""
    import core.rate_limiter as rl
    rl.redis_client = make_mock_redis(request_count=1)

    response = await client.get("/books/")
    assert response.status_code == 401  # rate limit не спрацював, але немає токена


async def test_anon_user_over_limit_http(client):
    """HTTP: анонімний юзер перевищив ліміт → 429"""
    import core.rate_limiter as rl
    rl.redis_client = make_mock_redis(request_count=2)

    response = await client.get("/books/")
    assert response.status_code == 429