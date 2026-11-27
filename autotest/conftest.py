"""Изоляция тестов, загрузка данных и диагностика в Allure."""

import json
from urllib.parse import urlsplit

import allure
import pytest

from core.browser import browser_session, clean_page
from core.config import settings
from core.logging_setup import get_logger
from core.reporting import redact

logger = get_logger(__name__)
failed_result = pytest.StashKey[bool]()


@pytest.fixture(scope="session")
def store_data():
    return json.loads(settings.data_file.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def browser():
    with browser_session(slow_mo=350 if settings.show_steps else 0) as session:
        yield session


@pytest.fixture
def page(browser, request):
    with clean_page(browser) as current:
        if request.node.get_closest_marker("shop"):
            current.route("https://tagmanager.andata.ru/**", lambda route: route.abort())
        if settings.show_steps:
            current.add_init_script("""
                document.addEventListener('DOMContentLoaded', () => {
                    const style = document.createElement('style');
                    style.textContent = `
                        input[name="USER_LOGIN"], input[name="EMAIL"],
                        input[name="PERSONAL_PHONE"], input[name="NAME"] {
                            -webkit-text-security: disc !important;
                        }
                    `;
                    document.head.append(style);
                });
            """)
        yield current
        if settings.show_steps and not current.is_closed():
            last_browser_test = next(
                item for item in reversed(request.session.items) if "page" in item.fixturenames
            )
            # Пауза для зрителя после завершения проверок на странице.
            hold_ms = 8000 if request.node.stash.get(failed_result, False) else 2500
            current.wait_for_timeout(12000 if request.node is last_browser_test else hold_ms)


@pytest.hookimpl(wrapper=True, trylast=True)
def pytest_runtest_makereport(item, call):
    report = yield
    if not report.failed:
        return report

    item.stash[failed_result] = True
    report.longrepr = redact(report.longreprtext, settings.private_values)

    page = item.funcargs.get("page")
    if page is None or page.is_closed():
        allure.attach("Страница браузера недоступна.", name="Причина отсутствия скриншота")
        return report

    url = urlsplit(page.url)
    safe_url = f"{url.scheme}://{url.netloc}{url.path}" if url.netloc else "Страница ещё открывается"
    logger.error("Сбой %s (%s), страница %s", item.name, report.when, safe_url)
    allure.attach(safe_url, name="Адрес страницы без параметров")
    try:
        elements = [page.locator("input:not([type='submit']), textarea")]
        elements.extend(page.get_by_text(value, exact=False) for value in settings.private_values if value)
        screenshot = page.screenshot(full_page=True, mask=elements, timeout=5000)
        allure.attach(screenshot, name="Состояние страницы при сбое", attachment_type=allure.attachment_type.PNG)
    except Exception as exc:
        allure.attach(type(exc).__name__, name="Причина отсутствия скриншота")
        logger.error("Скриншот недоступен (%s)", type(exc).__name__)
    return report
