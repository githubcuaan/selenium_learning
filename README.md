# Testing w Selenium

Automated E2E test suite for the demo e-commerce site **https://www.saucedemo.com**, built with Selenium WebDriver + pytest + Firefox.

---

## 1. Overview

| Item               | Value                                                                           |
| ------------------ | ------------------------------------------------------------------------------- |
| Target system      | https://www.saucedemo.com                                                       |
| Scope              | Login, product sorting, cart, checkout, logout                                  |
| Test framework     | pytest 9.1.1                                                                    |
| Browser automation | Selenium WebDriver 4.51.0 (Selenium Manager resolves geckodriver automatically) |
| Browser            | Mozilla Firefox 157.0.1                                                         |
| Language / runtime | Python 3.12.12                                                                  |
| Reports            | pytest-html (optional), screenshot on failure                                   |
| Suite result       | **10 passed**, 0 failed (headless and visible-browser runs)                     |
| Execution date     | 2026-10-23                                                                      |

---

## 2. Project structure

```
lap9_selenium/
├── conftest.py            # Firefox driver fixture + failure screenshot hook
├── saucedemo_test.py      # Page helpers + 9 test cases (TC01–TC09)
├── pyrightconfig.json     # Points Pyright at .venv for import resolution
├── requirements.txt       # selenium, pytest, pytest-html
├── screenshots/           # created on failure only
└── README.md
```

### Key helpers (`saucedemo_test.py`)

| Helper                                    | Purpose                                                                        |
| ----------------------------------------- | ------------------------------------------------------------------------------ |
| `wait_for(driver, condition, timeout=10)` | Generic `WebDriverWait` wrapper, returns condition's value with correct typing |
| `login(driver, username, password)`       | Opens `BASE_URL`, fills credentials, submits                                   |
| `login_ok(driver)`                        | `login()` with valid account + waits for `/inventory`                          |
| `error_message(driver)`                   | Waits for `[data-test=error]` and returns its text                             |

### Fixture (`conftest.py`)

- Creates a Firefox session per test, quits it after.
- `HEADLESS=1` → `-headless` mode.
- Fixed window `1920x1080`.
- Password-manager / breach-alert prefs disabled to avoid native popups.
- `pytest_runtest_makereport` hook saves `screenshots/<test_name>.png` when a test fails.

---

## 3. Test cases

| ID    | Test                                                                | Type          | Steps (summary)                                          | Expected result                                                           | Status |
| ----- | ------------------------------------------------------------------- | ------------- | -------------------------------------------------------- | ------------------------------------------------------------------------- | ------ |
| TC01  | `test_tc01_login_success`                                           | Positive      | Login with `standard_user` / `secret_sauce`              | Redirected to `/inventory.html`, title shows `Products`                   | PASS   |
| TC02  | `test_tc02_login_wrong_password`                                    | Negative      | Login with valid user + wrong password                   | Error contains "do not match", still on login page                        | PASS   |
| TC03  | `test_tc03_login_locked_out_user`                                   | Negative      | Login with `locked_out_user`                             | Error contains "locked out"                                               | PASS   |
| TC04a | `test_tc04_login_empty_fields[-secret_sauce-Username is required]`  | Validation    | Login with empty username                                | Error "Username is required"                                              | PASS   |
| TC04b | `test_tc04_login_empty_fields[standard_user--Password is required]` | Validation    | Login with empty password                                | Error "Password is required"                                              | PASS   |
| TC05  | `test_tc05_sort_price_low_to_high`                                  | Functional    | Login → sort dropdown → `Price (low to high)`            | Price list is non-empty and ascending                                     | PASS   |
| TC06  | `test_tc06_add_to_cart`                                             | Functional    | Login → add Backpack → open cart                         | Badge = `1`; cart contains `Sauce Labs Backpack`                          | PASS   |
| TC07  | `test_tc07_remove_from_cart`                                        | Functional    | Login → add Bike Light → cart → remove                   | Cart item list empty, badge gone                                          | PASS   |
| TC08  | `test_tc08_checkout_complete`                                       | E2E flow      | Login → add item → cart → checkout → fill info → finish  | Confirmation header = "Thank you for your order!"                         | PASS   |
| TC09  | `test_tc09_logout`                                                  | Security/flow | Login → burger menu → logout → revisit `/inventory.html` | URL back to login page; direct inventory access blocked with access error | PASS   |

**Coverage:** 1 E2E purchase flow, 3 login scenarios, 2 field-validation scenarios, 1 sorting, 2 cart operations, 1 logout/access-control scenario.

---

