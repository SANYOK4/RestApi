"""
Запускається один раз для створення тестового юзера і книг.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models.database import Base
from models.users import UserModel
from models.books import BookModel
from core.security import hash_password
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:WeRtY54321@localhost:54321/library_db"
)


async def init():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        # Створюємо тестового юзера
        user = UserModel(
            username="testuser",
            hashed_password=hash_password("testpass123")
        )
        session.add(user)

        # Додаємо 20 книг для тестування пагінації
        for i in range(20):
            book = BookModel(
                title=f"Book {i+1}",
                author=f"Author {i+1}",
                year=2000 + i
            )
            session.add(book)

        await session.commit()
    await engine.dispose()
    print("✅ Test data created!")


if __name__ == "__main__":
    asyncio.run(init())