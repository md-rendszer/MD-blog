from __future__ import annotations

import html
import json
import math
import os
import re
import shutil
import unicodedata
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

import markdown
from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
CONTENT = ROOT / "CONTENT"
OUTPUT = ROOT / "dist"
BASE_PATH = os.environ.get("SITE_BASE_PATH", "").rstrip("/")
SITE_URL = os.environ.get("SITE_URL", "https://matedomokos.hu").rstrip("/")
# Az általam alkotott rendszer (WordPress) – a felső sáv és a lábléc linkje ide mutat.
MAIN_SITE_URL = "https://mdmegvalositorendszer.hu/"
SITE_NAME = "Máté Domokos"
# A matedomokos.hu Domi személyes oldala (Rólam, Írások, közösségek, ajánlott,
# kapcsolat). A rendszerhez tartozó oldalak a központi WordPress-oldalon élnek;
# a régi címük oda irányít. A többi önálló oldal itt épül (CONTENT/*.md).
MOVED_PAGES = {
    "alap": f"{MAIN_SITE_URL}alap/",
    "alapozas": f"{MAIN_SITE_URL}alap/",
    "miert-jott-letre-az-md-megvalosito-rendszer": f"{MAIN_SITE_URL}miert-jott-letre-az-md-megvalosito-rendszer/",
    "mdhu-megvalosito-rendszer": MAIN_SITE_URL,
    "mdhu_megvalosito_rendszer": MAIN_SITE_URL,
}
FEED_SIZE = 20
# Témakörök: minden bejegyzés frontmatterében `tema:` jelöli, melyikbe tartozik.
# A témaoldalak (/tema/<slug>/) abban segítenek, hogy az olvasó a neki szóló
# írásokat egy helyen találja; a cikkek végén ugyanebből jön a „Neked ajánlom még”.
TOPICS: dict[str, tuple[str, str]] = {
    "felelosseg-es-napi-gyakorlat": ("Felelősség és napi gyakorlat", "Ha tudod, mi lenne jó, mégsem teszed; ha halogatsz, vagy azt keresed, mi múlik valóban rajtad – itt a következő lépésed."),
    "ego-es-elme": ("Ego, elme, belső hang", "Ha a fejedben szóló hang nem hallgat el, ítél, aggódik és rágódik – ezek az írások abban segítenek, hogy újra te vezess."),
    "onismeret-es-jelenlet": ("Önismeret és jelenlét", "Ha azt kérdezed, ki vagy valójában, és hogyan találhatsz haza önmagadhoz – itt kezdd."),
    "meltosag-es-ujrakezdes": ("Méltóság és újrakezdés", "Ha hibát cipelsz, szégyent érzel, vagy úgy érzed, elvesztetted a méltóságodat – ezek az írások a visszautat mutatják."),
    "kapcsolatok-es-konfliktusok": ("Kapcsolatok és konfliktusok", "Harag, vita, cserbenhagyás, indulat, magány – ha a kapcsolataidban keresel kapaszkodót, ezek neked szólnak."),
    "hit-es-biblia": ("Hit és Biblia", "Ha a Biblia üzenetét a mai életedre fordítanád le – a méltóságról, a kegyelemről, a hazatérésről."),
    "meditacio-es-joga": ("Meditáció, jóga, mesterek", "Krija-jóga, Transzcendentális Meditáció, Bábádzsí és Jógánanda – ha befelé vezető utat és gyakorlatot keresel."),
    "tanitok-es-tisztanlatas": ("Tanítók és tisztánlátás", "Ha egy tanító, egy videó vagy egy „most vagy soha” üzenet hatása alatt vagy, és szűrőt keresel, mielőtt rábíznád magad."),
    "tarsadalom-penz-technologia": ("Társadalom, pénz, technológia", "Kényelem, képernyő, mesterséges intelligencia, életszínvonal, közös döntések – ha a világ működését szeretnéd tisztábban látni."),
    "magyarsag-es-tortenelem": ("Magyarság és történelem", "Himnusz, székelyek, Trianon, a Kárpát-medence népei – ha fontosak a gyökereid, és igazul szeretnéd szeretni a múltunkat."),
    "egeszseg-es-termeszet": ("Egészség és természet", "Sejtek, mikrobiom, öregkor, víz és föld – ha a tested és a ránk bízott világ egészsége foglalkoztat."),
    "konyvek-es-filmek": ("Könyvek és filmek", "Ha jó könyvet, hangoskönyvet vagy elgondolkodtató filmet keresel a belső úthoz."),
    "md-megvalosito-rendszer": ("Az MD Megvalósító Rendszer", "Ha az MD Megvalósító Rendszer – Újjászületési és Helyreállítási Program érdekel: mi ez, hogyan épül fel, és hol kezdheted."),
    "domi-utja": ("Domi útja – személyes írások", "Ha szeretnéd tudni, ki ír neked: Máté Domokos személyes vallomásai és életútja."),
}
# Hozzászólások: Hyvor Talk (talk.hyvor.com). Üresen hagyva nincs hozzászólás-mező.
# A Website ID nem titkos, a Hyvor Talk konzoljában látható.
HYVOR_WEBSITE_ID = os.environ.get("HYVOR_WEBSITE_ID", "").strip()
# Olvasói visszajelzés (Tetszett? + három kérdés). Amíg nincs SalesAutopilot-űrlap,
# a válasz e-mailben érkezik erre a címre.
FEEDBACK_EMAIL = os.environ.get("FEEDBACK_EMAIL", "kapcsolat@mdmegvalositorendszer.hu").strip()
MD = markdown.Markdown(extensions=["extra", "sane_lists", "smarty"])
IMAGE_MANIFEST_PATH = CONTENT / "images" / "_manifest.json"
IMAGE_MANIFEST: dict[str, dict] = {}
BLOG_SLUGS: set[str] = set()
PAGE_SLUGS: set[str] = set()
BLOG_ALIASES: dict[str, str] = {}
PAGE_ALIASES: dict[str, str] = {}
MISSING_LOCAL_IMAGE_SOURCES: set[str] = set()


@dataclass
class Document:
    title: str
    date: str
    body: str
    slug: str
    image: str
    image_alt: str
    path: Path
    alias: str
    lead: str = ""
    kerdes: str = ""
    kinek: str = ""
    tema: str = ""
    kereses: tuple[str, ...] = ()


def split_frontmatter(text: str, path: Path) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError(f"{path} has no YAML front matter")
    marker = text.find("\n---\n", 4)
    if marker == -1:
        raise ValueError(f"{path} has an unterminated YAML front matter block")
    values: dict[str, str] = {}
    for line in text[4:marker].splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"Invalid front matter in {path}: {line}")
        value = value.strip()
        values[key.strip()] = json.loads(value) if value.startswith('"') else value
    return values, text[marker + 5 :]


