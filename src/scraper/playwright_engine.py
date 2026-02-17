from playwright.sync_api import sync_playwright

def fetch_rendered_html(url: str, timeout_ms: int = 30000) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=timeout_ms, wait_until="networkidle")
        html = page.content()
        browser.close()
        return html