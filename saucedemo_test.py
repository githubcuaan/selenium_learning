"""
Automated testing for https://www.saucedemo.com
features: login, products, cart, checkout, logout
"""

from collections.abc import Callable
from typing import Literal, TypeVar

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = "https://www.saucedemo.com"
VALID_USER = "standard_user"
VALID_PASS = "secret_sauce"


# --- utils ---
_T = TypeVar("_T")


def wait_for(
    driver: WebDriver,
    condition: Callable[[WebDriver], Literal[False] | _T],
    timeout: float = 10,
) -> _T:
    return WebDriverWait(driver, timeout).until(condition)


def login(driver: WebDriver, username, password):
    driver.get(BASE_URL)
    driver.find_element(By.ID, "user-name").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()


def login_ok(driver):
    login(driver, VALID_USER, VALID_PASS)
    wait_for(driver, EC.url_contains("inventory"))


def error_message(driver):
    return wait_for(
        driver, EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-test=error]"))
    ).text


# ------------------------- TC01 - TC04: Dang nhap -------------------------
def test_tc01_login_success(driver):
    """TC01: Dang nhap thanh cong voi tai khoan hop le."""
    login_ok(driver)
    assert driver.current_url.endswith("/inventory.html")
    assert (
        driver.find_element(By.CSS_SELECTOR, "[data-test='title']").text == "Products"
    )


def test_tc02_login_wrong_password(driver):
    """TC02: Dang nhap that bai khi sai mat khau."""
    login(driver, VALID_USER, "sai_mat_khau")
    assert "do not match" in error_message(driver)
    assert "inventory" not in driver.current_url


def test_tc03_login_locked_out_user(driver):
    """TC03: Tai khoan bi khoa khong the dang nhap."""
    login(driver, "locked_out_user", VALID_PASS)
    assert "locked out" in error_message(driver)


@pytest.mark.parametrize(
    "user, pwd, expected",
    [
        ("", VALID_PASS, "Username is required"),
        (VALID_USER, "", "Password is required"),
    ],
)
def test_tc04_login_empty_fields(driver, user, pwd, expected):
    """TC04: De trong username hoac password phai bao loi tuong ung."""
    login(driver, user, pwd)
    assert expected in error_message(driver)


# ------------------------- TC05: Sap xep / tim san pham -------------------------
def test_tc05_sort_price_low_to_high(driver):
    """TC05: Sap xep san pham theo gia tang dan."""
    login_ok(driver)
    Select(
        driver.find_element(By.CSS_SELECTOR, "[data-test='product-sort-container']")
    ).select_by_value("lohi")
    prices = [
        float(e.text.replace("$", ""))
        for e in driver.find_elements(By.CSS_SELECTOR, ".inventory_item_price")
    ]
    assert len(prices) > 1
    assert prices == sorted(prices)


# ------------------------- TC06 - TC07: Gio hang -------------------------
def test_tc06_add_to_cart(driver):
    """TC06: Them san pham vao gio hang, badge hien 1 va san pham co trong gio."""
    login_ok(driver)
    driver.find_element(
        By.CSS_SELECTOR, "[data-test='add-to-cart-sauce-labs-backpack']"
    ).click()

    badge = wait_for(
        driver, EC.visibility_of_element_located((By.CLASS_NAME, "shopping_cart_badge"))
    )
    assert badge.text == "1"

    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait_for(driver, EC.url_contains("cart"))
    names = [e.text for e in driver.find_elements(By.CLASS_NAME, "inventory_item_name")]
    assert names == ["Sauce Labs Backpack"]


def test_tc07_remove_from_cart(driver):
    """TC07: Xoa san pham khoi gio hang, gio hang tro thanh rong."""
    login_ok(driver)
    driver.find_element(
        By.CSS_SELECTOR, "[data-test='add-to-cart-sauce-labs-bike-light']"
    ).click()
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait_for(driver, EC.url_contains("cart"))

    driver.find_element(
        By.CSS_SELECTOR, "[data-test='remove-sauce-labs-bike-light']"
    ).click()
    assert driver.find_elements(By.CLASS_NAME, "cart_item") == []
    assert driver.find_elements(By.CLASS_NAME, "shopping_cart_badge") == []


# ------------------------- TC08: Thanh toan -------------------------
def test_tc08_checkout_complete(driver):
    """TC08: Luong mua hang tron ven tu them san pham den hoan tat don."""
    login_ok(driver)
    driver.find_element(
        By.CSS_SELECTOR, "[data-test='add-to-cart-sauce-labs-backpack']"
    ).click()
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    driver.find_element(By.CSS_SELECTOR, "[data-test='checkout']").click()

    wait_for(driver, EC.visibility_of_element_located((By.ID, "first-name"))).send_keys(
        "An"
    )
    driver.find_element(By.ID, "last-name").send_keys("Nguyen")
    driver.find_element(By.ID, "postal-code").send_keys("100000")
    driver.find_element(By.ID, "continue").click()

    wait_for(driver, EC.url_contains("checkout-step-two"))
    driver.find_element(By.ID, "finish").click()

    header = wait_for(
        driver, EC.visibility_of_element_located((By.CLASS_NAME, "complete-header"))
    )
    assert header.text == "Thank you for your order!"


# ------------------------- TC09: Dang xuat -------------------------
def test_tc09_logout(driver):
    """TC09: Dang xuat quay ve trang dang nhap; vao lai /inventory bi chan."""
    login_ok(driver)
    driver.find_element(By.ID, "react-burger-menu-btn").click()
    wait_for(driver, EC.element_to_be_clickable((By.ID, "logout_sidebar_link"))).click()

    wait_for(driver, EC.visibility_of_element_located((By.ID, "login-button")))
    assert driver.current_url.rstrip("/") == BASE_URL

    driver.get(f"{BASE_URL}/inventory.html")
    assert "only access '/inventory.html' when you are logged in" in error_message(
        driver
    )
