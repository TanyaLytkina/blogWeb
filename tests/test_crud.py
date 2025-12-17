import pytest

from blog_app import crud
from blog_app.models import PostCreate, UserCreate


@pytest.fixture
def init_db():
    conn = crud.get_db()
    conn.execute("DELETE FROM posts")
    conn.execute("DELETE FROM users")
    conn.commit()
    conn.close()


def test_create_get_user(init_db):
    user = crud.create_user(
        UserCreate(email="test@test.com", login="test", password="123")
    )
    fetched = crud.get_user(user.id)
    assert fetched.login == "test"
    assert fetched.email == "test@test.com"


def test_create_get_post(init_db):
    user = crud.create_user(
        UserCreate(email="admin@test.com", login="admin", password="123")
    )
    post = crud.create_post(
        PostCreate(authorId=user.id, title="Test Post", content="Test content")
    )
    fetched = crud.get_post(post.id)
    assert fetched.title == "Test Post"
    assert fetched.content == "Test content"


def test_search_posts(init_db):
    user = crud.create_user(
        UserCreate(email="admin@test.com", login="admin", password="123")
    )
    crud.create_post(
        PostCreate(authorId=user.id, title="Python Test", content="Python rocks")
    )
    results = crud.search_posts("Python")
    assert len(results) == 1
    assert "Python" in results[0].title
