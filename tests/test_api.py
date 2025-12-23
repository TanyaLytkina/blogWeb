import json
from fastapi.testclient import TestClient
from blog_app.main import app

client = TestClient(app)

def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Список постиков" in response.content.decode("utf-8")


def test_register_success():
    response = client.post("/register", data={
        "email": "test@example.com",
        "login": "testuser",
        "password": "1234"
    })
    assert response.status_code == 200
    assert response.headers["location"] == "/"

def test_register_duplicate_login():
    client.post("/register", data={
        "email": "test1@example.com",
        "login": "testuser",
        "password": "1234"
    })
    response = client.post("/register", data={
        "email": "test2@example.com",
        "login": "testuser",
        "password": "1234"
    })
    assert response.status_code == 200
    assert "ошибка" in response.text.lower()


def test_login_success():
    client.post("/register", data={
        "email": "login@example.com",
        "login": "loginuser",
        "password": "1234"
    })
    response = client.post("/login", data={
        "login": "loginuser",
        "password": "1234"
    })
    assert response.status_code == 200

def test_create_post():
    # Регистрация
    client.post("/register", data={
        "email": "post@example.com",
        "login": "postuser",
        "password": "1234"
    })
    client.post("/login", data={"login": "postuser", "password": "1234"})

    # Создание поста
    response = client.post("/create-post", data={
        "title": "Test Post",
        "content": "Test content"
    })
    assert response.status_code == 303
