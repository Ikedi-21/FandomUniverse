"""Crawl the local Django site and verify its links and browser resources."""
from __future__ import annotations

import http.cookiejar
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from html.parser import HTMLParser

BASE = "http://127.0.0.1:8000"
LOGIN = "/accounts/login/"
ROLES = [("anonymous", None), ("demo_user", "FandomDemo!2026"), ("admin", "FandomAdmin!2026")]
MAX_PAGES = 400


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.resources, self.forms = [], [], []
        self.form = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "link" and a.get("href"):
            self.resources.append(a["href"])
        if tag in ("script", "img", "source", "iframe") and a.get("src"):
            self.resources.append(a["src"])
        if tag == "form":
            self.form = {"attrs": a, "inputs": []}
            self.forms.append(self.form)
        elif tag == "input" and self.form is not None:
            self.form["inputs"].append(a)

    def handle_endtag(self, tag):
        if tag == "form":
            self.form = None


class Crawler:
    def __init__(self, role, password):
        self.role, self.password = role, password
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.errors, self.pages = [], {}
        self.checked_resources = set()

    def fetch(self, url, data=None):
        req = urllib.request.Request(url, data=data, headers={"User-Agent": "FanHubCrawler/1.0"})
        try:
            with self.opener.open(req, timeout=12) as res:
                return res.status, res.geturl(), res.headers.get("Content-Type", ""), res.read()
        except urllib.error.HTTPError as e:
            return e.code, e.geturl(), e.headers.get("Content-Type", ""), e.read()
        except Exception as e:
            return 0, url, "", str(e).encode()

    def login(self):
        status, final, _, body = self.fetch(BASE + LOGIN)
        parser = PageParser(); parser.feed(body.decode("utf-8", "replace"))
        form = next((f for f in parser.forms if f["attrs"].get("method", "get").lower() == "post"), None)
        if not form:
            self.errors.append((LOGIN, "login form missing", status)); return
        action = urllib.parse.urljoin(final, form["attrs"].get("action", final))
        fields = {i.get("name"): i.get("value", "") for i in form["inputs"] if i.get("name")}
        fields.update({"username": self.role, "password": self.password})
        data = urllib.parse.urlencode(fields).encode()
        req = urllib.request.Request(action, data=data, headers={"Referer": final, "Content-Type": "application/x-www-form-urlencoded"})
        try:
            self.opener.open(req, timeout=12).read()
        except urllib.error.HTTPError as e:
            if e.code >= 400:
                self.errors.append((LOGIN, "login POST", e.code))

    def check_resource(self, page, src):
        if src.startswith(("data:", "blob:", "mailto:", "javascript:")):
            return
        url = urllib.parse.urljoin(page, src)
        parts = urllib.parse.urlsplit(url)
        if parts.netloc != "127.0.0.1:8000":
            return
        resource_key = urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))
        if resource_key in self.checked_resources:
            return
        self.checked_resources.add(resource_key)
        status, final, ctype, body = self.fetch(url)
        if status < 200 or status >= 400:
            self.errors.append((page, url, status))
        if "text/css" in ctype or parts.path.endswith(".css"):
            css = body.decode("utf-8", "replace")
            for ref in re.findall(r"url\((?:['\"])?([^)'\"]+)", css, re.I):
                self.check_resource(final, ref.strip())

    def crawl(self):
        if self.password:
            self.login()
        queue = deque([BASE + "/", BASE + "/sitemap/"])
        seen = set()
        while queue and len(seen) < MAX_PAGES:
            url = queue.popleft()
            clean = urllib.parse.urldefrag(url)[0]
            if clean in seen:
                continue
            seen.add(clean)
            status, final, ctype, body = self.fetch(clean)
            self.pages[clean] = status
            if status < 200 or status >= 400:
                self.errors.append((clean, "page", status)); continue
            if "text/html" not in ctype:
                continue
            parser = PageParser(); parser.feed(body.decode("utf-8", "replace"))
            for src in parser.resources:
                self.check_resource(final, src)
            for href in parser.links:
                target = urllib.parse.urljoin(final, href)
                parts = urllib.parse.urlsplit(target)
                if parts.netloc == "127.0.0.1:8000":
                    # Query variants such as ?next= create unbounded duplicate pages.
                    target = urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
                    if target not in seen:
                        queue.append(target)
        return seen


def main():
    total = 0
    print("role | page | broken resource or link | status")
    for role, password in ROLES:
        crawler = Crawler(role, password)
        crawler.crawl()
        for page, reason, status in crawler.errors:
            print(f"{role} | {page} | {reason} | {status}")
        total += len(crawler.errors)
        print(f"{role} | pages checked={len(crawler.pages)} | problems={len(crawler.errors)}")
    print(f"TOTAL: {total} problems")
    raise SystemExit(bool(total))


if __name__ == "__main__":
    main()
