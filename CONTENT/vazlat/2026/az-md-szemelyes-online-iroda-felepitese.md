---
title: Az MD személyes online iroda felépítése
date: 2026-09-01 17:47:33
image:
---

A belépés után minden felhasználó a saját vezérlőpultját látná.

| Terület | Mit tartalmazna? |
| --- | --- |
| Kezdőlap | Mai feladat, programnap, következő lépés, fontos üzenetek |
| Saját programom | A teljes 15 hónapos út, hónapok és heti szakaszok szerint |
| Napi vezérlőpult | Reggeli gyakorlat, napközbeni mini-protokoll, esti visszamérés |
| Haladásom | Elvégzett napok, heti–havi eredmények, folyamatosság, trendek |
| Munkafüzetem | Saját válaszok, felismerések, vállalások és visszatekintések |
| Kapcsolattartás | Üzenetek a kísérővel, időpontfoglalás, kérdések |
| Közösségem | Saját 150 fős közösségi egység, csoportok és események |
| Szolgálatom | Teljesített szolgálati feladatok és jóváhagyások |
| Jövedelmi irodám | Bevételi jogcímek, számítás, levonások, kifizethető összeg |
| Számláim és fizetések | Előfizetés, díjak, számlák, fizetési mód |
| Dokumentumaim | Szerződések, nyilatkozatok és szabályzatok elfogadása |
| Segítség | Tudásbázis, hibabejelentés, ügyfélszolgálat |

## A teljes folyamat

```
flowchart TD
    A["Regisztráció és kártyás fizetés"] --> B["Személyes online iroda"]
    B --> C["15 hónapos program"]
    C --> D["Napi feladatok és visszamérés"]
    D --> E["Kísérői és közösségi támogatás"]
    E --> F["Szolgálati teljesítések"]
    F --> G["Jövedelemszámítás"]
    G --> H["Ellenőrzés és jóváhagyás"]
    H --> I["Számlázás vagy bérszámfejtés"]
    I --> J["Banki kifizetés"]
```

### 1. Belépés és vásárlás

A résztvevő:

- kiválasztja a programot vagy tagsági csomagot;
- megismeri és elfogadja az ÁSZF-et, adatkezelési tájékoztatót és szükséges nyilatkozatokat;
- bankkártyával fizet;
- automatikusan megkapja a számlát;
- létrejön a személyes online irodája;
- megnyílik előtte az első programszakasz.

