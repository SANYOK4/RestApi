from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1)
    description: Optional[str] = None
    year: int = Field(..., gt=0, lt=2100)


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: str = Field(alias="_id")

    model_config = ConfigDict(populate_by_name=True)


class BookPage(BaseModel):
    items: list[Book]
    total: int
    limit: int
    offset: int