def load_document(path: Path) -> Document:
    metadata, body = split_frontmatter(
        filesystem_path(path).read_text(encoding="utf-8"), path
    )
    return Document(
        title=metadata["title"],
        date=metadata.get("date", ""),
        body=body,
        slug=urllib.parse.unquote(path.stem),
        image=""
        if metadata.get("image", "-") in {"-", "", "null", "None"}
        else metadata["image"],
        image_alt=metadata.get("image_alt", ""),
        path=path,
        alias=metadata.get("alias", ""),
        lead=metadata.get("lead", ""),
        kerdes=metadata.get("kerdes", ""),
        kinek=metadata.get("kinek", ""),
        tema=metadata.get("tema", ""),
        kereses=tuple(
            part.strip() for part in metadata.get("kereses", "").split(";") if part.strip()
        ),
    )


def documents() -> tuple[list[Document], list[Document], Document | None]:
    pages: list[Document] = []
    root_page = None
    for path in sorted(CONTENT.glob("*.md")):
        page = load_document(path)
        if path.name == "_index.md":
            root_page = page
        else:
            pages.append(page)
    posts = [
        load_document(path)
        for path in sorted((CONTENT / "blog").rglob("*.md"))
        if path.name != "blog.md"
    ]
    posts.sort(key=lambda item: (item.date, item.title.casefold()), reverse=True)
    return pages, posts, root_page


def prefixed_url(value: str) -> str:
    if BASE_PATH and value.startswith("/") and not value.startswith("//"):
        return f"{BASE_PATH}{value}"
    return value


def add_responsive_image_attributes(rendered: str) -> str:
    if not IMAGE_MANIFEST_PATH.exists():
        return rendered
    manifest = json.loads(IMAGE_MANIFEST_PATH.read_text(encoding="utf-8"))

    def enhance(match: re.Match) -> str:
        tag = match.group(0)
        src_match = re.search(r'\bsrc=["\']([^"\']+)["\']', tag)
        if not src_match:
            return tag
        info = manifest.get(src_match.group(1))
        if not info:
            return tag
        attributes = []
        if info.get("srcset"):
            attributes.append(f'srcset="{html.escape(info["srcset"], quote=True)}"')
            attributes.append('sizes="(max-width: 760px) 100vw, 900px"')
        if info.get("width") and not re.search(r"\bwidth=", tag):
            attributes.append(f'width="{info["width"]}"')
        if info.get("height") and not re.search(r"\bheight=", tag):
            attributes.append(f'height="{info["height"]}"')
        if attributes:
            tag = tag[:-1] + " " + " ".join(attributes) + ">"
        return tag

    return re.sub(r"<img\b[^>]*>", enhance, rendered)


def remove_missing_local_images(rendered: str) -> str:
    def replace(match: re.Match) -> str:
        tag = match.group(0)
        source_match = re.search(r'\bsrc=["\']([^"\']+)["\']', tag)
        if not source_match:
            return tag
        source = html.unescape(source_match.group(1))
        parsed = urllib.parse.urlsplit(source)
        if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
            return tag
        path = urllib.parse.unquote(parsed.path)
        if BASE_PATH and path.startswith(f"{BASE_PATH}/"):
            path = path[len(BASE_PATH) :]
        if filesystem_path(CONTENT / path.lstrip("/")).is_file():
            return tag
        MISSING_LOCAL_IMAGE_SOURCES.add(source)
        alt_match = re.search(r'\balt=["\']([^"\']*)["\']', tag)
        return html.escape(html.unescape(alt_match.group(1))) if alt_match else ""

    return re.sub(r"<img\b[^>]*>", replace, rendered)


def rewrite_legacy_post_links(rendered: str) -> str:
    def replace(match: re.Match) -> str:
        raw = html.unescape(match.group(2))
        parsed = urllib.parse.urlsplit(raw)
        if parsed.scheme and (
            parsed.scheme not in {"http", "https"}
            or parsed.netloc.casefold() not in {"matedomokos.hu", "www.matedomokos.hu"}
        ):
            return match.group(0)
        if not parsed.scheme and parsed.netloc:
            return match.group(0)
        path_parts = [urllib.parse.unquote(part) for part in parsed.path.strip("/").split("/") if part]
        is_blog_path = len(path_parts) == 2 and path_parts[0].casefold() == "blog"
        if len(path_parts) != 1 and not is_blog_path:
            return match.group(0)

        route_slug = normalized_route_slug(path_parts[-1])
        key = route_slug.casefold()
        canonical_slug = ""
        route_prefix = ""
        if not is_blog_path and key in MOVED_PAGES:
            return f"{match.group(1)}{html.escape(MOVED_PAGES[key], quote=True)}{match.group(3)}"
        if is_blog_path:
            if key in BLOG_SLUGS:
                canonical_slug = route_slug
            else:
                canonical_slug = BLOG_ALIASES.get(key, "")
            route_prefix = "/blog/"
        elif key in PAGE_ALIASES:
            canonical_slug = PAGE_ALIASES[key]
            route_prefix = "/"
        elif key in PAGE_SLUGS:
            return match.group(0)
        elif key in BLOG_SLUGS:
            canonical_slug = route_slug
            route_prefix = "/blog/"
        else:
            canonical_slug = BLOG_ALIASES.get(key, "")
            route_prefix = "/blog/"
        if not canonical_slug:
            return match.group(0)
        target = urllib.parse.urlunsplit(
            (
                "",
                "",
                f"{route_prefix}{urllib.parse.quote(canonical_slug, safe='-_.~')}/",
                parsed.query,
                parsed.fragment,
            )
        )
        return f"{match.group(1)}{html.escape(target, quote=True)}{match.group(3)}"

    return re.sub(r'(href=["\'])([^"\']+)(["\'])', replace, rendered)


def render_markdown(text: str) -> str:
    rendered = MD.convert(text)
    MD.reset()
    rendered = remove_missing_local_images(rendered)
    rendered = add_responsive_image_attributes(rendered)
    rendered = rewrite_legacy_post_links(rendered)
    if BASE_PATH:
        rendered = re.sub(
            r'((?:href|src)=["\'])/(?!/)',
            lambda match: f"{match.group(1)}{BASE_PATH}/",
            rendered,
        )
        rendered = re.sub(
            r'(srcset=["\'])([^"\']+)(["\'])',
            lambda match: match.group(1)
            + ", ".join(
                f"{prefixed_url(part.strip().rsplit(' ', 1)[0])} "
                f"{part.strip().rsplit(' ', 1)[1]}"
                for part in match.group(2).split(",")
                if part.strip()
            )
            + match.group(3),
            rendered,
        )
    return rendered


def href(path: str) -> str:
    return f"{BASE_PATH}{path}"