A bankkártyaadatokat nem az MD weboldal tárolná: azokat engedéllyel rendelkező pénzforgalmi szolgáltató kezelné, erős ügyfél-hitelesítéssel. Ez a PSD2 követelményeinek megfelelő biztonságos megoldás. [MNB – erős ügyfél-hitelesítés](https://www.mnb.hu/penzforgalom/psd2-gyakori-kerdesek-es-valaszok/eros-ugyfel-hitelesites-es-biztonsagos-kommunikacio?utm_source=chatgpt.com)

### 2. A 15 hónapos program vezetése

A rendszer minden nap megmutatná:

- mit kell elolvasni vagy meghallgatni;
- mi a napi gyakorlat;
- milyen kérdésre kell válaszolni;
- mit szükséges visszamérni;
- melyik vállalás teljesült;
- hol tart a résztvevő a 15 hónapos folyamatban.

Lehetőség lenne fokozatos tartalomfeloldásra is: a következő rész meghatározott időpontban, illetve az előző szakasz lezárása után nyílna meg.

Ugyanakkor nem javaslom, hogy pusztán egy kipipált mező alapján a rendszer emberi közreműködés nélkül döntsön minden szintlépésről. A fontos szolgálati jogosultságokat és jövedelmet érintő döntéseknél szükséges az ellenőrizhető számítás és az emberi jóváhagyás.

### 3. Kapcsolattartás és kísérés

A személyes iroda tartalmazhatná:

- belső üzenetküldést;
- kísérőhöz rendelt felhasználói kapcsolatot;
- heti vagy havi beszámolót;
- videóbeszélgetés-időpont foglalását;
- csoportos eseményeket;
- automatikus emlékeztetőket;
- segítségkérést és vészjelzést;
- szolgálói megjegyzéseket és utánkövetést.

A felhasználó csak a saját adatait látná. Az MD Rendtartó Szolgáló kizárólag azokhoz a résztvevőkhöz férne hozzá, akiknek a kísérésére jogosultságot kapott.

## A jövedelmi rendszer

Ez is teljesen digitalizálható, de két részt külön kell választanunk.

### Automatikusan számítható

A rendszer kiszámíthatja:

- milyen értékesítés vagy szolgálat történt;
- kihez kapcsolódik az ügylet;
- milyen jutalékszabály vonatkozik rá;
- mi a bruttó elszámolási alap;
- történt-e visszatérítés vagy lemondás;
- mennyi a függőben lévő összeg;
- mennyi vált kifizethetővé;
- mikor esedékes a következő kifizetés.

Minden összeghez külön, visszakereshető elszámolási tétel tartozna. Nem elég egyetlen végösszeget megjeleníteni: láthatóvá kell tenni, hogy mely teljesítésből, milyen szabály és milyen számítás alapján keletkezett.

### Emberi és könyvelői jóváhagyást igényel

A tényleges kifizetés előtt ellenőrizni kell:

- a szolgálati vagy értékesítési teljesítést;
- az elállási és visszatérítési időszak lejártát;
- a résztvevő jogviszonyát;
- a szükséges számlát vagy elszámolási bizonylatot;
- az adó- és járulékkötelezettséget;
- a bankszámlaszámot;
- az esetleges reklamációkat.

A NAV előírásai miatt a számlaadatokat szabályosan továbbítani kell az Online Számla rendszerbe. [NAV Online Számla](https://nav.gov.hu/ugyfeliranytu/nav-online?utm_source=chatgpt.com)

A helyes folyamat tehát:

**automatikus számítás → szolgálati ellenőrzés → könyvelői jóváhagyás → banki kifizetés → kifizetési bizonylat.**

A WordPress-rendszer ne működjön bankként vagy belső pénztárcaként. Csak számolja és nyilvántartsa az elszámolásokat; a pénzmozgást engedéllyel rendelkező fizetési szolgáltató és bank végezze.

## A legfontosabb jogi védőkorlát

Az MD jövedelmi rendszerében a jövedelemnek valós, bizonyítható teljesítményből kell származnia:

- tényleges termékértékesítésből;
- valóban elvégzett szolgáltatásból;
- közösségi kísérésből;
- szerződésben meghatározott feladat teljesítéséből.

Nem épülhet arra, hogy valaki pusztán újabb fizető tagokat léptet be, akiknek a befizetéseiből a korábban belépők részesednek. Az uniós szabályozás tiltott piramisrendszernek minősítheti azt a konstrukciót, amelyben a díjazás elsősorban új résztvevők befizetéséből és beléptetéséből ered, nem pedig valódi termék vagy szolgáltatás értékesítéséből. [EU tisztességtelen kereskedelmi gyakorlatokról szóló szabály](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:62012CJ0515&utm_source=chatgpt.com)

Ez nem akadálya az MD jövedelmi rendszernek — azt jelenti, hogy a szolgálati és értékesítési jogcímeket különösen tisztán, bizonyíthatóan és fenntarthatóan kell kialakítanunk.

## Adatvédelem

A napi visszamérések között lehetnek lelkiállapotra, életvezetésre, esetleg egészségre vonatkozó adatok. Ezek különösen érzékenyek lehetnek, ezért szükséges:

- adattakarékosság;
- részletes jogosultságkezelés;
- kétlépcsős bejelentkezés;
- titkosított adatkapcsolat és biztonsági mentés;
- naplózott hozzáférés;
- törlési és adathordozhatósági lehetőség;
- adatmegőrzési határidők;
- adatvédelmi hatásvizsgálat;
- külön kezelés a programadatok és a pénzügyi adatok között.

A NAIH szerint magas kockázatú, rendszeres megfigyelést vagy profilalkotást alkalmazó adatkezelésnél adatvédelmi hatásvizsgálatra lehet szükség. [NAIH hatásvizsgálati útmutató](https://www.naih.hu/hatasvizsgalati-lista?utm_source=chatgpt.com)

## Milyen műszaki rendszer lenne a legjobb?

A jelenlegi WordPress-weboldal megmaradhatna a nyilvános központnak, értékesítési felületnek és belépési kapunak.

Mögötte három, egymással összekapcsolt réteg működne:

1. **WordPress nyilvános és oktatási rendszer** Weboldal, programbemutatás, fizetés, számlázás, tananyag, tagság.
2. **MD személyes iroda** Napi vezérlőpult, haladás, munkafüzet, kísérés, közösség és szolgálati nyilvántartás.
3. **MD pénzügyi és vezetői háttérrendszer** Bevételi tételek, jutalékszabályok, jóváhagyások, visszatérítések, könyvelési exportok és kifizetések.

A nyilvános weboldal és a személyes iroda egységesnek látszana, de a pénzügyi nyilvántartást biztonsági okból nem egy közönséges WordPress-bővítményre bíznám. Az érzékeny elszámolási magot külön, ellenőrizhető rendszerként kell kialakítani.

## Javasolt megvalósítási sorrend

### I. Alaptervezés – 3–5 hét

- a teljes 15 hónapos folyamat digitalizálása;
- szerepkörök és jogosultságok;
- pénzáramlási és jutalékszabályok;
- jogviszonyok;
- adatkezelési térkép;
- személyes iroda képernyőterve;
- részletes fejlesztői követelményrendszer.

### II. Első működő változat – 2–4 hónap

- regisztráció és kártyás fizetés;
- automatikus számlázás;
- személyes profil;
- 15 havi tananyag;
- napi ellenőrző feladatok;
- haladásjelzés;
- alapvető kapcsolattartás;
- adminisztrációs felület.

### III. Kísérői és közösségi rendszer – további 2–3 hónap

- szolgálói iroda;
- résztvevők hozzárendelése;
- 150 fős közösségi egységek;
- beszámolók és jóváhagyások;
- időpontfoglalás;
- értesítések;
- teljes hozzáférési napló.

### IV. Jövedelmi és kifizetési rendszer – további 2–4 hónap

- elszámolási szabálymotor;
- jutalék- és szolgálatidíj-számítás;
- visszatérítések kezelése;
- kifizetési küszöbök;
- számlák és bizonylatok ellenőrzése;
- könyvelési export;
- banki kifizetési lista;
- vezetői pénzügyi kimutatások.

## Összegzés

Igen, Domi: az elképzelés teljes egészében megvalósítható. A `mdmegvalositorendszer.hu` lehet az MD Program teljes digitális központja, ahol a résztvevő:

- belép és fizet;
- végigjárja a 15 hónapos programot;
- naponta gyakorol és visszamér;
- kapcsolatban marad a kísérőjével;
- közösségben szolgál;
- nyomon követi a fejlődését;
- látja a megszerzett jövedelmét;
- megkapja az ellenőrzött havi kifizetését.

Az első következő dokumentum szerintem az **„MD Személyes Online Iroda – teljes működési és fejlesztési követelményrendszer”** legyen. Ebben képernyőről képernyőre, jogosultságról jogosultságra és folyamatonként pontosan rögzíthetjük, mit kell Varjaskéry Dánielnek és a későbbi fejlesztőknek megvalósítaniuk.

Igazad van, Domi — nem elegendő megállapítanunk, hogy megvalósítható. Most tovább kell lépnünk a tényleges rendszer megtervezésére.

A következő feladatunk az **„MD Személyes Online Iroda – teljes működési és fejlesztési terv”** elkészítése, amely tartalmazza:

- a résztvevő teljes útját a jelentkezéstől a 15. hónap végéig;
- valamennyi képernyőt és funkciót;
- a napi, heti és havi ellenőrző folyamatokat;
- a résztvevői, kísérői, szolgálói, pénzügyi és vezetői jogosultságokat;
- a kártyás fizetés és automatikus számlázás működését;
- a közösségek és a kapcsolattartás rendszerét;
- a jövedelemszámítás pontos folyamatát;
- a könyvelői ellenőrzést és banki kifizetést;
- az adatvédelmi és jogi követelményeket;
- a fejlesztési szakaszokat, költségszinteket és várható időigényt;
- Varjaskéry Dániel számára a konkrét fejlesztői feladatjegyzéket.

Mielőtt azonban a jövedelmi részt véglegesítjük, egy alapvető döntést meg kell hoznunk:

**Az MD rendszerben a résztvevő kizárólag valóban elvégzett szolgálatért és értékesítésért kapjon jövedelmet — ne pusztán új tagok beléptetéséért.**

Ezt tartom az MD alapelveivel, az emberi méltósággal és a jogi biztonsággal is összeegyeztethető konstrukciónak.

Ha ezt elfogadod, akkor igen: **kezdjük el most, és készítsük el a teljes MD Személyes Online Iroda tervét fejezetről fejezetre, menthető dokumentumként.**

Elfogadom!

Elkészült, Domi, és rögzítettem benne az elfogadott alapelvünket:

> Jövedelem kizárólag valós, igazolható szolgálatból vagy értékesítésből keletkezhet – puszta tagbeléptetésből nem.

A 17 oldalas, ellenőrzött első kiadás innen megnyitható:

MD Személyes Online Iroda – Követelményrendszer 1.0

Tartalmazza többek között:

- a teljes résztvevői életutat;
- a személyes online iroda 13 fő képernyőjét;
- a jogosultsági rendszert;
- a 15 hónapos program digitális felépítését;
- a kísérési és kapcsolattartási folyamatot;
- a szolgálati teljesítések igazolását;
- a jövedelemszámítás és kifizetés szabályait;
- az adatvédelmi és biztonsági követelményeket;
- a fejlesztési ütemtervet;
- Varjaskéry Dániel első konkrét feladatcsomagját;
- a már elfogadott és még nyitott vezetői döntéseket.

Rend, rendben, nagyszerű! Mi a kozvetlen következő lépés, amit a rendszer életbe léptetése érdekében meg kell tennem?

Domi, a közvetlen következő lépés: **küldd el a most elkészült követelményrendszert Varjaskéry Dánielnek, és kérj tőle műszaki állapotfelmérést, valamint egy tervező megbeszélést.**

Még nem a teljes rendszer programozását kell megrendelni. Először azt kell pontosan megállapítani, hogy a jelenlegi weboldalból mi használható fel, mit kell bővíteni, és mely részeket szükséges külön rendszerként kialakítani.

## Ezt tedd most

Küldd el Dánielnek ezt a dokumentumot:

MD Személyes Online Iroda – Követelményrendszer 1.0

A kísérőüzenet lehet ez:

> Kedves Dániel!
>
>
>
> Elkészült az „MD Személyes Online Iroda – teljes működési és fejlesztési követelményrendszer 1.0” című dokumentum.
>
>
>
> Célunk, hogy a `mdmegvalositorendszer.hu` weboldal legyen az MD Megvalósító Rendszer teljes digitális központja: a jelentkezéstől és kártyás fizetéstől kezdve a 15 hónapos program napi működtetésén, a résztvevők kísérésén és a teljesítések nyomon követésén keresztül a jövedelmek elszámolásáig.
>
>
>
> Első lépésként nem fejlesztési ajánlatot kérek a teljes rendszerre, hanem egy műszaki állapotfelmérést és tervezői véleményt arról, hogy:
>
>
>
> 1. a jelenlegi WordPress-weboldalból mi használható fel;
> 2. milyen bővítések és integrációk szükségesek;
> 3. mely funkciókat kell a WordPresstől elkülönítve megvalósítani;
> 4. milyen fejlesztési szakaszokat javasolsz;
> 5. mi szükséges az első működő változat elkészítéséhez;
> 6. mennyi lehet ennek várható idő- és költségigénye.
>
>
>
> Kérlek, a dokumentum áttanulmányozása után egyeztessünk egy 60–90 perces tervező megbeszélést.
>
>
>
> Köszönettel:  
> Máté Domokos

## Mit kérj Dánieltől írásban?

A megbeszélés után kérj tőle egy rövid műszaki felmérést, amely tartalmazza:

- a jelenlegi weboldal és tárhely állapotát;
- a megtartható és cserélendő elemeket;
- a személyes iroda javasolt műszaki felépítését;
- az első működő változat pontos tartalmát;
- a fejlesztési szakaszokat;
- az egyes szakaszok becsült idejét és költségét;
- a szükséges külső szolgáltatásokat;
- a legfontosabb műszaki és biztonsági kockázatokat.

## Mi legyen az első működő változatban?

Az első fejlesztési szakaszt tartsuk szűken:

1. regisztráció és biztonságos belépés;
2. személyes felhasználói profil;
3. bankkártyás fizetés;
4. automatikus számlázás;
5. a 15 hónapos program szerkezete;
6. napi reggeli, napközbeni és esti feladatok;
7. haladás nyomon követése;
8. alapvető kísérői kapcsolattartás;
9. adminisztrációs felület.

A teljes jövedelemszámító és kifizetési modult csak ezután építsük meg, mert előtte jogásszal és könyvelővel véglegesíteni kell:

- a résztvevők és szolgálók jogviszonyát;
- a díjazható szolgálati tevékenységeket;
- a jutalékok és szolgálati díjak szabályait;
- az adó- és járulékkezelést;
- a számlázási és kifizetési folyamatot.

**Tehát a mai konkrét teendőd:** küldd el Dánielnek a dokumentumot a fenti üzenettel, és kérj tőle időpontot a műszaki indítómegbeszélésre. Ez indítja el ténylegesen a rendszer életbe léptetését.