## 4. How to run

```bash
# setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# full suite, headless
HEADLESS=1 pytest -q

# full suite with visible browser
pytest -q

# single test
HEADLESS=1 pytest saucedemo_test.py::test_tc01_login_success -q

# HTML report
HEADLESS=1 pytest --html=report.html --self-contained-html
```

Failure screenshots are written to `screenshots/`. `pyright` uses `pyrightconfig.json` (`venvPath: .`, `venv: .venv`) so third-party imports resolve.

---

## 5. Latest runs

### 5.1 Headless run

```
$ HEADLESS=1 pytest -q
..........                                                               [100%]
10 passed in 52.41s
```

### 5.2 Visible-browser run (Firefox UI)

```
$ pytest -v
platform linux -- Python 3.12.12, pytest-9.1.1, pluggy-1.7.0
plugins: html-4.2.0, metadata-3.1.1
collected 10 items

saucedemo_test.py::test_tc01_login_success PASSED                        [ 10%]
saucedemo_test.py::test_tc02_login_wrong_password PASSED                 [ 20%]
saucedemo_test.py::test_tc03_login_locked_out_user PASSED                [ 30%]
saucedemo_test.py::test_tc04_login_empty_fields[-secret_sauce-Username is required] PASSED   [ 40%]
saucedemo_test.py::test_tc04_login_empty_fields[standard_user--Password is required] PASSED  [ 50%]
saucedemo_test.py::test_tc05_sort_price_low_to_high PASSED               [ 60%]
saucedemo_test.py::test_tc06_add_to_cart PASSED                          [ 70%]
saucedemo_test.py::test_tc07_remove_from_cart PASSED                     [ 80%]
saucedemo_test.py::test_tc08_checkout_complete PASSED                    [ 90%]
saucedemo_test.py::test_tc09_logout PASSED                               [100%]

10 passed in 112.86s (0:01:52)
```

| Run mode        | Command                | Result    | Duration |
| --------------- | ---------------------- | --------- | -------- |
| Headless        | `HEADLESS=1 pytest -q` | 10 passed | 52.41 s  |
| Visible browser | `pytest -v`            | 10 passed | 112.86 s |

Visible browser is slower (real window rendering, no headless shortcut) but is the mode to use when visually verifying a flow or capturing failure screenshots.

### 5.3 Failure evidence (screenshots)

The `pytest_runtest_makereport` hook in `conftest.py` captures a screenshot automatically for every failed test, in either run mode:

```python
if report.when == "call" and report.failed:
    d = item.funcargs.get("driver")
    if d:
        os.makedirs("screenshots", exist_ok=True)
        d.save_screenshot(f"screenshots/{item.name}.png")
```

- Output path: `screenshots/<test_name>.png`, created only on failure.
- No screenshots are produced for passing tests, so an empty/absent folder means the suite is green.
- Works headless too — screenshots are captured from the virtual display buffer.

Static check:

```
$ pyright conftest.py saucedemo_test.py
0 errors, 0 warnings, 0 informations
```

---

## 6. Issues found and fixes applied during this lab

| Issue                              | Symptom                                                                  | Fix                                                                                                                             |
| ---------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| No `driver` fixture                | `fixture 'driver' not found` at setup for every test                     | Added `conftest.py` with a scoped Firefox fixture                                                                               |
| Browser choice                     | Suite was written against Chrome                                         | Switched to Firefox `Options` (`-headless`, `--width/--height`, `set_preference`)                                               |
| Password locator wrong             | `NoSuchElementException: [id="pass"]`                                    | Changed locator to `By.ID, "password"` (actual saucedemo id)                                                                    |
| `wait_for` returned `None`         | Pyright: `Cannot access attribute "text" for class "None"`               | Added `return` and generic `TypeVar` typing mirroring `WebDriverWait.until` (`Callable[[WebDriver], Literal[False] \| T] -> T`) |
| Pyright could not resolve `pytest` | `Import "pytest" could not be resolved` (global Pyright ignored `.venv`) | Added `pyrightconfig.json` with `venvPath`/`venv`                                                                               |

---

## 7. Notes and limitations

- Tests hit the live public demo site, so results depend on network latency; timeouts are 10 s.
- State is not shared between tests — each test logs in from a fresh browser session.
- Only Firefox is configured; Chrome/Edge would need a second fixture or a browser matrix.
- No CI pipeline yet; running headless (`HEADLESS=1`) is CI-ready.
- Suggested next steps: parameterize browser via env var, add marker-based grouping (login/cart/checkout), attach `report.html` as a CI artifact.
