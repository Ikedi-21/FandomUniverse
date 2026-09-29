"""Real-browser smoke checks for linked pages, shared styling, theme and font state."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

from crawl import BASE, Crawler, ROLES

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "screenshots"
THEME_PATHS = [
    "/catalog/explore/", "/merch/", "/accounts/login/", "/accounts/register/",
    "/characters/", "/events/", "/sitemap/", "/catalog/content/anime-original-feature-1/",
    "/dashboard/", "/profile/",
]


def log_in(page, username, password):
    page.goto(BASE + "/accounts/login/", wait_until="domcontentloaded")
    page.locator('form.auth-form input[name="username"]').fill(username)
    page.locator('form.auth-form input[name="password"]').fill(password)
    page.locator('form.auth-form button[type="submit"]').click()
    page.wait_for_load_state("domcontentloaded")
    if page.url.endswith("/accounts/login/"):
        raise RuntimeError(f"Real login failed for role {username}")


def main():
    page_set = Crawler("anonymous", None).crawl()
    paths = sorted({urlsplit(u).path for u in page_set})
    SCREENSHOTS.mkdir(exist_ok=True)
    rows, issues = [], set()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for role, password in ROLES:
            for width in (1280, 375):
                context = browser.new_context(viewport={"width": width, "height": 900})
                page = context.new_page()
                page.on("pageerror", lambda exc, r=role, w=width: issues.add((r, w, "console", str(exc))))
                page.on("console", lambda msg, r=role, w=width: issues.add((r, w, "console", msg.text)) if msg.type == "error" else None)
                page.on("requestfailed", lambda req, r=role, w=width: issues.add((r, w, "network", req.url + " :: " + str(req.failure))))
                page.on("response", lambda res, r=role, w=width: issues.add((r, w, "network", f"{res.status} {res.url}")) if res.status >= 400 else None)
                if password:
                    log_in(page, role, password)
                for path in paths:
                    try:
                        response = page.goto(BASE + path, wait_until="domcontentloaded", timeout=20000)
                        page.wait_for_timeout(80)
                        status = response.status if response else 0
                        details = page.evaluate("""() => ({
                          width: document.documentElement.scrollWidth,
                          viewport: window.innerWidth,
                          styles: [...document.querySelectorAll('link[rel=stylesheet]')].filter(x => x.sheet).length,
                          main: !![...document.scripts].find(x => x.src.endsWith('/js/main.js')),
                          themeInit: !![...document.scripts].find(x => x.src.endsWith('/js/theme-init.js'))
                        })""")
                        overflow = details["width"] > details["viewport"]
                        styled = details["styles"] >= 5 and details["main"] and details["themeInit"]
                        rows.append((role, width, path, status, "YES" if styled else "NO", "YES" if overflow else "NO"))
                        if status >= 400 or not styled or overflow:
                            issues.add((role, width, path, f"status={status}, styled={styled}, overflow={overflow}"))
                        if path == "/" and not (SCREENSHOTS / f"{role}-{width}-home.png").exists():
                            page.screenshot(path=str(SCREENSHOTS / f"{role}-{width}-home.png"), full_page=True)
                    except Exception as exc:
                        rows.append((role, width, path, 0, "NO", "unknown"))
                        issues.add((role, width, path, str(exc)))

                # Verify visitor preferences persist between the actual site pages.
                if role == "anonymous":
                    page.goto(BASE + "/catalog/explore/", wait_until="domcontentloaded")
                    page.locator("#themeToggleBtn").click()
                    for target in THEME_PATHS[:8]:
                        page.goto(BASE + target, wait_until="domcontentloaded")
                        theme = page.locator("html").get_attribute("data-theme")
                        if theme != "dark": issues.add((role, width, target, f"theme expected dark, got {theme}"))
                        page.reload(wait_until="domcontentloaded")
                        if page.locator("html").get_attribute("data-theme") != "dark":
                            issues.add((role, width, target, "dark theme did not survive reload"))
                    page.goto(BASE + "/accounts/login/", wait_until="domcontentloaded")
                    page.locator("#themeToggleBtn").click()
                    page.goto(BASE + "/characters/", wait_until="domcontentloaded")
                    if page.locator("html").get_attribute("data-theme") != "light":
                        issues.add((role, width, "/characters/", "light theme did not persist"))
                    page.locator("#fontSizeControl").select_option("large")
                    for target in ("/events/", "/sitemap/"):
                        page.goto(BASE + target, wait_until="domcontentloaded")
                        size = page.locator("html").get_attribute("data-font-size")
                        if size != "large": issues.add((role, width, target, f"font expected large, got {size}"))
                elif role == "demo_user":
                    page.goto(BASE + "/catalog/explore/", wait_until="domcontentloaded")
                    if page.locator("html").get_attribute("data-theme") != "dark":
                        page.locator("#themeToggleBtn").click()
                    page.wait_for_timeout(200)
                    for target in THEME_PATHS:
                        page.goto(BASE + target, wait_until="domcontentloaded")
                        theme = page.locator("html").get_attribute("data-theme")
                        if theme != "dark": issues.add((role, width, target, f"profile theme expected dark, got {theme}"))
                        if not page.locator(".server-session-controls").get_by_text(role).count():
                            issues.add((role, width, target, "server-rendered signed-in header missing"))
                    page.locator("#fontSizeControl").select_option("large")
                    page.wait_for_timeout(200)
                    page.goto(BASE + "/profile/", wait_until="domcontentloaded")
                    if page.locator("html").get_attribute("data-font-size") != "large":
                        issues.add((role, width, "/profile/", "saved font size did not persist"))
                    if page.locator("form[action='/accounts/logout/']").count() == 0:
                        issues.add((role, width, "/profile/", "server-rendered logout form missing"))
                    page.locator("form[action='/accounts/logout/'] button[type='submit']").click()
                    page.wait_for_load_state("domcontentloaded")
                    log_in(page, role, password)
                    if page.locator("html").get_attribute("data-theme") != "dark":
                        issues.add((role, width, "/accounts/login/", "profile theme did not restore after logout/login"))
                    if page.locator("html").get_attribute("data-font-size") != "large":
                        issues.add((role, width, "/accounts/login/", "profile font size did not restore after logout/login"))
                context.close()
        browser.close()

    print("role | width | page | status | styled | horizontal overflow")
    for row in rows: print(" | ".join(map(str, row)))
    print(f"PAGES: {len(paths)} per role/width; browser views: {len(rows)}")
    print("PROBLEMS:")
    for issue in sorted(issues): print(" | ".join(map(str, issue)))
    print(f"{len(issues)} browser problems found")
    raise SystemExit(bool(issues))


if __name__ == "__main__":
    main()