def social_meta(meta: dict | None) -> str:
    """Előnézeti adatok a Facebooknak és más megosztó oldalaknak."""
    if not meta:
        return ""
    attr = lambda value: html.escape(str(value), quote=True)
    lines = [
        f'<link rel="canonical" href="{attr(meta["url"])}">',
        '<meta property="og:type" content="article">',
        '<meta property="og:locale" content="hu_HU">',
        f'<meta property="og:site_name" content="{attr(SITE_NAME)}">',
        f'<meta property="og:url" content="{attr(meta["url"])}">',
        f'<meta property="og:title" content="{attr(meta["title"])}">',
        f'<meta property="og:description" content="{attr(meta["description"])}">',
        f'<meta property="og:image" content="{attr(meta["image"])}">',
        '<meta property="og:image:type" content="image/jpeg">',
        f'<meta property="og:image:alt" content="{attr(meta.get("image_alt") or meta["title"])}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{attr(meta["title"])}">',
        f'<meta name="twitter:description" content="{attr(meta["description"])}">',
        f'<meta name="twitter:image" content="{attr(meta["image"])}">',
    ]
    if meta.get("width") and meta.get("height"):
        lines.insert(8, f'<meta property="og:image:width" content="{meta["width"]}">')
        lines.insert(9, f'<meta property="og:image:height" content="{meta["height"]}">')
    if meta.get("published"):
        lines.append(f'<meta property="article:published_time" content="{attr(meta["published"])}">')
    return "\n  ".join(lines)


def layout(title: str, content: str, description: str = "", meta: dict | None = None, head_extra: str = "") -> str:
    safe_title = html.escape(title)
    safe_description = html.escape(description or title, quote=True)
    return f"""<!doctype html>
<html lang="hu">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{safe_description}">
  <title>{safe_title} · {html.escape(SITE_NAME)}</title>
  {social_meta(meta)}
  {head_extra}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gelasio:ital,wght@0,400;0,600;1,400&family=Playfair+Display:wght@500;600;700&display=swap">
  <link rel="stylesheet" href="{href('/assets/site.css')}">
  <link rel="icon" href="{href('/assets/favicon.svg')}" type="image/svg+xml">
  <link rel="alternate" type="application/rss+xml" title="{html.escape(SITE_NAME, quote=True)}" href="{SITE_URL}/feed.xml">
</head>
<body>
  <div class="topbar">
    <a href="{MAIN_SITE_URL}">Az általam alkotott rendszer: MD Megvalósító Rendszer →</a>
  </div>
  <header class="site-header">
    <a class="brand" href="{href('/')}">
      <span class="brand-name">Máté Domokos</span>
      <span class="brand-sub">Személyes oldal · Írások</span>
    </a>
    <nav aria-label="Fő navigáció">
      <a href="{href('/')}">Írások</a>
      <a href="{href('/temak/')}">Témák</a>
      <a href="{href('/rolam/')}">Rólam</a>
      <a href="{href('/online-kozossegeim/')}">Online közösségeim</a>
      <a href="{href('/ajanlott/')}">Ajánlott</a>
      <a href="{href('/kapcsolat/')}">Kapcsolat</a>
    </nav>
  </header>
  <main id="content">{content}</main>
  <footer class="site-footer">
    <a class="footer-brand" href="{href('/')}">Máté Domokos</a>
    <nav aria-label="Lábléc navigáció">
      <a href="{MAIN_SITE_URL}">MD Megvalósító Rendszer</a>
      <a href="{MAIN_SITE_URL}fogalomtar/">MD Fogalomtár</a>
      <a href="{MAIN_SITE_URL}gyakori-kerdesek/">MD Gyakori kérdések</a>
      <a href="{href('/kapcsolat/')}">Kapcsolat</a>
      <a href="{href('/adatkezelesi-tajekoztato/')}">Adatkezelési tájékoztató</a>
      <a href="https://www.facebook.com/mate.domokos/">Facebook</a>
      <a href="https://www.youtube.com/@mateshomebasedbusiness1806">YouTube</a>
    </nav>
    <span>© Máté Domokos 2026 – MD. Minden jog fenntartva.</span>
  </footer>
</body>
</html>
"""


def document_body(document: Document) -> str:
    return render_markdown(document.body)


def date_label(value: str) -> str:
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", value)
    if not match:
        return value
    year, month, day = map(int, match.groups())
    months = (
        "január", "február", "március", "április", "május", "június",
        "július", "augusztus", "szeptember", "október", "november", "december",
    )
    if not 1 <= month <= 12 or not 1 <= day <= 31:
        return value
    return f"{year}. {months[month - 1]} {day}."


def datetime_attribute(value: str) -> str:
    return value.replace(" ", "T", 1)


def normalized_route_slug(value: str) -> str:
    value = urllib.parse.unquote(value)
    value = "".join(
        character
        for character in value
        if unicodedata.category(character) not in {"So", "Sk", "Cf"}
        and character != "\u20e3"
        and not "\ufe00" <= character <= "\ufe0f"
    )
    return re.sub(r"-{2,}", "-", value).strip("-") or "content"


def image_element(
    source: str,
    alt: str,
    width: int = 0,
    height: int = 0,
    srcset: str = "",
    sizes: str = "(max-width: 760px) 100vw, 900px",
    loading: str = "lazy",
) -> str:
    attributes = [
        f'src="{html.escape(prefixed_url(source), quote=True)}"',
        f'alt="{html.escape(alt, quote=True)}"',
        f'loading="{loading}"',
        'decoding="async"',
    ]
    if loading == "eager":
        attributes.append('fetchpriority="high"')
    if width:
        attributes.append(f'width="{width}"')
    if height:
        attributes.append(f'height="{height}"')
    if srcset:
        prefixed_srcset = ", ".join(
            f"{prefixed_url(candidate.strip().rsplit(' ', 1)[0])} "
            f"{candidate.strip().rsplit(' ', 1)[1]}"
            for candidate in srcset.split(",")
            if candidate.strip()
        )
        attributes.append(f'srcset="{html.escape(prefixed_srcset, quote=True)}"')
        attributes.append(f'sizes="{html.escape(sizes, quote=True)}"')
    return f"<img {' '.join(attributes)}>"


def featured_image(document: Document, class_name: str) -> str:
    if not document.image:
        return ""
    image_path = filesystem_path(CONTENT / "images" / document.image)
    if not image_path.is_file():
        raise FileNotFoundError(f"Featured image not found: {image_path}")
    source = f"/images/{document.image}"
    image_info = IMAGE_MANIFEST.get(source, {})
    image = image_element(
        source,
        document.image_alt or document.title,
        image_info.get("width", 0),
        image_info.get("height", 0),
        image_info.get("srcset", ""),
        "(max-width: 699px) 100vw, (max-width: 1399px) 46vw, 640px"
        if class_name == "post-card-image"
        else "(max-width: 760px) 100vw, 900px",
        "eager" if class_name == "featured-image" else "lazy",
    )
    return f'<figure class="{class_name}">{image}</figure>'


