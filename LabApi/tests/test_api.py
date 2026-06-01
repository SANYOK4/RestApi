async def test_cursor_pagination(client):
    # Спочатку додаємо книги щоб було що пагінувати
    for i in range(5):
        await client.post("/books/", json={"title": f"Book {i}", "author": "Author", "year": 2020})

    response = await client.get("/books/", params={"limit": 2})
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "next_cursor" in data
    assert "limit" in data
    assert data["limit"] == 2
    assert len(data["items"]) == 2

    last_id = data["items"][-1]["id"]
    assert data["next_cursor"] == last_id

    # Наступна сторінка
    response2 = await client.get("/books/", params={"limit": 2, "cursor": last_id})
    assert response2.status_code == 200
    data2 = response2.json()

    for book in data2["items"]:
        assert book["id"] > last_id


async def test_last_page_has_no_next_cursor(client):
    response = await client.get("/books/", params={"limit": 100})
    assert response.status_code == 200
    data = response.json()
    assert data["next_cursor"] is None


async def test_cursor_beyond_last_id(client):
    response = await client.get("/books/", params={"cursor": 999999999})
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["next_cursor"] is None


async def test_create_book(client):
    payload = {"title": "Test Book", "author": "Author", "year": 2024}
    response = await client.post("/books/", json=payload)
    assert response.status_code == 201
    book = response.json()
    assert book["title"] == "Test Book"
    assert book["id"] is not None


async def test_get_book_by_id(client):
    payload = {"title": "Find Me", "author": "Author", "year": 2020}
    create_resp = await client.post("/books/", json=payload)
    book_id = create_resp.json()["id"]

    response = await client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["id"] == book_id


async def test_update_book(client):
    payload = {"title": "Old Title", "author": "Author", "year": 2020}
    create_resp = await client.post("/books/", json=payload)
    book_id = create_resp.json()["id"]

    updated = {"title": "New Title", "author": "Author", "year": 2021}
    response = await client.put(f"/books/{book_id}", json=updated)
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


async def test_delete_book(client):
    payload = {"title": "Delete Me", "author": "Author", "year": 2019}
    create_resp = await client.post("/books/", json=payload)
    book_id = create_resp.json()["id"]

    del_response = await client.delete(f"/books/{book_id}")
    assert del_response.status_code == 204

    get_response = await client.get(f"/books/{book_id}")
    assert get_response.status_code == 404


async def test_get_nonexistent_book(client):
    response = await client.get("/books/999999999")
    assert response.status_code == 404