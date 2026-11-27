"""Поиск модели из каталога стульев iModern."""

from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect

from ui.base_element import BaseElement
from ui.base_page import BasePage


class SearchPage(BasePage):
    def __init__(self, page, catalog_path: str):
        super().__init__(page)
        self.path = catalog_path

    def assert_catalog(self, title: str):
        expect(self.page.locator("h1")).to_have_text(title, ignore_case=True)

    def find_and_open(self, query: str, name: str, product_path: str):
        search = BaseElement(self.page, ".header-search:visible input[type='search'][name='q']", "Поиск")
        search.fill(query)
        search.locator.press("Enter")
        self.page.wait_for_url("**/search/**", wait_until="commit")
        assert parse_qs(urlsplit(self.page.url).query).get("q") == [query], "Изменился поисковый запрос."
        expect(self.page.locator("h1")).to_have_text("Поиск", ignore_case=True)
        result = self.page.locator(".catalog-item").filter(
            has=self.page.locator(f'a.catalog-item__link[href="{product_path}"]')
        )
        expect(result).to_have_count(1)
        expect(result).to_contain_text(name)
        result.locator("a.catalog-item__link").click()
