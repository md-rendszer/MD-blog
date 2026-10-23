# Git and Release Workflow

- Make only changes requested by the user. Do not edit `CONTENT/` unless the user explicitly asks for content work.
- Do not stage, commit, push, or rewrite history unless the user explicitly requests the relevant Git operation.
- Preserve public routes and post slugs. If a slug must change at the user's request, keep the old route as an alias.
- Use short Hungarian commit messages for content changes and descriptive messages for system changes.
- Never commit `dist/`, credentials, or generated Python cache files.
- Before pushing, inspect the branch and remote state. Rewrite shared history only when the user explicitly asks for it.
- Never force-push `main`. Force pushes on `main` are blocked by branch protection; on rejection, `git pull --rebase` and push again. A force push on 2026-10-27 silently removed a deployed fix and broke the site's styling.
- Save every text file as UTF-8 with LF line endings (`.editorconfig`, `.gitattributes`). Do not write Markdown with Windows PowerShell `Set-Content`/`Out-File` without `-Encoding utf8`; it produces UTF-16 and destroys Hungarian accents.
