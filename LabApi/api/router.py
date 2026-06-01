from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import get_db
from models.books import BookModel
from repository.book_repo import BookRepository
from schemas.book import Book as BookSchema, BookCreate, BookCursorPage

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=BookCursorPage)
async def read_books(
    limit: int = Query(10, ge=1, le=100),
    cursor: int = Query(None),  # Замість offset тепер cursor (останній відомий ID)
    db: AsyncSession = Depends(get_db),
):
    repo = BookRepository(db)
    books = await repo.get_all(limit=limit, cursor=cursor)

    # next_cursor — це ID останнього елемента на сторінці
    # Якщо повернулось менше ніж limit — більше немає сторінок
    next_cursor = books[-1].id if len(books) == limit else None

    return BookCursorPage(
        items=books,
        next_cursor=next_cursor,
        limit=limit,
    )


@router.get("/{book_id}", response_model=BookSchema)
async def read_book(book_id: int, db: AsyncSession = Depends(get_db)):
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookSchema, status_code=201)
async def create_book(book_data: BookCreate, db: AsyncSession = Depends(get_db)):
    repo = BookRepository(db)
    new_book = BookModel(
        title=book_data.title,
        author=book_data.author,
        description=book_data.description,
        year=book_data.year,
    )
    return await repo.create(new_book)


@router.put("/{book_id}", response_model=BookSchema)
async def update_book(
    book_id: int, book_data: BookCreate, db: AsyncSession = Depends(get_db)
):
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book.title = book_data.title
    book.author = book_data.author
    book.description = book_data.description
    book.year = book_data.year

    return await repo.update(book)


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    await repo.delete(book)