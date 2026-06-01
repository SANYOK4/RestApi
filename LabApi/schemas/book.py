from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class BookStatus(str, Enum):
    AVAILABLE = "available"
    ISSUED = "issued"


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1)
    description: Optional[str] = None
    year: int = Field(..., gt=0, lt=2100)


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int

    class Config:
        from_attributes = True


# Схема відповіді для cursor пагінації
class BookCursorPage(BaseModel):
    items: list[Book]
    next_cursor: Optional[int]  # None якщо більше немає записів
    limit: int