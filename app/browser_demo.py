"""Playwright learning demo; uses a public test page, not Gmail."""
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://example.com", wait_until="domcontentloaded")
        print("Title:", page.title())
        print("Heading:", page.locator("h1").inner_text())
        browser.close()

if __name__ == "__main__":
    main()