def post_card(post: Document) -> str:
    # A kártyán a kép díszítő: a cím ugyanabban a linkben áll, ezért üres alt,
    # különben a képleírás a cikk-kivonat elé kerülne (Google, felolvasók).
    image = featured_image(post, "post-card-image").replace(
        f'alt="{html.escape(post.image_alt or post.title, quote=True)}"', 'alt=""', 1
    )
    post_url = href(f"/blog/{urllib.parse.quote(post.slug, safe='-_.~')}/")
    lead = post.lead or plain_excerpt(post, 220)
    return f"""<article class="post-card">
  <a class="post-card-link" href="{post_url}">{image}<h2>{html.escape(post.title)}</h2></a>
  <p class="post-card-lead">{html.escape(lead)}</p>
  <time datetime="{html.escape(datetime_attribute(post.date))}">{html.escape(date_label(post.date))}</time>
</article>"""


OG_WIDTH = 1200


def share_excerpt(rendered: str, limit: int = 200) -> str:
    text = re.sub(r"<[^>]+>", " ", rendered)
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:–-")
    return cut + "…"


def share_image(post: Document, rendered: str) -> tuple[str, int, int]:
    """JPG előnézeti kép a megosztáshoz (a Facebook az AVIF-et nem mindig mutatja)."""
    candidates = []
    if post.image:
        candidates.append(CONTENT / "images" / post.image)
    for source in re.findall(r'<img[^>]+src="([^"]+)"', rendered):
        path = urllib.parse.unquote(urllib.parse.urlsplit(source).path)
        if BASE_PATH and path.startswith(BASE_PATH):
            path = path[len(BASE_PATH):]
        if path.startswith("/images/"):
            candidates.append(CONTENT / path.lstrip("/"))
    for candidate in candidates:
        source_path = filesystem_path(candidate)
        if not source_path.is_file():
            continue
        try:
            with Image.open(source_path) as picture:
                picture = picture.convert("RGB")
                if picture.width > OG_WIDTH:
                    picture = picture.resize(
                        (OG_WIDTH, round(picture.height * OG_WIDTH / picture.width)),
                        Image.LANCZOS,
                    )
                target = filesystem_path(OUTPUT / "images" / "megosztas" / f"{post.slug}.jpg")
                target.parent.mkdir(parents=True, exist_ok=True)
                picture.save(target, "JPEG", quality=82, optimize=True)
                url = f"{SITE_URL}{BASE_PATH}/images/megosztas/{urllib.parse.quote(post.slug, safe='-_.~')}.jpg"
                return url, picture.width, picture.height
        except (OSError, ValueError):
            continue
    return f"{SITE_URL}{BASE_PATH}/assets/og-default.jpg", 1200, 630


def share_links(url: str, title: str) -> dict[str, str]:
    q = lambda value: urllib.parse.quote(value, safe="")
    both = f"{title} {url}"
    return {
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={q(url)}",
        "whatsapp": f"https://wa.me/?text={q(both)}",
        "viber": f"viber://forward?text={q(both)}",
        "telegram": f"https://t.me/share/url?url={q(url)}&text={q(title)}",
        "x": f"https://x.com/intent/post?url={q(url)}&text={q(title)}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={q(url)}",
        "email": f"mailto:?subject={q(title)}&body={q(both)}",
    }


def share_top(url: str, title: str) -> str:
    links = share_links(url, title)
    return (
        '<div class="share-top">'
        f'<a class="share-btn share-facebook" href="{html.escape(links["facebook"], quote=True)}" '
        'target="_blank" rel="noopener">Megosztom a Facebookon</a>'
        '<a class="share-more" href="#megosztas">További megosztás ↓</a>'
        + ('<a class="share-more" href="#hozzaszolasok">Hozzászólások ↓</a>' if HYVOR_WEBSITE_ID else "")
        + "</div>"
    )


def share_bar(url: str, title: str) -> str:
    links = share_links(url, title)
    labels = [
        ("facebook", "Facebook"),
        ("whatsapp", "WhatsApp"),
        ("viber", "Viber"),
        ("telegram", "Telegram"),
        ("x", "X (Twitter)"),
        ("linkedin", "LinkedIn"),
        ("email", "E-mail"),
    ]
    buttons = "".join(
        f'<a class="share-btn share-{key}" href="{html.escape(links[key], quote=True)}"'
        + ("" if key in {"viber", "email"} else ' target="_blank" rel="noopener"')
        + f">{label}</a>"
        for key, label in labels
    )
    safe_url = html.escape(url, quote=True)
    safe_title = html.escape(title, quote=True)
    return f"""<section class="share" id="megosztas" aria-label="Megosztás">
  <p class="share-title">Ha ez az írás megszólított benned valamit…</p>
  <p class="share-invite">Kövesd és oszd meg – nem kötelességből, hanem igazodásból. Ami a REND-ből a tiéd lett, az akkor marad élő, ha továbbadod. Lehet, hogy valakinek épp ez a néhány sor nyitja meg a saját világos pillanatát.</p>
  <p class="share-label">Kövesd:</p>
  <div class="share-buttons follow-buttons"><a class="share-btn share-facebook" href="https://www.facebook.com/MDMegvalositoRendszer/" target="_blank" rel="noopener">Facebook-oldal</a><a class="share-btn share-youtube" href="https://www.youtube.com/@MD_Megvalosito_Rendszer?sub_confirmation=1" target="_blank" rel="noopener">YouTube-csatorna</a></div>
  <p class="share-label">Oszd meg:</p>
  <div class="share-buttons">{buttons}<button type="button" class="share-btn share-copy" data-url="{safe_url}">Link másolása</button><button type="button" class="share-btn share-native" data-url="{safe_url}" data-title="{safe_title}" hidden>Továbbiak (Messenger, Instagram…)</button></div>
</section>
<script>
document.querySelectorAll('.share-copy').forEach(function (b) {{
  b.addEventListener('click', function () {{
    var done = function () {{ b.textContent = 'Kimásolva ✓'; }};
    if (navigator.clipboard) {{ navigator.clipboard.writeText(b.dataset.url).then(done, function () {{ window.prompt('Másold ki a linket:', b.dataset.url); }}); }}
    else {{ window.prompt('Másold ki a linket:', b.dataset.url); }}
  }});
}});
if (navigator.share) {{
  document.querySelectorAll('.share-native').forEach(function (b) {{
    b.hidden = false;
    b.addEventListener('click', function () {{ navigator.share({{ title: b.dataset.title, url: b.dataset.url }}).catch(function () {{}}); }});
  }});
}}
</script>"""


