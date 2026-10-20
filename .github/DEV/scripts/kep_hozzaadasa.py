#!/usr/bin/env python3
"""Borítókép hozzáadása egy blogbejegyzéshez.

Használat: python kep_hozzaadasa.py <forraskep> <év> <slug>

Legyártja a 400, 768 és 1024 px széles AVIF-változatokat a
CONTENT/images/<év>/ mappába, és felveszi őket a _manifest.json-ba.
"""
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
IMAGES = ROOT / "CONTENT" / "images"
MANIFEST = IMAGES / "_manifest.json"
WIDTHS = (400, 768, 1024)


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    source, year, slug = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    image = Image.open(source).convert("RGB")
    if image.width < 1024:
        print(f"Figyelem: a forráskép csak {image.width} px széles.", file=sys.stderr)
    folder = IMAGES / year
    folder.mkdir(parents=True, exist_ok=True)

    variants = []
    for width in WIDTHS:
        height = round(image.height * width / image.width)
        name = f"{slug}.avif" if width == WIDTHS[-1] else f"{slug}-{width}x{height}.avif"
        image.resize((width, height), Image.LANCZOS).save(folder / name, quality=70)
        variants.append((f"/images/{year}/{name}", width, height))

    srcset = ", ".join(f"{path} {width}w" for path, width, _ in variants)
    raw = MANIFEST.read_text(encoding="utf-8") if MANIFEST.exists() else "{}"
    manifest = json.loads(raw)
    for path, width, height in variants:
        manifest[path] = {"width": width, "height": height, "srcset": srcset}
    indent = 2 if '\n  "' in raw else None
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=indent)
        + ("\n" if raw.endswith("\n") else ""),
        encoding="utf-8",
    )
    print(f"image: {year}/{slug}.avif")


if __name__ == "__main__":
    main()
