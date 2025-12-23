from playwright.sync_api import sync_playwright, expect

def test_guest_home_to_register_login_create_post():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("http://localhost:8000/")
        expect(page.locator("h2")).to_have_text("Список постиков")
        expect(page.locator(".card-title").first).to_be_visible()

        page.close()
        browser.close()