def image_lightbox() -> str:
    """Kattintásra teljes képernyős nézet a bejegyzés képeihez (borító és szövegközi képek)."""
    return """<div class="lightbox" id="kepnagyito" role="dialog" aria-modal="true" aria-label="Kép teljes képernyőn" hidden>
  <button type="button" class="lightbox-close" aria-label="Bezárás">×</button>
  <div class="lightbox-stage"><img class="lightbox-img" alt=""></div>
  <p class="lightbox-hint">Koppints a képre a nagyításhoz · Esc vagy × a bezáráshoz</p>
</div>
<script>
(function () {
  var box = document.getElementById('kepnagyito');
  if (!box) return;
  var big = box.querySelector('.lightbox-img');
  var closeBtn = box.querySelector('.lightbox-close');
  var opener = null;
  function largest(img) {
    var best = img.currentSrc || img.src, bestW = 0;
    (img.getAttribute('srcset') || '').split(',').forEach(function (part) {
      var bits = part.trim().split(/\\s+/);
      var w = parseInt(bits[1], 10) || 0;
      if (bits[0] && w > bestW) { bestW = w; best = bits[0]; }
    });
    return best;
  }
  function open(img) {
    opener = img;
    big.src = largest(img);
    big.alt = img.alt || '';
    box.classList.remove('is-zoomed');
    box.hidden = false;
    document.documentElement.classList.add('lightbox-open');
    closeBtn.focus();
  }
  function close() {
    box.hidden = true;
    box.classList.remove('is-zoomed');
    big.removeAttribute('src');
    document.documentElement.classList.remove('lightbox-open');
    if (opener) opener.focus();
  }
  document.querySelectorAll('.article .featured-image img, .article .prose img').forEach(function (img) {
    if (img.closest('a')) return;
    img.classList.add('zoomable');
    img.setAttribute('tabindex', '0');
    img.setAttribute('role', 'button');
    img.setAttribute('title', 'Kattints a teljes képernyős nézethez');
    img.addEventListener('click', function () { open(img); });
    img.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(img); }
    });
  });
  big.addEventListener('click', function (e) { e.stopPropagation(); box.classList.toggle('is-zoomed'); });
  closeBtn.addEventListener('click', close);
  box.addEventListener('click', function (e) { if (e.target === box || e.target.classList.contains('lightbox-stage')) close(); });
  document.addEventListener('keydown', function (e) { if (!box.hidden && e.key === 'Escape') close(); });
})();
</script>"""


def closing_question(post: Document) -> str:
    if not post.kerdes:
        return ""
    target = "#hozzaszolasok" if HYVOR_WEBSITE_ID else "#visszajelzes"
    return f"""<aside class="closing-question" aria-label="Kérdés hozzád">
  <p class="closing-question-label">Kérdés hozzád</p>
  <p class="closing-question-text">{html.escape(post.kerdes)}</p>
  <a class="closing-question-link" href="{target}">Írd meg a válaszodat ↓</a>
</aside>"""


def feedback_section(post: Document, url: str) -> str:
    attr = lambda value: html.escape(value, quote=True)
    return f"""<section class="feedback" id="visszajelzes" aria-label="Visszajelzés" data-slug="{attr(post.slug)}" data-title="{attr(post.title)}" data-url="{attr(url)}" data-email="{attr(FEEDBACK_EMAIL)}">
  <p class="feedback-title">Tetszett ez az írás?</p>
  <div class="feedback-vote" role="group" aria-label="Tetszett?">
    <button type="button" class="feedback-btn" data-vote="Tetszett" aria-pressed="false">👍 Tetszett</button>
    <button type="button" class="feedback-btn" data-vote="Nem igazán" aria-pressed="false">🤔 Nem igazán</button>
  </div>
  <form class="feedback-form" hidden>
    <label>Mi tetszett, vagy mi nem – és miért?<textarea name="miert" rows="3"></textarea></label>
    <label>Mi hiányzott? Mire kerested még a választ?<textarea name="hiany" rows="3"></textarea></label>
    <label>Válaszod a cikk végi kérdésre:<textarea name="valasz" rows="3"></textarea></label>
    <label>A neved (nem kötelező):<input type="text" name="nev" autocomplete="name"></label>
    <label>Az e-mail címed, ha választ szeretnél (nem kötelező):<input type="email" name="email" autocomplete="email"></label>
    <input type="text" name="_honey" tabindex="-1" autocomplete="off" style="display:none">
    <button type="submit" class="share-btn feedback-send">Elküldöm a visszajelzésem</button>
    <p class="feedback-note">Minden visszajelzést elolvasok, és a gyakori kérdésekre írásban is válaszolok. Az adatkezelésről az <a href="/adatkezelesi-tajekoztato/">adatkezelési tájékoztatóban</a> olvashatsz.</p>
    <p class="feedback-error" hidden>Most nem sikerült elküldeni. <a class="feedback-mailto" href="#">Küldd el inkább e-mailben</a>, vagy próbáld újra kicsit később.</p>
  </form>
  <p class="feedback-thanks" hidden>Köszönöm, hogy megírtad! Megérkezett. Minden visszajelzés segít, hogy a következő írás még pontosabban szóljon.</p>
</section>
<script>
document.querySelectorAll('.feedback').forEach(function (box) {{
  var form = box.querySelector('.feedback-form'), vote = '';
  box.querySelectorAll('.feedback-btn').forEach(function (b) {{
    b.addEventListener('click', function () {{
      vote = b.dataset.vote;
      box.querySelectorAll('.feedback-btn').forEach(function (o) {{ o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); }});
      form.hidden = false;
      try {{ localStorage.setItem('md-vote-' + box.dataset.slug, vote); }} catch (e) {{}}
    }});
  }});
  function openAnswer() {{
    form.hidden = false;
    box.querySelector('.feedback-thanks').hidden = true;
    setTimeout(function () {{ form.elements.valasz.focus({{ preventScroll: true }}); box.scrollIntoView({{ behavior: 'smooth', block: 'start' }}); }}, 50);
  }}
  document.querySelectorAll('a.closing-question-link[href="#visszajelzes"]').forEach(function (a) {{
    a.addEventListener('click', function (ev) {{ ev.preventDefault(); history.replaceState(null, '', '#visszajelzes'); openAnswer(); }});
  }});
  if (location.hash === '#visszajelzes') openAnswer();
  form.addEventListener('submit', function (ev) {{
    ev.preventDefault();
    var f = form.elements;
    var body = 'Írás: ' + box.dataset.title + '\\n' + box.dataset.url + '\\n\\nTetszett? ' + (vote || '-') +
      '\\n\\nMi tetszett / mi nem és miért:\\n' + f.miert.value + '\\n\\nMi hiányzott:\\n' + f.hiany.value +
      '\\n\\nVálasz a kérdésre:\\n' + f.valasz.value + '\\n\\nNév: ' + f.nev.value + '\\nE-mail: ' + f.email.value + '\\n';
    var mailto = 'mailto:' + box.dataset.email + '?subject=' + encodeURIComponent('Visszajelzés: ' + box.dataset.title) + '&body=' + encodeURIComponent(body);
    if (f._honey.value) return;
    var btn = form.querySelector('.feedback-send'), err = form.querySelector('.feedback-error');
    btn.disabled = true; btn.textContent = 'Küldés…'; err.hidden = true;
    var data = {{
      _subject: 'Blog-visszajelzés: ' + box.dataset.title,
      _template: 'table', _captcha: 'false',
      'Írás': box.dataset.title, 'Link': box.dataset.url, 'Tetszett?': vote || '-',
      'Mi tetszett / mi nem, miért': f.miert.value, 'Mi hiányzott': f.hiany.value,
      'Válasz a kérdésre': f.valasz.value, 'Név': f.nev.value, 'email': f.email.value
    }};
    fetch('https://formsubmit.co/ajax/' + box.dataset.email, {{
      method: 'POST', headers: {{ 'Content-Type': 'application/json', 'Accept': 'application/json' }}, body: JSON.stringify(data)
    }}).then(function (r) {{ return r.json(); }}).then(function (j) {{
      if (String(j.success) !== 'true') throw new Error(j.message || 'hiba');
      form.hidden = true; box.querySelector('.feedback-thanks').hidden = false;
    }}).catch(function () {{
      err.hidden = false; err.querySelector('.feedback-mailto').href = mailto;
      btn.disabled = false; btn.textContent = 'Elküldöm a visszajelzésem';
    }});
  }});
}});
</script>"""


