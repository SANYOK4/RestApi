from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.database import get_db
from models.books import BookModel
from schemas.book import Book as BookSchema, BookCreate

router = APIRouter(prefix="/books", tags=["books"])

# Отримати список книг (GET)
@router.get("/", response_model=list[BookSchema])
async def read_books(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(BookModel).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

# Додати нову книгу (POST)
@router.post("/", response_model=BookSchema)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    new_book = BookModel(
        title=book.title,
        author=book.author,
        description=book.description,
        year=book.year
    )
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book