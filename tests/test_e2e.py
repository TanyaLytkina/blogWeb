import httpx
from lxml import html

BASE = "http://localhost:8000"


def test_e2e():
    c = httpx.Client(follow_redirects=True)

    c.post(
        f"{BASE}/register",
        data={"email": "e2e@test.ru", "login": "e2e", "password": "1234"},
    )

    c.post(f"{BASE}/create-post", data={"title": "E2E", "content": "ok"})

    r = c.get(BASE)
    assert "E2E" in r.text
    print("✅ E2E passed")
