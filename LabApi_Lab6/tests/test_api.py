async def test_register(client):
    response = await client.post("/auth/register", json={
        "username": "newuser",
        "password": "password123"
    })
    assert response.status_code == 201


async def test_register_duplicate(client):
    await client.post("/auth/register", json={"username": "dupuser", "password": "pass123"})
    response = await client.post("/auth/register", json={"username": "dupuser", "password": "pass123"})
    assert response.status_code == 400


async def test_login(client):
    await client.post("/auth/register", json={"username": "loginuser", "password": "pass123"})
    response = await client.post("/auth/login", json={"username": "loginuser", "password": "pass123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client):
    await client.post("/auth/register", json={"username": "user2", "password": "correct"})
    response = await client.post("/auth/login", json={"username": "user2", "password": "wrong"})
    assert response.status_code == 401


async def test_refresh_token(client):
    await client.post("/auth/register", json={"username": "refreshuser", "password": "pass123"})
    login_resp = await client.post("/auth/login", json={"username": "refreshuser", "password": "pass123"})
    refresh_token = login_resp.json()["refresh_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_refresh_with_access_token_fails(client):
    await client.post("/auth/register", json={"username": "user3", "password": "pass123"})
    login_resp = await client.post("/auth/login", json={"username": "user3", "password": "pass123"})
    access_token = login_resp.json()["access_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 401


async def test_books_without_token(client):
    response = await client.get("/books/")
    assert response.status_code in (401, 403)


async def test_books_with_invalid_token(client):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = await client.get("/books/", headers=headers)
    assert response.status_code == 401


async def test_create_book(auth_client):
    response = await auth_client.post("/books/", json={
        "title": "Test Book",
        "author": "Author",
        "year": 2024
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Test Book"


async def test_get_books(auth_client):
    response = await auth_client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "next_cursor" in data


async def test_get_book_by_id(auth_client):
    create_resp = await auth_client.post("/books/", json={
        "title": "Find Me", "author": "Author", "year": 2020
    })
    book_id = create_resp.json()["id"]

    response = await auth_client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["id"] == book_id


async def test_update_book(auth_client):
    create_resp = await auth_client.post("/books/", json={
        "title": "Old", "author": "Author", "year": 2020
    })
    book_id = create_resp.json()["id"]

    response = await auth_client.put(f"/books/{book_id}", json={
        "title": "New", "author": "Author", "year": 2021
    })
    assert response.status_code == 200
    assert response.json()["title"] == "New"


async def test_delete_book(auth_client):
    create_resp = await auth_client.post("/books/", json={
        "title": "Delete Me", "author": "Author", "year": 2019
    })
    book_id = create_resp.json()["id"]

    assert (await auth_client.delete(f"/books/{book_id}")).status_code == 204
    assert (await auth_client.get(f"/books/{book_id}")).status_code == 404