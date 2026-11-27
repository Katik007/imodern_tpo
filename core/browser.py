"""Браузер Playwright и отдельный контекст для каждого теста."""

from contextlib import contextmanager

from playwright.sync_api import expect, sync_playwright

from core.config import settings
from core.logging_setup import get_logger

logger = get_logger(__name__)


@contextmanager
def browser_session(*, name: str | None = None, headless: bool | None = None, slow_mo: int = 0):
    name = name or settings.browser
    headless = settings.headless if headless is None else headless
    logger.info("Запуск %s, headless=%s", name, headless)
    expect.set_options(timeout=settings.default_timeout_ms)
    with sync_playwright() as playwright:
        browser_type = getattr(playwright, name)
        browser = browser_type.launch(headless=headless, slow_mo=slow_mo)
        try:
            yield browser
        finally:
            browser.close()
            logger.info("Браузер закрыт")


@contextmanager
def clean_page(browser):
    context = browser.new_context(
        base_url=settings.base_url,
        viewport={"width": 1440, "height": 900},
        locale="ru-RU",
    )
    context.set_default_timeout(settings.default_timeout_ms)
    context.set_default_navigation_timeout(settings.default_timeout_ms)
    try:
        yield context.new_page()
    finally:
        context.close()
