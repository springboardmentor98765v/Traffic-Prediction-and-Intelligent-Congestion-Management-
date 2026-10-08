"""Milestone 4 Days 4-6 — Selenium UI tests on the live frontend (cross-browser, responsive).

What a user actually does, in a real browser, against the deployed site:

    U1  Every page at desktop / tablet / mobile: loads, no horizontal scroll, has a
        viewport meta tag, no JavaScript errors (Chrome console), load time.
    U2  Login journey through the UI: role tab -> credentials -> CAPTCHA -> dashboard,
        session stored, then every app page while signed in, then logout.
    U3  Negative UI paths: wrong CAPTCHA and wrong password show an error, no redirect.
    U4  Role routing: operator and admin land on their own dashboards (needs DATABASE_URL
        to create those test accounts; SKIP otherwise).

    pip install selenium            (Selenium Manager downloads the matching driver)
    python QA/milestone4/day4/selenium_ui_test.py --browsers chrome,firefox,edge
        --report QA/milestone4/day4/selenium_ui_report.md --shots QA/milestone4/day4/screenshots

The CAPTCHA is read from the page (window-scope `currentCaptchaCode`) the same way a test
harness would bypass it; nothing in the app is changed for testing.
URLs come from WEB_URL / BACKEND_URL (see ../live_common.py). Runs headless by default.
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from live_common import (  # noqa: E402
    PASSWORD,
    Results,
    promote,
    register_and_login,
    service_urls,
    wake_services,
)

from selenium import webdriver  # noqa: E402
from selenium.common.exceptions import TimeoutException, WebDriverException  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402

VIEWPORTS = {"desktop": (1366, 768), "tablet": (768, 1024), "mobile": (390, 844)}
PUBLIC_PAGES = ["Login.html"]
APP_PAGES = [
    "public dashboard.html",
    "live maps.html",
    "route-analysis.html",
    "Alerts.html",
    "analytics.html",
]
DASHBOARDS = {
    "public": "public dashboard.html",
    "operator": "operator dashboard.html",
    "admin": "admin dashboard.html",
}
# Free-tier APIs can take ~60 s to wake; the page itself should be fast.
PAGE_TIMEOUT = 90


def make_driver(name, headless=True):
    if name == "chrome":
        opts = webdriver.ChromeOptions()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
        return webdriver.Chrome(options=opts)
    if name == "edge":
        opts = webdriver.EdgeOptions()
        if headless:
            opts.add_argument("--headless=new")
        opts.set_capability("ms:loggingPrefs", {"browser": "ALL"})
        return webdriver.Edge(options=opts)
    if name == "firefox":
        opts = webdriver.FirefoxOptions()
        if headless:
            opts.add_argument("-headless")
        return webdriver.Firefox(options=opts)
    raise ValueError(f"unknown browser {name}")


def page_url(web, page):
    return f"{web}/{page.replace(' ', '%20')}"


def js_errors(driver):
    """Severe console messages (Chromium only; Firefox has no log API in WebDriver)."""
    try:
        logs = driver.get_log("browser")
    except (WebDriverException, AttributeError, ValueError):
        return None
    errors = []
    for entry in logs:
        msg = entry.get("message", "")
        # Network failures for third-party assets and favicon are not app errors.
        if entry.get("level") == "SEVERE" and "favicon" not in msg:
            errors.append(msg[:200])
    return errors


def wait_loaded(driver):
    WebDriverWait(driver, PAGE_TIMEOUT).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def layout_checks(driver):
    return driver.execute_script("""
        const doc = document.documentElement;
        const nav = performance.getEntriesByType('navigation')[0];
        return {
          overflow: doc.scrollWidth - window.innerWidth,
          viewportMeta: !!document.querySelector('meta[name="viewport"]'),
          loadMs: nav ? Math.round(nav.loadEventEnd - nav.startTime) : null,
          title: document.title,
        };
    """)


def check_page(r, driver, area, web, page, viewport, shots, browser):
    width, height = VIEWPORTS[viewport]
    driver.set_window_size(width, height)
    js_errors(driver)  # drain earlier messages
    start = time.perf_counter()
    try:
        driver.get(page_url(web, page))
        wait_loaded(driver)
    except TimeoutException:
        r.add(area, f"{page} [{viewport}] loads", False, "complete", "timeout")
        return
    ms = (time.perf_counter() - start) * 1000
    info = layout_checks(driver)
    r.add(area, f"{page} [{viewport}] loads", True, "complete", info["title"][:40], ms)
    r.add(
        area,
        f"{page} [{viewport}] no horizontal scroll",
        info["overflow"] <= 1,
        "<= 1 px",
        f"{info['overflow']} px",
    )
    if viewport == "mobile":
        r.add(area, f"{page} has viewport meta", info["viewportMeta"], True, info["viewportMeta"])
    errors = js_errors(driver)
    if errors is not None:
        r.add(
            area,
            f"{page} [{viewport}] no JS errors",
            not errors,
            0,
            len(errors),
            detail="; ".join(errors[:2]),
        )
    if shots:
        safe = page.replace(" ", "_").replace(".html", "")
        driver.save_screenshot(str(shots / f"{browser}_{viewport}_{safe}.png"))


def fill_login(driver, web, role, email, password, captcha_ok=True):
    driver.get(page_url(web, "Login.html"))
    wait_loaded(driver)
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f'.role-btn[data-role="{role}"]'))
    ).click()
    driver.find_element(By.ID, "input-username").clear()
    driver.find_element(By.ID, "input-username").send_keys(email)
    driver.find_element(By.ID, "input-password").clear()
    driver.find_element(By.ID, "input-password").send_keys(password)
    # Firefox runs injected scripts in a sandbox that can't see the page's `let` bindings;
    # window.eval evaluates in the page's own global scope.
    code = (
        driver.execute_script(
            "try { return currentCaptchaCode; }"
            " catch (e) { return window.eval('currentCaptchaCode'); }"
        )
        if captcha_ok
        else "WRONG"
    )
    driver.find_element(By.ID, "input-captcha").clear()
    driver.find_element(By.ID, "input-captcha").send_keys(code)
    driver.find_element(By.ID, "submit-btn").click()


def error_shown(driver, timeout=PAGE_TIMEOUT):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: "hidden"
            not in (d.find_element(By.ID, "error-message").get_attribute("class") or "")
        )
        return True
    except TimeoutException:
        return False


def login_journey(r, driver, area, web, role, email, shots, browser):
    fill_login(driver, web, role, email, PASSWORD)
    target = DASHBOARDS[role]
    try:
        WebDriverWait(driver, PAGE_TIMEOUT).until(
            lambda d: target.replace(" ", "%20") in d.current_url or target in d.current_url
        )
        ok = True
    except TimeoutException:
        ok = False
    r.add(area, f"{role} login lands on {target}", ok, target, driver.current_url.split("/")[-1])
    if not ok:
        return False
    wait_loaded(driver)
    has_session = driver.execute_script("return !!(localStorage.length || sessionStorage.length);")
    r.add(area, f"{role} session stored", bool(has_session), True, bool(has_session))
    if shots:
        driver.save_screenshot(str(shots / f"{browser}_desktop_{role}_dashboard.png"))
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browsers", default="chrome", help="comma list: chrome,firefox,edge")
    parser.add_argument("--viewports", default="desktop,tablet,mobile")
    parser.add_argument("--report")
    parser.add_argument("--json")
    parser.add_argument("--shots", help="folder for screenshots (evidence)")
    parser.add_argument("--headed", action="store_true", help="show the browser windows")
    args = parser.parse_args()

    urls = service_urls()
    web, backend = urls["web"], urls["backend"]
    shots = Path(args.shots) if args.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    r = Results("Milestone 4 — Selenium UI Test (live frontend)", urls)

    print("Waking services...")
    ready = wake_services(urls)
    r.notes.append("Time to first 200: " + ", ".join(f"{k} {v} s" for k, v in ready.items()))

    # Test accounts are created through the API (sign-up has its own UI check below).
    accounts = {}
    email, login = register_and_login(backend, "m4ui")
    accounts["public"] = email if login else None
    for role in ("operator", "admin"):
        e, lg = register_and_login(backend, f"m4ui.{role}")
        accounts[role] = e if lg and promote(e, role) else None

    viewports = [v.strip() for v in args.viewports.split(",") if v.strip()]
    for browser in [b.strip() for b in args.browsers.split(",") if b.strip()]:
        try:
            driver = make_driver(browser, headless=not args.headed)
        except WebDriverException as exc:
            r.add(f"{browser}", "browser starts", False, "driver", str(exc).splitlines()[0][:80])
            continue
        driver.set_page_load_timeout(PAGE_TIMEOUT)
        try:
            area = f"U1 {browser}"
            for page in PUBLIC_PAGES:
                for vp in viewports:
                    check_page(r, driver, area, web, page, vp, shots, browser)

            area = f"U3 {browser}"
            if accounts["public"]:
                fill_login(driver, web, "public", accounts["public"], PASSWORD, captcha_ok=False)
                r.add(area, "Wrong CAPTCHA shows error", error_shown(driver, 10), True, "")
                fill_login(driver, web, "public", accounts["public"], "Wrong#Pass1")
                shown = error_shown(driver)
                r.add(area, "Wrong password shows error", shown, True, "")
                r.add(
                    area,
                    "Wrong password stays on Login",
                    "Login.html" in driver.current_url,
                    "Login.html",
                    driver.current_url.split("/")[-1],
                )

            area = f"U2 {browser}"
            if accounts["public"] and login_journey(
                r, driver, area, web, "public", accounts["public"], shots, browser
            ):
                for page in APP_PAGES:
                    for vp in viewports:
                        check_page(r, driver, f"U1 {browser}", web, page, vp, shots, browser)
                driver.set_window_size(*VIEWPORTS["desktop"])
                driver.get(page_url(web, "public dashboard.html"))
                wait_loaded(driver)
                driver.execute_script("if (typeof logout === 'function') logout();")
                try:
                    WebDriverWait(driver, 20).until(lambda d: "Login.html" in d.current_url)
                    out = True
                except TimeoutException:
                    out = False
                r.add(
                    area,
                    "Logout returns to Login",
                    out,
                    "Login.html",
                    driver.current_url.split("/")[-1],
                )
                driver.get(page_url(web, "admin dashboard.html"))
                try:
                    WebDriverWait(driver, 20).until(lambda d: "Login.html" in d.current_url)
                    guarded = True
                except TimeoutException:
                    guarded = False
                r.add(
                    area,
                    "Dashboard guarded after logout",
                    guarded,
                    "redirect to Login",
                    driver.current_url.split("/")[-1],
                )
            elif not accounts["public"]:
                r.add(area, "Public account", False, "created", "API register/login failed")

            area = f"U4 {browser}"
            for role in ("operator", "admin"):
                if not accounts[role]:
                    r.add(area, f"{role} login", None, "dashboard", "no DATABASE_URL to promote")
                    continue
                driver.delete_all_cookies()
                driver.get(page_url(web, "Login.html"))
                driver.execute_script("localStorage.clear(); sessionStorage.clear();")
                if login_journey(r, driver, area, web, role, accounts[role], shots, browser):
                    check_page(r, driver, area, web, DASHBOARDS[role], "desktop", shots, browser)
        finally:
            driver.quit()

    print()
    print(r.markdown())
    r.save(args.report, args.json)
    return 1 if r.failed else 0


if __name__ == "__main__":
    sys.exit(main())
