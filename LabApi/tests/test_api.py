import pytest
from httpx import AsyncClient, ASGITransport
from main import app # тепер імпорт без LabApi

@pytest.mark.asyncio
async def test_read_books():
    # Використовуємо транспорт для зв'язку з FastAPI
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/books/", params={"limit": 10, "offset": 0})
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)