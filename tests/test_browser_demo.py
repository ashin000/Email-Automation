import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.browser_demo import get_page_heading


class FakeLocator:
    def __init__(self, text):
        self.text = text

    def count(self):
        return 1 if self.text else 0

    def inner_text(self):
        return self.text


class FakePage:
    def __init__(self, h1_text="", body_text="Example Domain"):
        self.h1_text = h1_text
        self.body_text = body_text

    def locator(self, selector):
        if selector == "h1":
            return FakeLocator(self.h1_text)
        if selector == "body":
            return FakeLocator(self.body_text)
        return FakeLocator("")


def test_get_page_heading_uses_body_when_h1_is_missing():
    page = FakePage(h1_text="", body_text="Example Domain")

    assert get_page_heading(page) == "Example Domain"
