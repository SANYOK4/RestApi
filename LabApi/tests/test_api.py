import pytest
from httpx import AsyncClient, ASGITransport  # ПЕРЕВІРТЕ ЦЕЙ РЯДОК
from main import app

@pytest.mark.asyncio
async def test_create_and_get_book():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create
        payload = {"title": "Kobzar", "author": "Shevchenko", "year": 1840}
        resp = await ac.post("/books/", json=payload)
        assert resp.status_code == 201
        book_id = resp.json()["id"]

        # Get by ID
        resp = await ac.get(f"/books/{book_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Kobzar"

@pytest.mark.asyncio
async def test_delete_idempotency():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await ac.delete(f"/books/{fake_id}")
        assert resp.status_code == 204