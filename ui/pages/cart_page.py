"""Проверка позиции, количества и итогов гостевой корзины iModern."""

from playwright.sync_api import expect

from ui.base_page import BasePage, rubles


class CartPage(BasePage):
    path = "/cart/"

    def assert_empty(self):
        expect(self.page.locator(':text-is("Ваша корзина пустая")')).to_be_visible()

    def assert_contents(self, name: str, path: str, price: int) -> int:
        item = self.page.locator(".basket-info")
        expect(item).to_have_count(1)
        expect(item).to_contain_text(name)
        expect(item.locator(f'a[href="{path}"]').first).to_be_attached()
        expect(item.locator(".item-count")).to_have_text("1")
        assert rubles(item.locator(".bitem-prices .price-current").inner_text()) == price
        subtotal = rubles(self.page.locator(".basket-list .basket-sum .number").inner_text())
        total = self.order_total()
        assert subtotal == total == price, "Корзина должна содержать один товар по цене карточки."
        return total

    def order_total(self) -> int:
        row = self.page.locator(".basket-list .basket-discount").filter(has_text="Итого к оплате")
        amount = row.locator(".number")
        expect(amount).to_be_visible()
        return rubles(amount.inner_text())

    def open_checkout(self):
        self.page.wait_for_load_state("domcontentloaded")
        open_form = self.page.locator(".cart-action button.butn")
        expect(open_form).to_have_text("Оформить заказ")
        expect(open_form).to_be_enabled()
        open_form.click()
