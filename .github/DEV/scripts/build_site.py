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


ROOT = Path(__file__).resolve().parents[3]
CONTENT = ROOT / "CONTENT"
OUTPUT = ROOT / "dist"
BASE_PATH = os.environ.get("SITE_BASE_PATH", "").rstrip("/")
SITE_URL = os.environ.get("SITE_URL", "https://blog.mdmegvalositorendszer.hu").rstrip("/")
MAIN_SITE_URL = "https://mdmegvalositorendszer.hu/"
SITE_NAME = "MD Megvalósító Rendszer – Blog"
# Az önálló oldalak a központi WordPress-oldalra költöztek; a régi címeik oda irányítanak.
MOVED_PAGES = {
    "rolam": f"{MAIN_SITE_URL}rolam/",
    "kapcsolat": f"{MAIN_SITE_URL}kapcsolat/",
    "alap": f"{MAIN_SITE_URL}alap/",
    "alapozas": f"{MAIN_SITE_URL}alap/",
    "ajanlott": f"{MAIN_SITE_URL}ajanlott/",
    "online-kozossegeim": f"{MAIN_SITE_URL}online-kozossegeim/",
    "kozosseg": f"{MAIN_SITE_URL}online-kozossegeim/",
    "miert-jott-letre-az-md-megvalosito-rendszer": f"{MAIN_SITE_URL}miert-jott-letre-az-md-megvalosito-rendszer/",
    "adatkezelesi-tajekoztato": f"{MAIN_SITE_URL}adatkezelesi-tajekoztato/",
    "kezdolap": MAIN_SITE_URL,
    "home": MAIN_SITE_URL,
    "mdhu-megvalosito-rendszer": MAIN_SITE_URL,
    "mdhu_megvalosito_rendszer": MAIN_SITE_URL,
}
FEED_SIZE = 20
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


def layout(title: str, content: str, description: str = "") -> str:
    safe_title = html.escape(title)
    safe_description = html.escape(description or title, quote=True)
    return f"""<!doctype html>
<html lang="hu">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{safe_description}">
  <title>{safe_title} · {html.escape(SITE_NAME)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gelasio:ital,wght@0,400;0,600;1,400&family=Playfair+Display:wght@500;600;700&display=swap">
  <link rel="stylesheet" href="{href('/assets/site.css')}">
  <link rel="icon" href="{href('/assets/favicon.svg')}" type="image/svg+xml">
  <link rel="alternate" type="application/rss+xml" title="{html.escape(SITE_NAME, quote=True)}" href="{SITE_URL}/feed.xml">
</head>
<body>
  <div class="topbar">
    <a href="{MAIN_SITE_URL}">Tovább az MD Megvalósító Rendszer oldalára →</a>
  </div>
  <header class="site-header">
    <a class="brand" href="{href('/')}">
      <span class="brand-name">Blog</span>
      <span class="brand-sub">MD Megvalósító Rendszer · Újjászületési és Helyreállítási Program</span>
    </a>
    <nav aria-label="Fő navigáció">
      <a href="{MOVED_PAGES['rolam']}">Rólam</a>
      <a href="{MOVED_PAGES['kapcsolat']}">Kapcsolat</a>
    </nav>
  </header>
  <main id="content">{content}</main>
  <footer class="site-footer">
    <a class="footer-brand" href="{MAIN_SITE_URL}">MD Megvalósító Rendszer</a>
    <nav aria-label="Lábléc navigáció">
      <a href="{MOVED_PAGES['kapcsolat']}">Kapcsolat</a>
      <a href="{MOVED_PAGES['adatkezelesi-tajekoztato']}">Adatkezelési tájékoztató</a>
      <a href="{SITE_URL}/feed.xml">RSS</a>
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
    image = featured_image(post, "post-card-image")
    post_url = href(f"/blog/{urllib.parse.quote(post.slug, safe='-_.~')}/")
    return f"""<article class="post-card">
  <a class="post-card-link" href="{post_url}">{image}<h2>{html.escape(post.title)}</h2></a>
  <time datetime="{html.escape(datetime_attribute(post.date))}">{html.escape(date_label(post.date))}</time>
</article>"""


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


def write_page(path: Path, title: str, content: str, description: str = "") -> None:
    path = filesystem_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(layout(title, content, description), encoding="utf-8")


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
            + f"    <description>{html.escape(plain_excerpt(post))}</description>\n"
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
        write_page(archive_path, "Blog", archive)
        if current_page == 1:
            write_page(OUTPUT / "index.html", "Blog", archive)
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

    for old_slug, target in MOVED_PAGES.items():
        if old_slug.casefold() in BLOG_SLUGS:
            raise ValueError(f"Moved page slug collides with a blog post: {old_slug}")
        write_redirect(OUTPUT / old_slug / "index.html", "Átköltözött oldal", target)

    for index, post in enumerate(posts):
        content = f"""<article class="page-content article">
  {featured_image(post, "featured-image")}
  <header class="article-header"><h1>{html.escape(post.title)}</h1></header>
  <div class="prose">{document_body(post)}</div>
  {post_navigation(posts, index)}
</article>"""
        write_page(
            OUTPUT / "blog" / post.slug / "index.html",
            post.title,
            content,
            post.title,
        )
        if post.alias and post.alias.casefold() != post.slug.casefold():
            old_route = OUTPUT / "blog" / post.alias / "index.html"
            write_redirect(
                old_route,
                post.title,
                f"/blog/{urllib.parse.quote(post.slug, safe='-_.~')}/",
            )

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
