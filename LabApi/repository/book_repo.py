from typing import List, Optional, Dict
from uuid import UUID, uuid4
from models.storage import BOOKS_STORAGE

class BookRepository:
    async def get_all(self) -> List[Dict]:
        return BOOKS_STORAGE

    async def get_by_id(self, book_id: UUID) -> Optional[Dict]:
        return next((b for b in BOOKS_STORAGE if b["id"] == book_id), None)

    async def add(self, book_data: Dict) -> Dict:
        book_data["id"] = uuid4()
        BOOKS_STORAGE.append(book_data)
        return book_data

    async def delete(self, book_id: UUID) -> bool:
        for i, b in enumerate(BOOKS_STORAGE):
            if b["id"] == book_id:
                del BOOKS_STORAGE[i]
                return True
        return False