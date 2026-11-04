# Kiadásra váró változások

## Megosztás

- Minden bejegyzés címe alatt egy kattintással megosztható a Facebookon, a bejegyzés végén pedig Facebookra, WhatsAppra, Viberre, Telegramra, X-re, LinkedInre és e-mailben is; a link egy gombnyomással kimásolható, telefonon a „Továbbiak” gomb a készülék saját megosztását nyitja meg (Messenger, Instagram stb.).
- A bejegyzések megosztáskor címmel, rövid kivonattal és a borítóképükkel jelennek meg a Facebookon és más oldalakon; ahol nincs kép, egységes alapkép látszik.

## Dokumentáció és fejlesztői munkafolyamat

- A közös tartalomfeltöltési készség új oldalra, blogbejegyzésre, szövegmódosításra, valamint képek hozzáadására és cseréjére is kiterjed.
- A blog buildje és tartalomsegédletei a megosztott fejlesztői szkriptek közé kerülnek, a GitHub Actions az új helyről futtatja őket.
- Az agent útmutatók a magyar nyelvű webhelyhez és a tényleges repószerkezethez igazodnak.
- A README rövid rendszerismertetőre és magyar változásnaplóra hivatkozik.

## Mérés

- A matedomokos.hu minden oldalán működik a Google Analytics (G-JL5KR1VJCM) látogatottságmérés.

## Javítás

- A felső sáv „Az általam alkotott rendszer: MD Megvalósító Rendszer” linkje és a lábléc rendszer-linkje ismét az mdmegvalositorendszer.hu-ra mutat (eddig a matedomokos.hu-ra vitt vissza).

- A stíluslap-másolás a buildből ismét kimaradt (2026. október 27. óta minden élesítés elakadt az ellenőrzésen); visszakerült, az új bejegyzések újra megjelennek.
- Helyreállt a matedomokos.hu megjelenése: a szerkezeti átrendezéskor a `site.css` a generátor mellé került, de a build csak a `CONTENT/assets` mappát másolta, így az oldalak arculat nélkül jelentek meg. A build most mindkét helyről másol, és leáll, ha az arculati fájl hiányzik.
- Új élesítés előtti ellenőrzés (`check-dist.py`): ha bármelyik oldalról hiányzik a stíluslap vagy nem létező fájlra hivatkozik, a GitHub Actions nem telepíti az új változatot, a régi működő oldal marad kint.
- A stíluslap és az ikon címe tartalom-ujjlenyomatot kap (`site.css?v=…`): minden változás után a böngészők maguktól az új megjelenést töltik be, kézi frissítés (Ctrl+F5) nélkül.
- A build kibírja a Windowsban rosszul (UTF-16, CRLF) mentett fájlokat; figyelmeztet, de az oldal nem dől le. Új `.gitattributes` és `.editorconfig` rögzíti az UTF-8 / LF formát.
- Három írás (Akinek senki sem fogja a kezét, Ezt mondtad, Első 30 nap checklist) ékezetei a hibás mentésben elvesztek; visszaállítva, a szándékolt képhivatkozás-törlések megmaradtak.
- A Rólam portréjának címe javítva (`/images/rolam/mate-domokos-portre.jpg`); a rendszeroldalra mutató linkek és átirányítások ismét az mdmegvalositorendszer.hu-ra mutatnak (önmagukra irányítottak, végtelen körben).
- A `main` ágra tilos a felülíró feltöltés (force push).
