from models.database import db
from models.book import BookModel


class BookRepository:

    def get_all(self, limit: int, offset: int):
        total = BookModel.query.count()
        books = BookModel.query.offset(offset).limit(limit).all()
        return books, total

    def get_by_id(self, book_id: int):
        return BookModel.query.get(book_id)

    def create(self, data: dict):
        book = BookModel(**data)
        db.session.add(book)
        db.session.commit()
        return book

    def update(self, book: BookModel, data: dict):
        for key, value in data.items():
            setattr(book, key, value)
        db.session.commit()
        return book

    def delete(self, book: BookModel):
        db.session.delete(book)
        db.session.commit()