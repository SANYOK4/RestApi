import time
import redis.asyncio as aioredis
from fastapi import Request, HTTPException
from core.security import decode_token

REDIS_URL = "redis://redis:6379"

RATE_LIMITS = {
    "authenticated": (10, 60),  # 10 запитів за 60 секунд
    "anonymous":     (2,  60),  # 2 запити за 60 секунд
}

redis_client: aioredis.Redis = None


async def get_redis() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    return redis_client


async def rate_limit(request: Request, user_id: str | None = None):
    r = await get_redis()

    # Визначаємо identity
    identity = user_id or request.client.host

    # Визначаємо тип ліміту
    limit_type = "authenticated" if user_id else "anonymous"
    limit, period = RATE_LIMITS[limit_type]

    # Ключ для Redis
    key = f"rate_limit_{identity}"

    # Sliding window
    now = int(time.time())
    window_start = now - period

    # Видаляємо застарілі записи
    await r.zremrangebyscore(key, min=0, max=window_start)

    # Рахуємо поточну кількість запитів
    request_count = await r.zcard(key)

    # Перевіряємо ліміт
    if request_count >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Limit: {limit} per {period}s"
        )

    # Додаємо поточний запит
    await r.zadd(key, {str(now): now})
    await r.expire(key, period)


async def check_rate_limit(request: Request):
    """Dependency для ендпоінтів — визначає user_id з токена"""
    user_id = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            user_id = payload.get("sub")

    await rate_limit(request, user_id)