# Repository Instructions

This repository contains a Hungarian-language static archive of Máté Domokos's website and blog. Keep the website's user-facing content in Hungarian; write these agent instructions in English.

<<<<<<< HEAD
<<<<<<< HEAD
Before a task, read the relevant project guidance:
=======
- A blog a központi oldal (https://mdmegvalositorendszer.hu/, WordPress) része, de a képek miatt itt, GitHub Pages-en fut. A fejléc és a lábléc a központi oldalra mutat.
=======
- A blog a központi oldal (https://mdmegvalositorendszer.hu/, WordPress) része, de a képek miatt itt, GitHub Pages-en fut. A fejléc címe „Blog”, és a gyökérre (`/`) mutat; felette egy topbar visz a központi oldalra. A menüben nincs „Főoldal” és „Blog” link, mert a blog kezdőlapja maga a bejegyzéslista.
>>>>>>> addec46 (Fejléc: Blog cím, topbar a központi oldalra, Főoldal és Blog link nélkül)
- Célcím: https://blog.mdmegvalositorendszer.hu/ (DNS: `blog` CNAME → `md-rendszer.github.io`, a GitHubon Settings → Pages → Custom domain). Átmenetileg még a blog.matedomokos.hu cím is élhet. A `pages.yml`-ben a `SITE_BASE_PATH` üres; ne állítsd vissza `/MD-blog`-ra.
- Bejegyzés URL-je: `https://blog.mdmegvalositorendszer.hu/blog/<fájlnév kiterjesztés nélkül>/`
- Ezen a blogon csak a blogbejegyzések vannak. Az önálló oldalak (Rólam, Kapcsolat, ALAP, AJÁNLOTT, Online Közösségeim, Miért jött létre…, Adatkezelési tájékoztató) a központi WordPress-oldalon élnek; a régi címeik a `build_site.py` `MOVED_PAGES` listája alapján oda irányítanak. Új önálló oldalt ne ide tegyél, hanem a WordPressbe, és ha kell, vedd fel a `MOVED_PAGES`-be.
- A gyökér (`/`) a blog-archívum első oldala. A `feed.xml` RSS-hírcsatorna (legfrissebb 20 bejegyzés) táplálja a központi WordPress-főoldal „Legfrissebb írások” blokkját, ezért a formátumát ne törd el.
>>>>>>> 0869c03 (Önálló oldalak átköltöztetése a központi oldalra, régi címek átirányítása)

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
| `CONTENT/blog.md` | A blog-archívum bevezetője (az egyetlen nem-bejegyzés oldal) |
| `CONTENT/images/<év>/` | Képek AVIF formátumban, három méretben |
| `CONTENT/images/_manifest.json` | Képméretek és `srcset` minden képváltozathoz |
| `CONTENT/assets/` | CSS, favicon |
| `.github/build_site.py` | Az oldalépítő szkript (kimenet: `dist/`, nincs verziókezelve) |
| `.github/workflows/pages.yml` | Push a `main` ágra → build és közzététel |
>>>>>>> 0869c03 (Önálló oldalak átköltöztetése a központi oldalra, régi címek átirányítása)

Do not edit `CONTENT/` unless the user explicitly requests content changes. Preserve existing public post slugs and URLs. Never include `dist/` or generated Python cache files in commits.
