"""Подготовка заказа на публичном сайте и статус полного E2E."""

import allure
import pytest

from ui.pages.cart_page import CartPage
from ui.pages.checkout_page import CheckoutPage
from ui.pages.product_page import ProductPage
from ui.pages.search_page import SearchPage


@allure.epic("iModern")
@allure.feature("Покупка")
@allure.id("SHOP-01")
@allure.title("SHOP-01 · Поиск → карточка стула → корзина → форма заказа")
@pytest.mark.shop
def test_prepare_order(page, store_data):
    sku = store_data["sku"]
    name = store_data["name"]
    color = store_data["color"]
    allure.dynamic.parameter("Товар", name)
    allure.dynamic.parameter("Артикул", sku)
    allure.dynamic.parameter("Вариант", color)

    cart = CartPage(page)
    with allure.step("Убедиться, что новая гостевая корзина пуста"):
        cart.open()
        cart.assert_empty()
    with allure.step("Открыть каталог стульев, найти модель в поиске и открыть карточку"):
        search = SearchPage(page, store_data["catalog_path"])
        search.open()
        search.assert_catalog(store_data["catalog_title"])
        search.find_and_open(store_data["query"], name, store_data["product_path"])
    product = ProductPage(page)
    with allure.step("Проверить карточку, вариант и цену, добавить товар"):
        price = product.check_and_add(name, sku, color, store_data["product_path"])
    with allure.step("Сверить позицию, количество, цену и итог корзины"):
        product.open_cart()
        total = cart.assert_contents(name, store_data["product_path"], price)
        allure.attach(f"{total} ₽", name="Итог корзины", attachment_type=allure.attachment_type.TEXT)
    with allure.step("Открыть первый экран оформления, проверить контакты, итог и условия оферты"):
        cart.open_checkout()
        CheckoutPage(page).assert_first_step(name, total)


@allure.epic("iModern")
@allure.feature("Покупка")
@allure.id("E2E-01")
@allure.title("E2E-01 · Создание заказа и проверка номера")
@pytest.mark.e2e
def test_submit_and_verify_order():
    pytest.skip("Публичная форма передаёт реальный заказ продавцу. Требуется тестовый режим iModern.")
