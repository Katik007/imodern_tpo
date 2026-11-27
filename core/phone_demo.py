"""Видимая демонстрация отказа во входе по телефону."""

from datetime import datetime

from core.browser import browser_session, clean_page
from core.config import ROOT_DIR, settings
from core.reporting import redact
from data.auth_cases import AUTH_CASES
from ui.pages.login_page import LoginPage


def run_phone_demo() -> int:
    if not (settings.phone and settings.password):
        print("Для демонстрации заполните IMODERN_TEST_PHONE и IMODERN_TEST_PASSWORD в .env.")
        return 2

    case = next(case for case in AUTH_CASES if case.case_id == "AUTH-07")
    output = ROOT_DIR / "test-results" / "phone-demo" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    output.mkdir(parents=True)
    try:
        with browser_session(name="chromium", headless=False, slow_mo=700) as browser, clean_page(browser) as page:
            login = LoginPage(page)
            login.open()
            login.form.wait_for(state="visible")
            page.add_style_tag(
                content="input[name='USER_LOGIN'] { -webkit-text-security: disc !important; }"
            )

            print("В поле E-mail вводится телефон. Символы скрыты.", flush=True)
            login.fill_credentials(settings.phone, settings.password)
            login.form.scroll_into_view_if_needed()
            private_fields = login.form.locator("input[name='USER_LOGIN'], input[name='USER_PASSWORD']")
            page.screenshot(path=output / "01-phone-login.png", mask=[private_fields], mask_color="#e3e6ea")

            login.submit()
            login.assert_rejected(case.expected_error)
            page.locator(".login__error").scroll_into_view_if_needed()
            page.screenshot(path=output / "02-login-rejected.png", mask=[private_fields], mask_color="#e3e6ea")
            print(f"iModern отклонил вход по телефону. Скриншоты сохранены в {output}", flush=True)
            # Пауза для зрителя после проверки. Тестовые ожидания завершены.
            page.wait_for_timeout(7000)
    except Exception as error:
        print(redact(f"Демонстрация остановилась: {error}", settings.private_values))
        return 1
    return 0
