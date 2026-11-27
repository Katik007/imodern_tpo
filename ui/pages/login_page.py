"""Авторизация через защищённую страницу профиля iModern."""

import re

from playwright.sync_api import expect

from core.config import settings
from ui.base_element import BaseElement
from ui.base_page import BasePage


class LoginPage(BasePage):
    path = "/personal/profile/"
    form_selector = "form.form-popup--auth"

    @property
    def form(self):
        return self.page.locator(self.form_selector)

    def sign_in(self, identifier: str, password: str):
        self.open()
        self.fill_credentials(identifier, password)
        self.submit()

    def fill_credentials(self, identifier: str, password: str):
        user = BaseElement(self.page, f"{self.form_selector} input[name='USER_LOGIN']", "Email")
        secret = BaseElement(self.page, f"{self.form_selector} input[name='USER_PASSWORD']", "Пароль")
        user.fill(identifier)
        secret.fill(password)

    def submit(self):
        self.form.locator("input[type='submit']").click()

    def assert_account(self, name: str):
        expect(self.page).to_have_url(f"{settings.base_url}{self.path}")
        expect(self.page.locator("h1")).to_have_text("Профиль")
        expect(self.form).to_have_count(0)
        expect(self.page.locator("input[name='NAME']").first).to_have_value(name)
        expect(self.page.locator("input[name='EMAIL']")).to_have_value(settings.email)
        if settings.phone:
            phone = self.page.locator("input[name='PERSONAL_PHONE']")
            expect(phone).not_to_have_value("")
            actual = re.sub(r"\D", "", phone.input_value())
            expected = re.sub(r"\D", "", settings.phone)
            assert actual == expected, "Телефон в профиле отличается."

    def assert_rejected(self, reason: str):
        expect(self.page).to_have_url(f"{settings.base_url}{self.path}")
        expect(self.form).to_be_visible()
        expect(self.page.locator("h1")).to_have_text("Авторизация")
        expect(self.page.locator("input[name='PERSONAL_PHONE']")).to_have_count(0)
        if reason in {"required_email", "required_password"}:
            field = "USER_LOGIN" if reason == "required_email" else "USER_PASSWORD"
            invalid = self.form.locator(f"input[name='{field}']:required:invalid:focus")
            expect(invalid).to_be_visible()
            assert invalid.evaluate("element => element.validity.valueMissing && Boolean(element.validationMessage)")
            expect(self.page.locator(".login__error")).to_have_count(0)
        elif reason == "email_format":
            error = self.page.locator(".login__error")
            expect(error).to_be_visible()
            message = error.inner_text().strip()
            assert re.search(r"формат|корректн\w*\s+(?:email|e-mail|адрес)", message, re.IGNORECASE), (
                f"Ожидалась подсказка о формате email. Сайт показал «{message}»."
            )
        else:
            expect(self.page.locator(".login__error")).to_have_text("Неверный логин или пароль")
