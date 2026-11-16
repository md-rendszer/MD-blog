---
name: uj-blogbejegyzes
description: Új blogbejegyzés (és opcionális borítókép) hozzáadása az MD-blog repóhoz, ellenőrzés és közzététel. Akkor használd, ha Domi új bejegyzést, borítóképet vagy bejegyzésjavítást kér a md-rendszer/MD-blog repóban.
---

# Új blogbejegyzés az MD-blogba

Előbb olvasd el a repó gyökerében az `AGENTS.md`-t (formátum, nyelv, MD terminológia).

## 1. Fájl létrehozása

1. Slug a címből: kisbetű, ékezetek nélkül (á→a, é→e, í→i, ó/ö/ő→o, ú/ü/ű→u), minden más karakter helyett kötőjel, egymás utáni kötőjelek összevonva. Ha bármelyik évmappában létezik már ilyen nevű fájl, tegyél a végére `-2`-t.
2. Útvonal: `CONTENT/blog/<év>/<slug>.md`, ahol az év a `date` éve.
3. Frontmatter:

   ```
   ---
   title: <cím, idézőjelek nélkül>
   date: <ÉÉÉÉ-HH-NN óó:pp:mm, budapesti idő>
   image: -
   image_alt: <egy rövid mondat a képről, legfeljebb 200 karakter>
   lead: "<2–3 mondatos, figyelemfelkeltő bevezető: kinek szól, mit kap belőle>"
   kerdes: "<egyszerű, nyitott, személyes kérdés az olvasóhoz>"
   kinek: "<élethelyzet, ahogy az olvasó maga mondaná – a cikkben így jelenik meg: „Neked, ha …”>"
   tema: <témakör slugja a build_site.py TOPICS listájából>
   kereses: "<2–3 kifejezés, amit az olvasó a Google-be írna; pontosvesszővel elválasztva>"
   ---
   ```

4. A `lead` jelenik meg az Írások-kártyán, a Google-találatban és a Facebook-előnézetben; a `kerdes` a cikk végén, kiemelt dobozban. Mindkettő tegező, nem szenzációhajhász. A `kinek` a cím alatti „Kinek szól?” dobozban áll; a `tema` dönti el, melyik témaoldalon (/tema/<slug>/) és melyik „Neked ajánlom még” listában jelenik meg az írás; a `kereses` első kifejezése a böngészőfül és a Google-találat címébe kerül. Konkrét élethelyzetet írj (mit él át, mire keres rá az olvasó), ne általános témát.
5. Törzs: magyar, tegező, MD kanonikus szóhasználat, szövegközi forráshivatkozás nélkül. Ha Domi kész szöveget ad, ne írd át, csak formázd.

## 2. Borítókép (ha kérik)

1. Készíts egy PNG-t vagy JPG-t, legalább 1024 px szélesen, kb. 16:9 arányban, az MD arculatában (bordó `#6E1423`, arany `#9C7A3C`, törtfehér háttér, dupla arany keret, rombusz díszek). Ne használj jogvédett képet, ismert karaktert vagy valós személy fotóját.
2. Futtasd:

   ```bash
   python .claude/skills/uj-blogbejegyzes/scripts/kep_hozzaadasa.py <forraskep.png> <év> <slug>
   ```

   Ez legyártja a három AVIF-méretet a `CONTENT/images/<év>/` mappába, frissíti a `_manifest.json`-t, és kiírja a frontmatterbe való `image:` sort.
3. Írd be az `image:` sort a bejegyzés fejlécébe.

## 3. Ellenőrzés

```bash
python -m pip install -q -r .github/requirements.txt
python .github/build_site.py
python .claude/skills/uj-blogbejegyzes/scripts/ellenorzes.py
ls dist/blog/<slug>/index.html
```

Ha bármelyik hibát jelez, javítsd, mielőtt továbblépsz.

## 4. Közzététel

```bash
git pull --rebase origin main
git add CONTENT
git commit -m "Új bejegyzés: <cím>"
git push origin HEAD:main
```

Ha a pull ütközések tömegét hozza (a `main` közben `_init_site` újrafeltöltést kapott), ne oldd fel kézzel: klónozd újra a repót, másold át a saját fájljaidat, és onnan commitolj.

A push után az oldal 1–2 perc alatt frissül. A link: `https://matedomokos.hu/blog/<slug>/`. A `gh run list -R md-rendszer/MD-blog -L 1` mutatja a build állapotát.

## 5. Visszajelzés Dominak

Röviden, magyarul, tegezve: a bejegyzés címe, a nyilvános link, és ha volt, minden eltérés vagy probléma. Ne sorold fel a lépéseket.
