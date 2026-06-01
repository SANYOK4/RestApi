from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional


def book_helper(book: dict) -> dict:
    """Конвертує MongoDB документ — _id з ObjectId в str"""
    book["_id"] = str(book["_id"])
    return book


class BookRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["books"]

    async def get_all(self, limit: int, offset: int) -> tuple[list[dict], int]:
        total = await self.collection.count_documents({})
        cursor = self.collection.find().skip(offset).limit(limit)
        books = [book_helper(book) async for book in cursor]
        return books, total

    async def get_by_id(self, book_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(book_id):
            return None
        book = await self.collection.find_one({"_id": ObjectId(book_id)})
        return book_helper(book) if book else None

    async def create(self, book_data: dict) -> dict:
        result = await self.collection.insert_one(book_data)
        book = await self.collection.find_one({"_id": result.inserted_id})
        return book_helper(book)

    async def update(self, book_id: str, book_data: dict) -> Optional[dict]:
        if not ObjectId.is_valid(book_id):
            return None
        await self.collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": book_data}
        )
        book = await self.collection.find_one({"_id": ObjectId(book_id)})
        return book_helper(book) if book else None

    async def delete(self, book_id: str) -> bool:
        if not ObjectId.is_valid(book_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(book_id)})
        return result.deleted_count > 0