def comments_section(post: Document, url: str) -> str:
    if not HYVOR_WEBSITE_ID:
        return ""
    attr = lambda value: html.escape(value, quote=True)
    return f"""<section class="comments" id="hozzaszolasok" aria-label="Hozzászólások">
  <h2>Hozzászólások</h2>
  <p class="comments-note">Írd meg a gondolataidat! Regisztráció nem kell, elég egy név. A hozzászólások jóváhagyás után jelennek meg. Az adatkezelésről az <a href="{href('/adatkezelesi-tajekoztato/')}">adatkezelési tájékoztatóban</a> olvashatsz.</p>
  <hyvor-talk-comments website-id="{attr(HYVOR_WEBSITE_ID)}" page-id="{attr(post.slug)}" page-title="{attr(post.title)}" page-url="{attr(url)}" language="hu" loading="lazy"></hyvor-talk-comments>
  <script async src="https://talk.hyvor.com/embed/embed.js" type="module"></script>
</section>"""


def post_href(post: Document) -> str:
    return href(f"/blog/{urllib.parse.quote(post.slug, safe='-_.~')}/")


def clean_title(title: str) -> str:
    """Cím a keresőknek: a …(?)… jelzés, emojik és szélső idézőjelek nélkül."""
    text = re.sub(r"[.…]+\s*\(\?\)\s*[.…]*", "", title)
    text = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]", "", text)
    text = text.strip().strip('"„”“').strip().rstrip(",:")
    return re.sub(r"\s+", " ", text) or title


def search_title(post: Document) -> str:
    """A böngészőfül és a Google-találat címe: a bejegyzés címe + a fő keresett kifejezés."""
    base = clean_title(post.title)
    if post.kereses:
        phrase = post.kereses[0]
        if phrase.casefold() not in base.casefold():
            return f"{base} – {phrase[0].upper()}{phrase[1:]}"
    return base


def audience_box(post: Document) -> str:
    if not post.kinek:
        return ""
    topic = ""
    if post.tema in TOPICS:
        topic = (
            f'<a class="audience-topic" href="{href(f"/tema/{post.tema}/")}">'
            f"Téma: {html.escape(TOPICS[post.tema][0])} →</a>"
        )
    return f"""<aside class="audience" aria-label="Kinek szól ez az írás">
  <p class="audience-label">Kinek szól?</p>
  <p class="audience-text">Neked, ha {html.escape(post.kinek)}.</p>
  {topic}
</aside>"""


def related_posts(post: Document, posts: list[Document], limit: int = 3) -> list[Document]:
    same = [p for p in posts if p.tema == post.tema and p.slug != post.slug]
    position = {p.slug: i for i, p in enumerate(posts)}
    me = position[post.slug]
    same.sort(key=lambda p: abs(position[p.slug] - me))
    return same[:limit]


def related_section(post: Document, posts: list[Document]) -> str:
    related = related_posts(post, posts)
    if not related:
        return ""
    items = "".join(
        f'<li><a href="{post_href(p)}">{html.escape(p.title)}</a>'
        + (f'<span>Neked, ha {html.escape(p.kinek)}.</span>' if p.kinek else "")
        + "</li>"
        for p in related
    )
    more = ""
    if post.tema in TOPICS:
        more = (
            f'<a class="related-more" href="{href(f"/tema/{post.tema}/")}">'
            f"Minden írás ebben a témában: {html.escape(TOPICS[post.tema][0])} →</a>"
        )
    return f"""<section class="related" aria-label="Neked ajánlom még">
  <p class="related-title">Ha ez az írás neked szólt, ezeket is neked ajánlom:</p>
  <ul>{items}</ul>
  {more}
</section>"""


def article_jsonld(post: Document, url: str, description: str, image: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": clean_title(post.title)[:110],
        "description": description,
        "url": url,
        "mainEntityOfPage": url,
        "image": image,
        "datePublished": datetime_attribute(post.date),
        "inLanguage": "hu",
        "author": {"@type": "Person", "name": "Máté Domokos", "url": f"{SITE_URL}/rolam/"},
        "publisher": {"@type": "Person", "name": "Máté Domokos"},
    }
    if post.kereses:
        data["keywords"] = ", ".join(post.kereses)
    if post.tema in TOPICS:
        data["articleSection"] = TOPICS[post.tema][0]
    if post.kinek:
        data["audience"] = {"@type": "Audience", "audienceType": f"Akinek: {post.kinek}"}
    text = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">{text}</script>'


def write_topic_pages(posts: list[Document]) -> list[str]:
    urls = []
    cards = []
    for slug, (name, intro) in TOPICS.items():
        topic_posts = [p for p in posts if p.tema == slug]
        if not topic_posts:
            continue
        cards.append(
            f'<li><a href="{href(f"/tema/{slug}/")}"><strong>{html.escape(name)}</strong>'
            f"<span>{html.escape(intro)}</span><em>{len(topic_posts)} írás</em></a></li>"
        )
        content = f"""<section class="blog-archive topic-page">
  <p class="topic-back"><a href="{href('/temak/')}">← Minden téma</a></p>
  <h1>{html.escape(name)}</h1>
  <p class="topic-intro">{html.escape(intro)}</p>
  <div class="post-grid">{''.join(post_card(p) for p in topic_posts)}</div>
</section>"""
        write_page(OUTPUT / "tema" / slug / "index.html", name, content, intro)
        urls.append(f"/tema/{slug}/")
    content = f"""<section class="page-content topics">
  <h1>Témák – mit keresel most?</h1>
  <p class="topic-intro">Válaszd ki, mi foglalkoztat most a leginkább: ott találod azokat az írásokat, amelyek neked szólnak.</p>
  <ul class="topic-list">{''.join(cards)}</ul>
</section>"""
    write_page(
        OUTPUT / "temak" / "index.html",
        "Témák",
        content,
        "Máté Domokos írásai témák szerint: önismeret, ego és elme, felelősség, kapcsolatok, hit, meditáció, magyarság és az MD Megvalósító Rendszer.",
    )
    urls.append("/temak/")
    return urls


