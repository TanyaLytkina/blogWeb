from fastapi.testclient import TestClient

from blog_app.main import app

client = TestClient(app)


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200


def test_login_page():
    response = client.get("/login")
    assert response.status_code == 200
