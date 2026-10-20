# Development and Validation

This is a static Markdown site for a Hungarian-language website. The build and content utilities live in `.github/DEV/scripts/`; the Pages workflow is `.github/workflows/pages.yml`.

Run the site build and content checks from the repository root:

```powershell
python -m pip install -r .github/DEV/scripts/requirements.txt
python .github/DEV/scripts/build_site.py
python .github/DEV/scripts/ellenorzes.py
```

The build writes generated output to `dist/`. Do not commit that directory or Python cache files. Preserve the RSS feed format and the configured empty `SITE_BASE_PATH` for the custom domain.

