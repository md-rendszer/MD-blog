# Kiadásra váró változások

## Tartalom

- Mind a 255 bejegyzés célzott olvasót kapott: a cím alatt „Kinek szól?” doboz mondja meg, kinek szól az írás, a cikk végén három ugyanilyen helyzetű olvasónak szóló írás ajánlója áll.
- Új Témák oldal és 14 témaoldal (pl. Ego, elme, belső hang; Kapcsolatok és konfliktusok; Magyarság és történelem), a főmenüben is.
- Keresőknek: minden bejegyzés böngésző- és Google-címe a fő keresett kifejezéssel bővül, a bejegyzések strukturált adatot (BlogPosting) kapnak, és elkészül a sitemap.xml és a robots.txt.
- Az Írások között csak a képpel ellátott bejegyzések maradnak nyilvánosak; a kép nélküli belső munkajegyzetek (103 db) az archívumba kerültek, a Biblia – MD kivonat 2. és 3. része nyilvános maradt, régi címük az Írások kezdőlapjára visz.

## Sebesség

- Gyorsabban jelenik meg az Írások oldal és minden bejegyzés: a betűtípusok a saját oldalról, előre betöltve érkeznek (nem a Google-tól), az első sor képei pedig azonnal, kiemelt elsőbbséggel töltődnek be.

## Képek

- Minden bejegyzés képe – a borítókép és a szövegközi illusztrációk is – kattintásra teljes képernyőn nyílik meg, a legnagyobb elérhető felbontásban; a képre újra koppintva tovább nagyítható, így az apró feliratok is olvashatók. Bezárás: ×, Esc vagy a kép mellé kattintás.

## Megosztás

- Minden bejegyzés végén követésre és megosztásra hívó, a REND-hez igazodás szellemében írt szöveg áll, a Facebook-oldal és a YouTube-csatorna követőgombjaival.
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

## Nyelvi változatok

- Egy írás fordításai a Kárpát-medence népeinek nyelvén (román, szlovák, szerb, horvát, szlovén, ukrán, ruszin, német, romani), valamint angolul a nagyvilágnak saját címen jelennek meg; az eredeti és a fordítások tetején nyelvválasztó áll, a keresők pedig hreflang-jelöléssel tudják, melyik nyelv melyik változat. A fordítások nem kerülnek az Írások listába, a témákba és a hírcsatornába, de benne vannak az oldaltérképben. Első ilyen írás: A legnehezebb választás – innen indulhat a béke.
