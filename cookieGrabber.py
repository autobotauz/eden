# capture_discord_oauth_cookie_headless_with_fallback.py
"""
Attempts headless Selenium login to the Discord OAuth url and captures cookies when redirected
back to eden-daoc.net. If Cloudflare / bot-check or other blocking is detected, it restarts
Chrome in visible mode so you can complete login and the script captures cookies automatically.

Requirements:
  - pip install selenium
  - compatible Chrome and ChromeDriver. See: https://googlechromelabs.github.io/chrome-for-testing/
  - Update CHROMEDRIVER_PATH and (optionally) USER_DATA_DIR below.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, re, json, os, sys

# === CONFIG ===
CHROMEDRIVER_PATH = r"chromedriver.exe"   # <<--- update this
OAUTH_URL = (
    "https://discord.com/api/v9/oauth2/authorize?"
    "client_id=1000531741456470137&response_type=code&"
    "redirect_uri=https%3A%2F%2Feden-daoc.net%2Fucp.php%3Fmode%3Dlogin%26login%3Dexternal%26oauth_service%3Dstudio_discord&"
    "scope=identify%20email&state=3ef27fa63651cf44448cd6110a204505&integration_type=0"
)
# If you want to reuse an existing Chrome profile (avoid re-login), set USER_DATA_DIR to that path.
USER_DATA_DIR = None  # e.g. r"C:\Users\<you>\AppData\Local\Google\Chrome\User Data\Profile 1"

# How long to wait for redirect to eden-daoc.net (seconds)
MAX_WAIT_SECONDS = 180

# Output files
COOKIES_JSON = "cookies_captured.json"
JWT_TXT = "jwt_cookie.txt"
PREFERRED_COOKIE_TXT = "preferred_cookie.txt"

JWT_RE = re.compile(r'^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$')

def make_driver(headless=True):
    options = webdriver.ChromeOptions()
    if USER_DATA_DIR:
        options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    if headless:
        # headless mode - use "new" headless when available
        options.add_argument("--headless=new")
        # common headless flags
    # anti-detection / session-like options
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,1024")
    # set a common user-agent (adjust if you prefer)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    # Use CDP to hide webdriver property for new documents
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'}
        )
    except Exception:
        # older/newer versions may differ; ignore if not available
        pass

    return driver

def capture_cookies_from_driver(driver):
    cookies = driver.get_cookies()
    # normalize cookies list
    cookies_list = []
    for c in cookies:
        cookies_list.append({
            "name": c.get("name"),
            "value": c.get("value"),
            "domain": c.get("domain"),
            "path": c.get("path"),
            "secure": c.get("secure"),
            "httpOnly": c.get("httpOnly"),
            "expiry": c.get("expiry"),
        })
    return cookies_list

def looks_like_cloudflare_bot_check(page_source, title):
    # Common signs: "Bot check", "Checking your browser", or inline base64 JS challenge
    ps = (page_source or "").lower()
    title_l = (title or "").lower()
    if "bot check" in title_l or "checking your browser" in ps or "bot check" in ps:
        return True
    # Cloudflare JS challenge often has "jschl_vc" or "cf_clearance" patterns
    if "cf_clearance" in ps or "data:text/javascript;base64" in ps:
        return True
    return False

def run_attempt(headless=True):
    driver = make_driver(headless=headless)
    try:
        driver.get(OAUTH_URL)
        print(f"Opened OAuth URL (headless={headless}). Waiting for redirect to eden-daoc.net ...")

        # Wait until the URL contains eden-daoc.net/ucp.php OR until timeout
        try:
            WebDriverWait(driver, MAX_WAIT_SECONDS).until(EC.url_contains("eden-daoc.net/ucp.php"))
        except Exception as exc:
            # timed out waiting for expected redirect
            print("Timeout waiting for redirect; current URL:", driver.current_url)
            # but continue to inspect page for bot-check
        # small pause to let any final cookies be set
        time.sleep(1.0)

        current_url = driver.current_url
        title = driver.title
        page_source = ""
        try:
            page_source = driver.page_source
        except Exception:
            pass

        print("Current URL:", current_url)
        print("Page title:", title)

        # check for bot-check/cloudflare
        if looks_like_cloudflare_bot_check(page_source, title):
            print("Detected a JS/bot-check (Cloudflare-like) on the response. Headless may be blocked.")
            return {"status": "bot_check", "driver": driver, "current_url": current_url, "page_source": page_source}

        # If redirected properly but no code param present that's OK; site may set session and redirect without code
        # capture cookies
        cookies_list = capture_cookies_from_driver(driver)
        # save cookies
        with open(COOKIES_JSON, "w") as f:
            json.dump(cookies_list, f, indent=2)
        print(f"Saved {len(cookies_list)} cookies to {COOKIES_JSON}")

        # detect jwt-like cookie
        jwt_candidates = [c for c in cookies_list if c.get("value") and JWT_RE.match(c["value"])]
        if jwt_candidates:
            print("Found JWT-like cookie(s):", [c["name"] for c in jwt_candidates])
            with open(JWT_TXT, "w") as f:
                f.write(jwt_candidates[0]["value"])
            print(f"Wrote first JWT-shaped cookie value to {JWT_TXT}")
        else:
            print("No JWT-shaped cookie detected automatically. Inspect", COOKIES_JSON)

        # prefer common cookie names
        preferred_names = ["POWSESS", "eden_daoc_sid", "eden_daoc_u", "eden_daoc_k", "session", "jwt", "auth"]
        found_pref = None
        for n in preferred_names:
            for c in cookies_list:
                if c["name"] and c["name"].lower() == n.lower():
                    found_pref = c
                    break
            if found_pref:
                break
        if found_pref:
            with open(PREFERRED_COOKIE_TXT, "w") as f:
                f.write(found_pref["value"])
            print(f"Saved preferred cookie ({found_pref['name']}) to {PREFERRED_COOKIE_TXT}")

        return {"status": "ok", "cookies": cookies_list, "driver": driver, "current_url": current_url}

    except Exception as e:
        print("Exception during attempt:", repr(e))
        return {"status": "error", "error": str(e), "driver": driver}
    # not closing the driver here on purpose for fallback handler to reuse if needed

def main():
    # 1) try headless
    print("Attempt 1: headless mode")
    res = run_attempt(headless=True)

    if res.get("status") == "bot_check":
        print("Headless got bot check. Restarting in visible mode so you can interact and finish login...")
        # close the headless driver
        try:
            res["driver"].quit()
        except Exception:
            pass

        # 2) restart in visible (non-headless)
        res2 = run_attempt(headless=False)
        if res2.get("status") == "ok":
            print("Captured cookies in visible mode. Output files:", COOKIES_JSON, JWT_TXT, PREFERRED_COOKIE_TXT)
            # clean up driver
            try:
                res2["driver"].quit()
            except Exception:
                pass
            return
        else:
            print("Visible-mode attempt failed:", res2.get("status"), res2.get("error"))
            try:
                res2["driver"].quit()
            except Exception:
                pass
            return
    elif res.get("status") == "ok":
        print("Headless attempt succeeded. Cookies saved to", COOKIES_JSON)
        try:
            res["driver"].quit()
        except Exception:
            pass
        return
    else:
        print("Headless attempt errored:", res.get("status"), res.get("error"))
        try:
            res["driver"].quit()
        except Exception:
            pass
        # fallback visible attempt
        print("Falling back to visible mode attempt now...")
        res2 = run_attempt(headless=False)
        if res2.get("status") == "ok":
            print("Captured cookies in visible mode. Output files:", COOKIES_JSON, JWT_TXT, PREFERRED_COOKIE_TXT)
            try:
                res2["driver"].quit()
            except Exception:
                pass
        else:
            print("Visible attempt also failed. See output above.")

if __name__ == "__main__":
    # basic sanity checks
    if not os.path.exists(CHROMEDRIVER_PATH) and not os.path.exists(CHROMEDRIVER_PATH):
        print("ERROR: CHROMEDRIVER_PATH not found at:", CHROMEDRIVER_PATH)
        print("Download ChromeDriver that matches your Chrome version and set CHROMEDRIVER_PATH.")
        sys.exit(1)
    main()
