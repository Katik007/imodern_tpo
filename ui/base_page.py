"""Общая навигация и формат цен iModern."""

import re

from playwright.sync_api import TimeoutError as PlaywrightTimeout

from core.config import settings
from core.logging_setup import get_logger

logger = get_logger(__name__)


def rubles(text: str) -> int:
    values = re.findall(r"(\d[\d \u00a0\u202f]*)\s*(?:₽|руб\.?|р\.)", text)
    assert len(values) == 1, "Ожидалась одна цена в рублях."
    return int(re.sub(r"\s", "", values[0]))


class BasePage:
    path = "/"

    def __init__(self, page):
        self.page = page

    def open(self):
        logger.info("Открытие страницы %s", self.path)
        try:
            response = self.page.goto(self.path, wait_until="commit")
        except PlaywrightTimeout:
            logger.warning("Страница %s не ответила вовремя, повторяем открытие", self.path)
            response = self.page.goto(self.path, wait_until="commit")
        assert response is not None and response.ok, "Страница iModern недоступна."
        assert response.url.startswith(f"{settings.base_url}/"), "Страница переадресована за пределы iModern."
