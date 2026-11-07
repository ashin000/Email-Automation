"""Playwright learning demo; uses a public test page, not Gmail."""
from playwright.sync_api import sync_playwright


def get_page_heading(page):
    heading = page.locator("h1")
    if heading.count() > 0:
        try:
            text = heading.first.inner_text().strip()
            if text:
                return text
        except Exception:
            pass

    try:
        body_text = page.locator("body").inner_text()
    except Exception:
        return "No heading found"

    lines = [line.strip() for line in body_text.splitlines() if line.strip()]
    return lines[0] if lines else "No heading found"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://example.com", wait_until="domcontentloaded")
        print("Title:", page.title())
        print("Heading:", get_page_heading(page))
        browser.close()


if __name__ == "__main__":
    main()
