#!/usr/bin/env python3
"""A kész oldal (dist/) ellenőrzése élesítés előtt.

Megakadályozza, hogy az oldal kinézet nélkül („szétesve”) kerüljön ki:
- minden HTML-oldalnak be kell húznia a /assets/site.css-t,
- a site.css-nek léteznie kell és nem lehet üres,
- minden helyi /assets/ és /images/ hivatkozásnak létező fájlra kell mutatnia.

Hibánál 1-es kóddal lép ki, így a GitHub Actions leállítja a telepítést,
és az előző, működő változat marad kint.
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[3]
DIST = ROOT / "dist"
REF = re.compile(r'(?:href|src)="([^"]+)"')
CHECKED_PREFIXES = ("/assets/", "/images/")


def main() -> None:
    errors: list[str] = []
    css = DIST / "assets" / "site.css"
    if not css.is_file() or css.stat().st_size < 1000:
        errors.append("dist/assets/site.css hiányzik vagy gyanúsan kicsi")

    pages = sorted(DIST.rglob("*.html"))
    if not pages:
        errors.append("nincs egyetlen HTML-oldal sem a dist/ mappában")

    missing: dict[str, int] = {}
    without_css = 0
    for page in pages:
        text = page.read_text(encoding="utf-8")
        is_redirect = 'http-equiv="refresh"' in text
        if not is_redirect and not re.search(r'href="[^"]*/assets/site\.css(\?v=[0-9a-f]+)?"', text):
            without_css += 1
        for ref in REF.findall(text):
            if "\\" in ref:
                missing[f"hibás (visszaperjeles) cím: {ref}"] = missing.get(f"hibás (visszaperjeles) cím: {ref}", 0) + 1
                continue
            path = unquote(urlparse(ref).path) if not ref.startswith(("http:", "https:", "//")) else ""
            if path.startswith(CHECKED_PREFIXES) and not (DIST / path.lstrip("/")).is_file():
                missing[path] = missing.get(path, 0) + 1

    if without_css:
        errors.append(f"{without_css} oldal nem hivatkozik a /assets/site.css-re")
    for path, count in sorted(missing.items()):
        errors.append(f"nem létező fájlra hivatkozás: {path} ({count} oldalon)")

    if errors:
        print("A kész oldal HIBÁS, nem élesíthető:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print(f"Kész oldal rendben: {len(pages)} HTML-oldal, arculat (site.css) megvan.")


if __name__ == "__main__":
    main()
