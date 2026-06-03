from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db
from models.books import BookModel
from repository.book_repo import BookRepository
from schemas.book import Book as BookSchema, BookCreate, BookCursorPage
from core.security import decode_token

router = APIRouter(prefix="/books", tags=["books"])
bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["sub"]


@router.get("/", response_model=BookCursorPage)
async def read_books(
    limit: int = Query(10, ge=1, le=100),
    cursor: int = Query(None),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    repo = BookRepository(db)
    books = await repo.get_all(limit=limit, cursor=cursor)
    next_cursor = books[-1].id if len(books) == limit else None
    return BookCursorPage(items=books, next_cursor=next_cursor, limit=limit)


@router.get("/{book_id}", response_model=BookSchema)
async def read_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookSchema, status_code=201)
async def create_book(
    book_data: BookCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    repo = BookRepository(db)
    return await repo.create(BookModel(**book_data.model_dump()))


@router.put("/{book_id}", response_model=BookSchema)
async def update_book(
    book_id: int,
    book_data: BookCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book_data.model_dump().items():
        setattr(book, key, value)
    return await repo.update(book)


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    await repo.delete(book)