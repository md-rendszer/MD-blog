# Változásnapló

## [v2.0.0] - 2026-10-20

### Hozzáadva

- A WordPress-alapú webhely blogarchívuma Markdown-forrásokból épülő statikus webhellyé válik, amely GitHub Pages-en érhető el.
- A migráció az önálló oldalakat, a közzétett bejegyzéseket és a helyben tárolt piszkozatokat külön kezeli; a bejegyzések évenkénti mappákban maradnak.
- A képtár helyi AVIF-változatokkal és reszponzív képadatokkal egészül ki.
- A GitHub Actions munkafolyamat automatikusan építi és telepíti a webhelyet a `main` ágra érkező változtatások után.
- A blogarchívum lapozást, bejegyzésenkénti útvonalakat, régi címekhez átirányításokat és RSS-hírcsatornát kap.
- A megjelenés a központi webhely arculatához igazodik, és kis, illetve nagy képernyőkön is használható.
- A közös képfeldolgozó, bejegyzés-ellenőrző és agent munkakészségek elérhetővé válnak a fejlesztők és AI-ügynökök számára.
- Magyar nyelvű rendszerismertető és tartalmi statisztika foglalja össze az archívum szerkezetét és közzétételét.

### Javítva

- A helyben tárolt bejegyzésképek, a manifest és a generált képhivatkozások egyeznek.
- A régi vagy hiányzó helyi képfájlok nem maradnak észrevétlenek: az építés figyelmeztetést ad róluk.
- A helyi build és a GitHub Actions ugyanazokat a fejlesztői szkripteket és függőségeket használja.

