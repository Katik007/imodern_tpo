"""Карточка стула с проверкой цены и добавления в корзину."""

import re

from playwright.sync_api import expect

from core.config import settings
from core.logging_setup import get_logger
from ui.base_page import BasePage, rubles

logger = get_logger(__name__)


class ProductPage(BasePage):
    def check_and_add(self, name: str, sku: str, color: str, path: str) -> int:
        expect(self.page).to_have_url(f"{settings.base_url}{path}")
        self.page.wait_for_load_state("domcontentloaded")
        header = self.page.locator("h1")
        expect(header).to_have_text(name)
        expect(header).to_contain_text(color, ignore_case=True)
        expect(self.page.locator(".catalog-element__unic-code span")).to_have_text(sku)
        price_label = self.page.locator(".catalog-element__price")
        price_pattern = re.compile(r"\d+.*(?:₽|руб\.?|р\.)")
        try:
            expect(price_label).to_contain_text(price_pattern)
        except AssertionError:
            logger.warning("Цена не отобразилась, обновляем карточку до добавления товара")
            self.page.reload(wait_until="domcontentloaded")
            expect(self.page).to_have_url(f"{settings.base_url}{path}")
            expect(price_label).to_contain_text(price_pattern)
        price = rubles(price_label.inner_text())
        assert price > 0, "Цена стула должна быть положительной."
        button_selector = f'.add-cart[data-id="{sku}"]'
        button = self.page.locator(button_selector)
        confirmation = self.page.locator(".product-in-cart a.btn_cartt")
        expect(confirmation).to_be_hidden()
        expect(button.locator(".btn-text-pc")).to_have_text("Добавить в корзину", ignore_case=True)
        self.page.wait_for_function(
            """selector => typeof document.querySelector(selector)?.onclick === "function"
                && typeof window.getCarttProductList === "function" """,
            arg=button_selector,
        )
        button.click()
        expect(confirmation).to_be_visible()
        return price

    def open_cart(self):
        self.page.locator(".product-in-cart a.btn_cartt[href='/cart/']").click()
        self.page.wait_for_url(f"{settings.base_url}/cart/", wait_until="commit")
