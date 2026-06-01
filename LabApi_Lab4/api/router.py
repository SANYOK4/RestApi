from fastapi import APIRouter, Depends, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.database import get_db
from repository.book_repo import BookRepository
from schemas.book import Book, BookCreate, BookPage

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=BookPage)
async def read_books(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    repo = BookRepository(db)
    books, total = await repo.get_all(limit=limit, offset=offset)
    return BookPage(items=books, total=total, limit=limit, offset=offset)


@router.get("/{book_id}", response_model=Book)
async def read_book(book_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=Book, status_code=201)
async def create_book(book_data: BookCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = BookRepository(db)
    return await repo.create(book_data.model_dump())


@router.put("/{book_id}", response_model=Book)
async def update_book(
    book_id: str,
    book_data: BookCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    repo = BookRepository(db)
    book = await repo.update(book_id, book_data.model_dump())
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = BookRepository(db)
    deleted = await repo.delete(book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")