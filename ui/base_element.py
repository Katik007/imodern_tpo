"""Базовая обёртка над элементами Playwright."""

from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from core.logging_setup import get_logger

logger = get_logger(__name__)


class BaseElement:
    def __init__(self, page: Page, selector: str, name: str | None = None) -> None:
        self.page = page
        self.selector = selector
        self.name = name or selector
        self.locator: Locator = page.locator(selector)

    def first(self) -> Locator:
        return self.locator.first

    def click(self) -> None:
        logger.debug("Клик: %s", self.name)
        self.first().click()

    def fill(self, value: str) -> None:
        logger.debug("Ввод в %s", self.name)
        self.first().fill(value)

    def clear(self) -> None:
        self.first().fill("")

    def text(self) -> str:
        return (self.first().inner_text() or "").strip()

    def is_visible(self) -> bool:
        return self.first().is_visible()

    def wait_visible(self) -> None:
        expect(self.first()).to_be_visible()

    def wait_hidden(self) -> None:
        expect(self.first()).to_be_hidden()

    def check(self) -> None:
        self.first().check()
