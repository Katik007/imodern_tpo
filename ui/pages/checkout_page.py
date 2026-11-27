"""Проверки первого экрана оформления iModern."""

import re

from playwright.sync_api import expect

from core.config import settings
from ui.base_page import BasePage


class CheckoutPage(BasePage):
    def assert_first_step(self, name: str, total: int):
        self.page.wait_for_url(f"{settings.base_url}/order/", wait_until="commit")
        expect(self.page.locator("h1")).to_have_text("Оформление заказа", ignore_case=True)
        main = self.page.locator("main")
        expect(main).to_contain_text(name)
        for label in ("Фамилия, Имя", "Номер телефона", "E-mail"):
            expect(main).to_contain_text(label, ignore_case=True)
        expect(main.locator("input:visible").first).to_be_visible()
        next_button = main.locator(':text-matches("^Продолжить оформление$", "i")')
        expect(next_button).to_be_visible()
        expect(main).to_contain_text("условия оферты", ignore_case=True)
        formatted = r"\s*".join(f"{total:,}".split(","))
        expect(main).to_contain_text(re.compile(rf"Итого к оплате:\s*{formatted}\s*₽"))
        captcha = main.locator("iframe[src*='captcha' i], .smart-captcha, .g-recaptcha, .h-captcha")
        expect(captcha).to_have_count(0)
