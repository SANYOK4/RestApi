async def test_pagination(client):
    # Додаємо 5 книг
    for i in range(5):
        await client.post("/books/", json={"title": f"Book {i}", "author": "Author", "year": 2020})

    response = await client.get("/books/", params={"limit": 2, "offset": 0})
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert data["total"] == 5
    assert len(data["items"]) == 2

    response2 = await client.get("/books/", params={"limit": 2, "offset": 2})
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2["items"]) == 2

    response3 = await client.get("/books/", params={"limit": 2, "offset": 4})
    assert response3.status_code == 200
    data3 = response3.json()
    assert len(data3["items"]) == 1


async def test_offset_beyond_total(client):
    response = await client.get("/books/", params={"limit": 10, "offset": 9999})
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []


async def test_create_book(client):
    payload = {"title": "Test Book", "author": "Author", "year": 2024}
    response = await client.post("/books/", json=payload)
    assert response.status_code == 201
    book = response.json()
    assert book["title"] == "Test Book"
    assert "_id" in book


async def test_get_book_by_id(client):
    payload = {"title": "Find Me", "author": "Author", "year": 2020}
    create_resp = await client.post("/books/", json=payload)
    book_id = create_resp.json()["_id"]

    response = await client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["_id"] == book_id


async def test_update_book(client):
    payload = {"title": "Old Title", "author": "Author", "year": 2020}
    create_resp = await client.post("/books/", json=payload)
    book_id = create_resp.json()["_id"]

    updated = {"title": "New Title", "author": "Author", "year": 2021}
    response = await client.put(f"/books/{book_id}", json=updated)
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


async def test_delete_book(client):
    payload = {"title": "Delete Me", "author": "Author", "year": 2019}
    create_resp = await client.post("/books/", json=payload)
    book_id = create_resp.json()["_id"]

    del_response = await client.delete(f"/books/{book_id}")
    assert del_response.status_code == 204

    get_response = await client.get(f"/books/{book_id}")
    assert get_response.status_code == 404


async def test_get_nonexistent_book(client):
    response = await client.get("/books/000000000000000000000000")
    assert response.status_code == 404