import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from main import app
from models.database import get_db
from repository.book_repo import BookRepository


@pytest.fixture
async def mock_db():
    db = MagicMock()
    collection = MagicMock()

    books_store = {}
    counter = [1]

    async def mock_insert(doc):
        from bson import ObjectId
        oid = ObjectId()
        doc["_id"] = oid
        books_store[str(oid)] = doc.copy()
        result = MagicMock()
        result.inserted_id = oid
        return result

    async def mock_find_one(query):
        from bson import ObjectId
        oid = query.get("_id")
        if oid:
            return books_store.get(str(oid), None)
        return None

    async def mock_count(_):
        return len(books_store)

    async def mock_update(query, update):
        from bson import ObjectId
        oid = query.get("_id")
        if oid and str(oid) in books_store:
            books_store[str(oid)].update(update["$set"])
        result = MagicMock()
        result.modified_count = 1
        return result

    async def mock_delete(query):
        from bson import ObjectId
        oid = query.get("_id")
        key = str(oid) if oid else None
        result = MagicMock()
        if key and key in books_store:
            del books_store[key]
            result.deleted_count = 1
        else:
            result.deleted_count = 0
        return result

    class MockCursor:
        def __init__(self, items):
            self._items = items
            self._index = 0

        def skip(self, n):
            self._items = self._items[n:]
            return self

        def limit(self, n):
            self._items = self._items[:n]
            return self

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self._index >= len(self._items):
                raise StopAsyncIteration
            item = self._items[self._index]
            self._index += 1
            return item

    def mock_find(*args, **kwargs):
        return MockCursor(list(books_store.values()))

    collection.insert_one = mock_insert
    collection.find_one = mock_find_one
    collection.count_documents = mock_count
    collection.update_one = mock_update
    collection.delete_one = mock_delete
    collection.find = mock_find

    db.__getitem__ = MagicMock(return_value=collection)
    return db


@pytest.fixture
async def client(mock_db):
    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()