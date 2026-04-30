from repository.book_repo import BookRepository
from typing import Optional

class BookService:
    def __init__(self):
        self.repo = BookRepository()

    async def list_books(self, status=None, author=None, sort_by=None):
        books = await self.repo.get_all()
        
        # Фільтрація
        if status:
            books = [b for b in books if b["status"] == status]
        if author:
            books = [b for b in books if author.lower() in b["author"].lower()]
        
        # Сортування
        if sort_by in ["title", "year"]:
            books = sorted(books, key=lambda x: x[sort_by])
            
        return books

    async def create_book(self, book_data):
        return await self.repo.add(book_data)

    async def get_book(self, book_id):
        return await self.repo.get_by_id(book_id)

    async def delete_book(self, book_id):
        return await self.repo.delete(book_id)