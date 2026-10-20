---
name: site-validation
description: Az MD-blog statikus webhelyének és bejegyzésképeinek ellenőrzése a helyi build előtt. Akkor használd, ha buildet, tartalomellenőrzést vagy GitHub Pages kiadást kell validálni.
---

# Webhely-ellenőrzés

Futtasd a parancsokat a repó gyökeréből:

```powershell
python -m pip install -r .github/DEV/scripts/requirements.txt
python .github/DEV/scripts/build_site.py
python .github/DEV/scripts/ellenorzes.py
```

Sikeres build esetén nézd meg, hogy a várt útvonal létrejött-e a `dist/` alatt, és hogy a build nem jelez hibát. Az „unavailable local image sources” figyelmeztetést jelentsd, ne kezeld sikeres kép-helyreállításként.

Ne commitold a generált `dist/` mappát.

