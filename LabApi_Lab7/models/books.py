from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from models.database import Base


class BookModel(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    author: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String, nullable=True)
    year: Mapped[int] = mapped_column(Integer)