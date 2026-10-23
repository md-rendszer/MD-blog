# Repository Instructions

<<<<<<< HEAD
This repository contains a Hungarian-language static archive of Máté Domokos's website and blog. Keep the website's user-facing content in Hungarian; write these agent instructions in English.

<<<<<<< HEAD
<<<<<<< HEAD
Before a task, read the relevant project guidance:
=======
- A blog a központi oldal (https://mdmegvalositorendszer.hu/, WordPress) része, de a képek miatt itt, GitHub Pages-en fut. A fejléc és a lábléc a központi oldalra mutat.
=======
- A blog a központi oldal (https://mdmegvalositorendszer.hu/, WordPress) része, de a képek miatt itt, GitHub Pages-en fut. A fejléc címe „Blog”, és a gyökérre (`/`) mutat; felette egy topbar visz a központi oldalra. A menüben nincs „Főoldal” és „Blog” link, mert a blog kezdőlapja maga a bejegyzéslista.
<<<<<<< HEAD
>>>>>>> addec46 (Fejléc: Blog cím, topbar a központi oldalra, Főoldal és Blog link nélkül)
- Célcím: https://blog.mdmegvalositorendszer.hu/ (DNS: `blog` CNAME → `md-rendszer.github.io`, a GitHubon Settings → Pages → Custom domain). Átmenetileg még a blog.matedomokos.hu cím is élhet. A `pages.yml`-ben a `SITE_BASE_PATH` üres; ne állítsd vissza `/MD-blog`-ra.
- Bejegyzés URL-je: `https://blog.mdmegvalositorendszer.hu/blog/<fájlnév kiterjesztés nélkül>/`
- Az önálló oldalak (Kapcsolat, ALAP, AJÁNLOTT, Online Közösségeim, Miért jött létre…, Adatkezelési tájékoztató, Kezdőlap) itt, a `CONTENT/*.md` fájlokból épülnek. Kivétel a Rólam: az a központi WordPress-oldalon él, a régi címe a `build_site.py` `MOVED_PAGES` listája alapján oda irányít.
- A gyökér (`/`) a blog-archívum első oldala. A `feed.xml` RSS-hírcsatorna (legfrissebb 20 bejegyzés) táplálja a központi WordPress-főoldal „Legfrissebb írások” blokkját, ezért a formátumát ne törd el.
>>>>>>> 0869c03 (Önálló oldalak átköltöztetése a központi oldalra, régi címek átirányítása)
=======
=======
Ez a repó Máté Domokos (Domi) személyes weboldala (matedomokos.hu): Markdown-fájlokból épülő statikus oldal, amely GitHub Pages-en fut.

- Felosztás (2026. október): a matedomokos.hu Domi maga, emberként (Rólam, Írások, Online közösségeim, Ajánlott, Kapcsolat); az mdmegvalositorendszer.hu (WordPress) az általa alkotott rendszer. A fejléc címe „Máté Domokos”, és a gyökérre (`/`) mutat; felette egy topbar visz a rendszer oldalára. Menü: Írások (`/`) · Rólam · Online közösségeim · Ajánlott · Kapcsolat.
- Domi 2026 októbertől senkit nem hív meg a PPH Nyílt Akadémiára: PPH-meghívót, partnerlinket (`vez=1181333`) ne tegyél be sehová.
>>>>>>> 7c34a17 (Személyes oldal: Rólam ide költözött, rendszeroldalak átirányítva, PPH-meghívók ki)
- Cím: https://matedomokos.hu/ (DNS a Sybellnél: `@` A-rekordok → `185.199.108–111.153`, AAAA → `2606:50c0:8000–8003::153`, `www` CNAME → `md-rendszer.github.io`; a Zoho MX- és TXT-rekordokhoz nem kell nyúlni. GitHubon Settings → Pages → Custom domain: `matedomokos.hu`). A webcímet a `pages.yml` `SITE_URL` változója adja. A `SITE_BASE_PATH` üres; ne állítsd vissza `/MD-blog`-ra.
- Bejegyzés URL-je: `https://matedomokos.hu/blog/<fájlnév kiterjesztés nélkül>/`
- Az önálló oldalak (Rólam, Kapcsolat, AJÁNLOTT, Online Közösségeim, Adatkezelési tájékoztató, Kezdőlap) itt, a `CONTENT/*.md` fájlokból épülnek. A rendszerhez tartozó oldalak (ALAP, Miért jött létre…, MDHU Megvalósító Rendszer) a központi WordPress-oldalon élnek; a régi címük a `build_site.py` `MOVED_PAGES` listája alapján oda irányít.
- A gyökér (`/`) a blog-archívum első oldala. A `feed.xml` RSS-hírcsatorna (legfrissebb 20 bejegyzés, `https://matedomokos.hu/feed.xml`) táplálja a központi WordPress-főoldal „Legfrissebb írások” blokkját, ezért a formátumát ne törd el. A láblécben nincs látható RSS-link, csak a `<head>`-ben.
>>>>>>> d7c546a (Webcím: matedomokos.hu; RSS-link ki a láblécből (a hírcsatorna marad))

- [Content and language rules](.agents/language-and-content.md)
- [Build, scripts, and validation](.agents/development.md)
- [Documentation and changelog](.agents/documentation.md)
- [Git and release workflow](.agents/git-and-release.md)
- [System overview](./_docs/README.md)

<<<<<<< HEAD
Shared skills are maintained in the root `.skills/` folder; Claude Code skill entries under `.claude/skills/` point back to those canonical instructions.
=======
| Hely | Tartalom |
| --- | --- |
| `CONTENT/blog/<év>/<slug>.md` | Blogbejegyzések, évenkénti mappában |
| `CONTENT/*.md` | Önálló oldalak; `blog.md` a blog-archívum bevezetője, `_index.md` jelenleg nem jelenik meg (a gyökér a bejegyzéslista) |
| `CONTENT/images/<év>/` | Képek AVIF formátumban, három méretben |
| `CONTENT/images/_manifest.json` | Képméretek és `srcset` minden képváltozathoz |
| `CONTENT/assets/` | CSS, favicon |
| `.github/build_site.py` | Az oldalépítő szkript (kimenet: `dist/`, nincs verziókezelve) |
| `.github/workflows/pages.yml` | Push a `main` ágra → build és közzététel |
>>>>>>> 0869c03 (Önálló oldalak átköltöztetése a központi oldalra, régi címek átirányítása)

Do not edit `CONTENT/` unless the user explicitly requests content changes. Preserve existing public post slugs and URLs. Never include `dist/` or generated Python cache files in commits.
