"""Авторизация на сайте iModern."""

import allure
import pytest

from core.config import settings
from core.logging_setup import get_logger
from data.auth_cases import AUTH_CASES
from ui.pages.login_page import LoginPage

logger = get_logger(__name__)


@allure.epic("iModern")
@allure.feature("Авторизация")
@pytest.mark.auth
@pytest.mark.parametrize("case", AUTH_CASES, ids=lambda case: case.case_id)
def test_authorization(page, case):
    allure.dynamic.id(case.case_id)
    allure.dynamic.title(f"{case.case_id} · {case.title}")
    allure.dynamic.parameter("case", case.case_id)
    allure.dynamic.parameter("Вид идентификатора", case.identifier_kind)
    allure.dynamic.parameter("Данные идентификатора", case.identifier_data)
    allure.dynamic.parameter("Данные пароля", case.password_data)
    expected = {
        None: "Сессия ожидаемого пользователя",
        "required_email": "Браузер указывает на пустой email",
        "required_password": "Браузер указывает на пустой пароль",
        "rejected": "Неверный логин или пароль",
        "email_format": "Сообщение указывает на неверный формат email",
    }
    allure.dynamic.parameter("Ожидание", expected[case.expected_error])
    logger.info("%s · %s", case.case_id, case.title)

    sample_password = "SampleValid-9!"
    identifier = {
        "existing": settings.phone if case.identifier_kind == "phone" else settings.email,
        "empty": "",
        "invalid_email": "invalid@",
        "unknown": "qa-imodern@example.com",
    }[case.identifier_data]
    password = {
        "correct": settings.password,
        "empty": "",
        "sample": sample_password,
        "wrong": "Incorrect-Login-9!",
    }[case.password_data]
    if case.identifier_data == "existing" and not identifier:
        pytest.skip("Укажите идентификатор тестового аккаунта в локальном .env.")
    if case.password_data == "correct" and not password:
        pytest.skip("Укажите пароль тестового аккаунта в локальном .env.")
    if not case.expected_error and not settings.account_name:
        pytest.skip("Укажите имя владельца тестового аккаунта в локальном .env.")

    login = LoginPage(page)
    with allure.step("Заполнить и отправить форму входа"):
        login.sign_in(identifier, password)
    if case.expected_error:
        with allure.step("Проверить сообщение об ошибке и отсутствие авторизованной сессии"):
            login.assert_rejected(case.expected_error)
            if case.case_id == "AUTH-07":
                masked_fields = login.form.locator("input[type='text'], input[type='password']")
                allure.attach(
                    page.screenshot(mask=[masked_fields], mask_color="#e3e6ea"),
                    name="Ответ сайта на вход по телефону",
                    attachment_type=allure.attachment_type.PNG,
                )
    else:
        with allure.step("Проверить переход и сессию ожидаемого пользователя"):
            login.assert_account(settings.account_name)
