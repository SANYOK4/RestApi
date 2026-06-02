import json


def test_pagination(client):
    # Додаємо 5 книг
    for i in range(5):
        client.post("/books/", json={"title": f"Book {i}", "author": "Author", "year": 2020})

    # Перша сторінка
    response = client.get("/books/?limit=2&offset=0")
    assert response.status_code == 200
    data = response.get_json()

    assert "items" in data
    assert "total" in data
    assert data["total"] == 5
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert len(data["items"]) == 2

    # Друга сторінка
    response2 = client.get("/books/?limit=2&offset=2")
    data2 = response2.get_json()
    assert len(data2["items"]) == 2

    # Остання сторінка
    response3 = client.get("/books/?limit=2&offset=4")
    data3 = response3.get_json()
    assert len(data3["items"]) == 1


def test_offset_beyond_total(client):
    response = client.get("/books/?limit=10&offset=9999")
    assert response.status_code == 200
    data = response.get_json()
    assert data["items"] == []


def test_create_book(client):
    payload = {"title": "Test Book", "author": "Author", "year": 2024}
    response = client.post("/books/", json=payload)
    assert response.status_code == 201
    book = response.get_json()
    assert book["title"] == "Test Book"
    assert book["id"] is not None


def test_get_book_by_id(client):
    payload = {"title": "Find Me", "author": "Author", "year": 2020}
    create_resp = client.post("/books/", json=payload)
    book_id = create_resp.get_json()["id"]

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.get_json()["id"] == book_id


def test_update_book(client):
    payload = {"title": "Old Title", "author": "Author", "year": 2020}
    create_resp = client.post("/books/", json=payload)
    book_id = create_resp.get_json()["id"]

    updated = {"title": "New Title", "author": "Author", "year": 2021}
    response = client.put(f"/books/{book_id}", json=updated)
    assert response.status_code == 200
    assert response.get_json()["title"] == "New Title"


def test_delete_book(client):
    payload = {"title": "Delete Me", "author": "Author", "year": 2019}
    create_resp = client.post("/books/", json=payload)
    book_id = create_resp.get_json()["id"]

    del_response = client.delete(f"/books/{book_id}")
    assert del_response.status_code == 204

    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 404


def test_get_nonexistent_book(client):
    response = client.get("/books/999999999")
    assert response.status_code == 404


def test_swagger_ui(client):
    response = client.get("/docs/")
    assert response.status_code == 200


def test_swagger_spec(client):
    response = client.get("/apispec.json")
    assert response.status_code == 200
    spec = response.get_json()
    assert "paths" in spec
    assert "/books/" in spec["paths"]