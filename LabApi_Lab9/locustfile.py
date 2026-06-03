from locust import HttpUser, task, between
import json


class LibraryUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        """Виконується при старті кожного юзера — логінимось і отримуємо токен"""
        response = self.client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpass123"},
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    @task
    def get_books(self):
        """Навантажувальний тест ендпоінту GET /books/"""
        self.client.get("/books/", headers=self.headers)