def write_sitemap(paths: list[tuple[str, str]]) -> None:
    rows = "".join(
        f"  <url><loc>{html.escape(SITE_URL + href(path))}</loc>"
        + (f"<lastmod>{html.escape(lastmod)}</lastmod>" if lastmod else "")
        + "</url>\n"
        for path, lastmod in paths
    )
    filesystem_path(OUTPUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + rows
        + "</urlset>\n",
        encoding="utf-8",
    )
    filesystem_path(OUTPUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}{BASE_PATH}/sitemap.xml\n",
        encoding="utf-8",
    )


def post_navigation(posts: list[Document], index: int) -> str:
    links = []
    if index < len(posts) - 1:
        older = posts[index + 1]
        href_value = href(
            f"/blog/{urllib.parse.quote(older.slug, safe='-_.~')}/"
        )
        links.append(
            f'<a rel="prev" href="{href_value}">← {html.escape(older.title)}</a>'
        )
    if index > 0:
        newer = posts[index - 1]
        href_value = href(
            f"/blog/{urllib.parse.quote(newer.slug, safe='-_.~')}/"
        )
        links.append(
            f'<a rel="next" href="{href_value}">{html.escape(newer.title)} →</a>'
        )
    if not links:
        return ""
    return (
        '<nav class="post-navigation" aria-label="Bejegyzés navigáció">'
        + "".join(links)
        + "</nav>"
    )


def pagination(current_page: int, total_pages: int) -> str:
    if total_pages < 2:
        return ""
    links = []
    for number in range(1, total_pages + 1):
        target = "/" if number == 1 else f"/blog/page/{number}/"
        if number == current_page:
            links.append(
                f'<span class="current-page" aria-current="page">{number}</span>'
            )
        else:
            links.append(f'<a href="{href(target)}">{number}</a>')
    previous = ""
    if current_page > 1:
        target = "/" if current_page == 2 else f"/blog/page/{current_page - 1}/"
        previous = f'<a class="page-direction" rel="prev" href="{href(target)}">← Újabb bejegyzések</a>'
    following = ""
    if current_page < total_pages:
        following = (
            f'<a class="page-direction" rel="next" '
            f'href="{href(f"/blog/page/{current_page + 1}/")}">Régebbi bejegyzések →</a>'
        )
    return (
        '<nav class="pagination" aria-label="Blog oldalak">'
        f"{previous}<span class=\"page-numbers\">{''.join(links)}</span>{following}"
        "</nav>"
    )


def write_page(
    path: Path,
    title: str,
    content: str,
    description: str = "",
    meta: dict | None = None,
    head_extra: str = "",
) -> None:
    path = filesystem_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(layout(title, content, description, meta, head_extra), encoding="utf-8")


def write_redirect(path: Path, title: str, target: str) -> None:
    target_url = target if target.startswith(("http://", "https://")) else href(target)
    safe_target = html.escape(target_url, quote=True)
    content = f"""<!doctype html>
<html lang="hu">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="0; url={safe_target}">
  <link rel="canonical" href="{safe_target}">
  <title>{html.escape(title)} · Máté Domokos</title>
</head>
<body>
  <p>Az oldal új címre költözött. <a href="{safe_target}">Tovább</a></p>
  <script>location.replace({json.dumps(target_url)});</script>
</body>
</html>
"""
    path = filesystem_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def filesystem_path(path: Path) -> Path:
    if os.name == "nt" and not str(path).startswith("\\\\?\\"):
        return Path("\\\\?\\" + str(path.resolve()))
    return path


def build_aliases(
    items: list[Document], canonical_slugs: set[str], label: str
) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for item in items:
        if not item.alias:
            continue
        alias = normalized_route_slug(item.alias)
        key = alias.casefold()
        if key == item.slug.casefold():
            continue
        if key in canonical_slugs:
            raise ValueError(f"{label} alias {item.alias!r} collides with a canonical URL")
        if key in aliases:
            raise ValueError(f"Duplicate {label} alias: {item.alias!r}")
        aliases[key] = item.slug
    return aliases


def plain_excerpt(document: Document, limit: int = 280) -> str:
    text = re.sub(r"<[^>]+>", " ", render_markdown(document.body))
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:–-") + "…"


