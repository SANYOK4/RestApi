from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.books import BookModel


class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, limit: int, cursor: int | None) -> list[BookModel]:
        # Cursor пагінація: сортуємо за ID, беремо записи після курсора
        query = select(BookModel).order_by(BookModel.id)

        if cursor is not None:
            query = query.where(BookModel.id > cursor)

        query = query.limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, book_id: int) -> BookModel | None:
        result = await self.db.execute(
            select(BookModel).where(BookModel.id == book_id)
        )
        return result.scalar_one_or_none()

    async def create(self, book: BookModel) -> BookModel:
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def update(self, book: BookModel) -> BookModel:
        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def delete(self, book: BookModel) -> None:
        await self.db.delete(book)
        await self.db.commit()