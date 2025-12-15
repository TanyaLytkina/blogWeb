import pytest

from blog_app.models import PostCreate, UserCreate


def test_user_create():
    u = UserCreate(email="a@b.com", login="test", password="1234")
    assert u.login == "test"


def test_user_invalid_email():
    with pytest.raises(ValueError):
        UserCreate(email="bad", login="t", password="p")


def test_post_create():
    p = PostCreate(authorId=1, title="t", content="c")
    assert "c" in p.content
