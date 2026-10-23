# Kiadásra váró változások

## Dokumentáció és fejlesztői munkafolyamat

- A közös tartalomfeltöltési készség új oldalra, blogbejegyzésre, szövegmódosításra, valamint képek hozzáadására és cseréjére is kiterjed.
- A blog buildje és tartalomsegédletei a megosztott fejlesztői szkriptek közé kerülnek, a GitHub Actions az új helyről futtatja őket.
- Az agent útmutatók a magyar nyelvű webhelyhez és a tényleges repószerkezethez igazodnak.
- A README rövid rendszerismertetőre és magyar változásnaplóra hivatkozik.

## Mérés

- A matedomokos.hu minden oldalán működik a Google Analytics (G-JL5KR1VJCM) látogatottságmérés.

## Javítás

- Helyreállt a matedomokos.hu megjelenése: a szerkezeti átrendezéskor a `site.css` a generátor mellé került, de a build csak a `CONTENT/assets` mappát másolta, így az oldalak arculat nélkül jelentek meg. A build most mindkét helyről másol, és leáll, ha az arculati fájl hiányzik.
- Új élesítés előtti ellenőrzés (`check-dist.py`): ha bármelyik oldalról hiányzik a stíluslap vagy nem létező fájlra hivatkozik, a GitHub Actions nem telepíti az új változatot, a régi működő oldal marad kint.
- A stíluslap és az ikon címe tartalom-ujjlenyomatot kap (`site.css?v=…`): minden változás után a böngészők maguktól az új megjelenést töltik be, kézi frissítés (Ctrl+F5) nélkül.
- A build kibírja a Windowsban rosszul (UTF-16, CRLF) mentett fájlokat; figyelmeztet, de az oldal nem dől le. Új `.gitattributes` és `.editorconfig` rögzíti az UTF-8 / LF formát.
- Három írás (Akinek senki sem fogja a kezét, Ezt mondtad, Első 30 nap checklist) ékezetei a hibás mentésben elvesztek; visszaállítva, a szándékolt képhivatkozás-törlések megmaradtak.
- A Rólam portréjának címe javítva (`/images/rolam/mate-domokos-portre.jpg`); a rendszeroldalra mutató linkek és átirányítások ismét az mdmegvalositorendszer.hu-ra mutatnak (önmagukra irányítottak, végtelen körben).
- A `main` ágra tilos a felülíró feltöltés (force push).
