from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.books import BookModel

class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, limit: int, offset: int):
        query = select(BookModel).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()