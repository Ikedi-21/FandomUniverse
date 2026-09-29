"""Audit project templates for broken Django static and URL references."""
from __future__ import annotations

import re
from pathlib import Path

import os
import sys
import django

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FandomUniverse.settings")
django.setup()

from django.urls import NoReverseMatch, reverse

TEMPLATE_DIRS = [p for p in ROOT.glob("*/templates") if p.is_dir()]
TEMPLATE_DIRS += [ROOT / "core"]
RAW_ASSET = re.compile(r"(?:href|src)\s*=\s*['\"]((?:\.\.?/|/)?(?:css|js|images|assets|hero_section|avatars|fandoms|posters)/[^'\"]+)['\"]", re.I)
RAW_HTML = re.compile(r"(?:href|action)\s*=\s*['\"]([^'\"]+\.html(?:[?#][^'\"]*)?)['\"]", re.I)
URL_TAG = re.compile(r"\{%\s*url\s+['\"]([^'\"]+)['\"]([^%]*)%\}")
STATIC_TAG = re.compile(r"\{%\s*static\s+['\"]")
LOAD_STATIC = re.compile(r"\{%\s*load\s+[^%]*\bstatic\b[^%]*%\}")
THEME = re.compile(r"localStorage\.(?:getItem|setItem)\(['\"]([^'\"]+)")


def can_reverse(name: str, tail: str) -> bool:
    attempts = [(), (1,), ("sample",), (1, 1), ("sample", 1), (1, "sample")]
    if " as " in name or name == "static":
        return True
    for args in attempts:
        try:
            reverse(name, args=args)
            return True
        except (NoReverseMatch, TypeError):
            pass
    return False


def main() -> None:
    problems: list[str] = []
    rows = []
    files = sorted({f for d in TEMPLATE_DIRS for f in d.rglob("*.html")})
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT).as_posix()
        if STATIC_TAG.search(text) and not LOAD_STATIC.search(text):
            problems.append(f"{rel}: static tag without load static")
        assets = RAW_ASSET.findall(text)
        html_links = RAW_HTML.findall(text)
        urls = URL_TAG.findall(text)
        for value in assets:
            problems.append(f"{rel}: raw asset path {value}")
        for value in html_links:
            problems.append(f"{rel}: raw .html link {value}")
        for name, tail in urls:
            if not can_reverse(name, tail):
                problems.append(f"{rel}: cannot reverse URL name {name}")
        rows.append((rel, bool(LOAD_STATIC.search(text)), len(STATIC_TAG.findall(text)), len(assets), len(urls), len(html_links), ",".join(THEME.findall(text)) or "none"))
    print("app | path | load static | static tags | raw assets | url tags | raw .html links | theme keys")
    for rel, loaded, nstatic, nasset, nurl, nhtml, keys in rows:
        app = rel.split("/")[0]
        print(f"{app} | {rel} | {'yes' if loaded else 'no'} | {nstatic} | {nasset} | {nurl} | {nhtml} | {keys}")
    print("Problems:")
    for issue in problems:
        print(issue)
    print(f"{len(problems)} problems found")
    raise SystemExit(bool(problems))


if __name__ == "__main__":
    main()