def rfc822_date(value: str) -> str:
    from datetime import datetime
    from email.utils import format_datetime
    from zoneinfo import ZoneInfo

    try:
        moment = datetime.strptime(value[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            moment = datetime.strptime(value[:10], "%Y-%m-%d")
        except ValueError:
            return ""
    return format_datetime(moment.replace(tzinfo=ZoneInfo("Europe/Budapest")))


def write_feed(path: Path, posts: list[Document]) -> None:
    items = []
    for post in posts:
        link = f"{SITE_URL}/blog/{urllib.parse.quote(post.slug, safe='-_.~')}/"
        published = rfc822_date(post.date)
        items.append(
            "  <item>\n"
            f"    <title>{html.escape(post.title)}</title>\n"
            f"    <link>{html.escape(link)}</link>\n"
            f"    <guid isPermaLink=\"true\">{html.escape(link)}</guid>\n"
            + (f"    <pubDate>{published}</pubDate>\n" if published else "")
            + f"    <description>{html.escape(post.lead or plain_excerpt(post))}</description>\n"
            "  </item>"
        )
    last_build = rfc822_date(posts[0].date) if posts else ""
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "<channel>\n"
        f"  <title>{html.escape(SITE_NAME)}</title>\n"
        f"  <link>{SITE_URL}/blog/</link>\n"
        f'  <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>\n'
        "  <description>Máté Domokos írásai az MD Megvalósító Rendszer útjáról.</description>\n"
        "  <language>hu</language>\n"
        + (f"  <lastBuildDate>{last_build}</lastBuildDate>\n" if last_build else "")
        + "\n".join(items)
        + "\n</channel>\n</rss>\n"
    )
    filesystem_path(path).write_text(feed, encoding="utf-8")


def main() -> None:
    global BLOG_ALIASES, BLOG_SLUGS, IMAGE_MANIFEST, PAGE_ALIASES, PAGE_SLUGS
    if not CONTENT.is_dir():
        raise FileNotFoundError(f"Content directory not found: {CONTENT}")
    if filesystem_path(IMAGE_MANIFEST_PATH).exists():
        IMAGE_MANIFEST = json.loads(
            filesystem_path(IMAGE_MANIFEST_PATH).read_text(encoding="utf-8")
        )
    pages, posts, root_page = documents()
    BLOG_SLUGS = {post.slug.casefold() for post in posts}
    PAGE_SLUGS = {page.slug.casefold() for page in pages if page.slug != "blog"}
    BLOG_ALIASES = build_aliases(posts, BLOG_SLUGS, "Blog")
    PAGE_ALIASES = build_aliases(
        [page for page in pages if page.slug != "blog"], PAGE_SLUGS, "Page"
    )
    if not posts:
        raise FileNotFoundError(f"No blog posts found in {CONTENT / 'blog'}")

    if OUTPUT.exists():
        shutil.rmtree(filesystem_path(OUTPUT))
    (OUTPUT / "assets").mkdir(parents=True)
    (OUTPUT / "images").mkdir(parents=True)
    site_assets = Path(__file__).resolve().parents[1] / "assets"
    for asset in site_assets.rglob("*"):
        if asset.is_file():
            target = filesystem_path(OUTPUT / "assets" / asset.relative_to(site_assets))
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(filesystem_path(asset), target)
    assets_root = filesystem_path(CONTENT / "assets")
    for asset in assets_root.rglob("*"):
        if asset.is_file():
            target = filesystem_path(OUTPUT / "assets" / asset.relative_to(assets_root))
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(filesystem_path(asset), target)
    for image in (CONTENT / "images").rglob("*"):
        if image.is_file() and image.name != "_manifest.json":
            target = OUTPUT / "images" / image.relative_to(CONTENT / "images")
            filesystem_path(target).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(filesystem_path(image), filesystem_path(target))


    blog_page = next((page for page in pages if page.slug == "blog"), None)
    blog_intro = document_body(blog_page) if blog_page else ""
    per_page = 20
    total_pages = math.ceil(len(posts) / per_page)
    for current_page in range(1, total_pages + 1):
        page_posts = posts[(current_page - 1) * per_page : current_page * per_page]
        archive = f"""<section class="blog-archive">
  {blog_intro}
  <div class="post-grid">{''.join(post_card(post) for post in page_posts)}</div>
  {pagination(current_page, total_pages)}
</section>
"""
        archive_path = (
            OUTPUT / "blog" / "index.html"
            if current_page == 1
            else OUTPUT / "blog" / "page" / str(current_page) / "index.html"
        )
        write_page(archive_path, "Írások", archive)
        if current_page == 1:
            write_page(OUTPUT / "index.html", "Írások", archive)
    write_feed(OUTPUT / "feed.xml", posts[:FEED_SIZE])

    for page in pages:
        if page.slug == "blog":
            continue
        content = f"""<article class="page-content">
  <h1>{html.escape(page.title)}</h1>
  <div class="prose">{document_body(page)}</div>
</article>"""
        write_page(OUTPUT / page.slug / "index.html", page.title, content, page.title)
        if page.alias and page.alias.casefold() != page.slug.casefold():
            write_redirect(
                OUTPUT / page.alias / "index.html",
                page.title,
                f"/{urllib.parse.quote(page.slug, safe='-_.~')}/",
            )

    # A CONTENT/archivum/ alatti írások nem jelennek meg (pl. a PPH-hoz kötődők,
    # 2026. október); a régi címük az Írások kezdőlapjára visz.
    for archived in sorted((CONTENT / "archivum").rglob("*.md")):
        if archived.stem.casefold() in BLOG_SLUGS:
            raise ValueError(f"Archived post slug is also published: {archived.stem}")
        write_redirect(OUTPUT / "blog" / archived.stem / "index.html", "Archivált írás", "/")

    for old_slug, target in MOVED_PAGES.items():
        if old_slug.casefold() in BLOG_SLUGS:
            raise ValueError(f"Moved page slug collides with a blog post: {old_slug}")
        write_redirect(OUTPUT / old_slug / "index.html", "Átköltözött oldal", target)

    for index, post in enumerate(posts):
        body = document_body(post)
        post_url = f"{SITE_URL}{BASE_PATH}/blog/{urllib.parse.quote(post.slug, safe='-_.~')}/"
        image_url, image_width, image_height = share_image(post, body)
        excerpt = post.lead or share_excerpt(body) or post.title
        content = f"""<article class="page-content article">
  {featured_image(post, "featured-image")}
  <header class="article-header"><h1>{html.escape(post.title)}</h1>{audience_box(post)}{share_top(post_url, post.title)}</header>
  <div class="prose">{body}</div>
  {closing_question(post)}
  {related_section(post, posts)}
  {feedback_section(post, post_url)}
  {share_bar(post_url, post.title)}
  {comments_section(post, post_url)}
  {post_navigation(posts, index)}
</article>
{image_lightbox()}"""
        write_page(
            OUTPUT / "blog" / post.slug / "index.html",
            search_title(post),
            content,
            excerpt,
            {
                "url": post_url,
                "title": post.title,
                "description": excerpt,
                "image": image_url,
                "width": image_width,
                "height": image_height,
                "image_alt": post.image_alt,
                "published": datetime_attribute(post.date),
            },
            article_jsonld(post, post_url, excerpt, image_url),
        )
        if post.alias and post.alias.casefold() != post.slug.casefold():
            old_route = OUTPUT / "blog" / post.alias / "index.html"
            write_redirect(
                old_route,
                post.title,
                f"/blog/{urllib.parse.quote(post.slug, safe='-_.~')}/",
            )

    topic_urls = write_topic_pages(posts)
    sitemap = [("/", posts[0].date[:10])]
    sitemap += [(f"/blog/page/{n}/", "") for n in range(2, total_pages + 1)]
    sitemap += [(url, "") for url in topic_urls]
    sitemap += [
        (f"/{urllib.parse.quote(page.slug, safe='-_.~')}/", "")
        for page in pages
        if page.slug != "blog"
    ]
    sitemap += [
        (f"/blog/{urllib.parse.quote(post.slug, safe='-_.~')}/", post.date[:10])
        for post in posts
    ]
    write_sitemap(sitemap)

    page_count = (
        1
        + total_pages
        + len(pages)
        - 1
        + len(posts)
        + len(PAGE_ALIASES)
        + len(MOVED_PAGES)
        + len(BLOG_ALIASES)
    )
    print(
        f"Built {page_count} pages ({total_pages} blog archive pages) in {OUTPUT}"
    )
    if MISSING_LOCAL_IMAGE_SOURCES:
        examples = ", ".join(
            sorted(
                Path(urllib.parse.urlsplit(source).path).name
                for source in MISSING_LOCAL_IMAGE_SOURCES
            )[:5]
        )
        print(
            f"Warning: omitted {len(MISSING_LOCAL_IMAGE_SOURCES)} unavailable local image sources "
            f"from Markdown (examples: {examples})"
        )


if __name__ == "__main__":
    main()
