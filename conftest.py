import os

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


@pytest.fixture
def driver():
    """Khoi tao Firefox cho moi test; dat HEADLESS=1 de chay khong giao dien."""
    opts = Options()
    if os.getenv("HEADLESS") == "1":
        opts.add_argument("-headless")
    opts.add_argument("--width=1920")
    opts.add_argument("--height=1080")
    opts.set_preference("signon.rememberSignons", False)
    opts.set_preference("signon.autofillForms", False)
    opts.set_preference("signon.management.page.breach-alerts.enabled", False)
    d = webdriver.Firefox(options=opts)
    yield d
    d.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Tu dong chup anh man hinh khi test that bai."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        d = item.funcargs.get("driver")
        if d:
            os.makedirs("screenshots", exist_ok=True)
            d.save_screenshot(f"screenshots/{item.name}.png")
