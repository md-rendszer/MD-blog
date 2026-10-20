#!/usr/bin/env python3
"""A blogbejegyzések alapellenőrzése.

Használat: python ellenorzes.py [fájl ...]
Fájlok megadása nélkül az összes bejegyzést ellenőrzi.
Hibánál 1-es kóddal lép ki.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTENT = ROOT / "CONTENT"
MANIFEST = json.loads((CONTENT / "images" / "_manifest.json").read_text(encoding="utf-8"))
DATE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("hiányzó vagy lezáratlan frontmatter")
    values = {}
    for line in text[4 : text.find("\n---\n", 4)].splitlines():
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"hibás frontmatter sor: {line!r}")
        value = value.strip()
        values[key.strip()] = json.loads(value) if value.startswith('"') else value
    return values


def check(path: Path) -> list[str]:
    errors = []
    try:
        meta = frontmatter(path)
    except (ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]
    if not meta.get("title"):
        errors.append("nincs title")
    date = meta.get("date", "")
    if not DATE.match(date):
        errors.append(f"hibás date: {date!r}")
    elif path.parent.name.isdigit() and not date.startswith(path.parent.name):
        errors.append(f"a date éve nem egyezik a mappával ({path.parent.name})")
    if not SLUG.match(path.stem):
        errors.append("a fájlnév nem kisbetűs, ékezet nélküli, kötőjeles slug")
    image = meta.get("image", "-")
    if image not in {"-", "", "null", "None"}:
        if not (CONTENT / "images" / image).exists():
            errors.append(f"a kép nem létezik: images/{image}")
        elif f"/images/{image}" not in MANIFEST:
            errors.append(f"a kép hiányzik a _manifest.json-ból: {image}")
    return errors


def main() -> None:
    paths = [Path(p) for p in sys.argv[1:]] or sorted((CONTENT / "blog").rglob("*.md"))
    failed = 0
    for path in paths:
        errors = check(path)
        if errors:
            failed += 1
            print(f"{path.relative_to(ROOT) if path.is_absolute() else path}:")
            for error in errors:
                print(f"  - {error}")
    print(f"{len(paths)} bejegyzés ellenőrizve, {failed} hibás.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
