# Repository Instructions

This repository contains a Hungarian-language static archive of Máté Domokos's website and blog. Keep the website's user-facing content in Hungarian; write these agent instructions in English.

Before a task, read the relevant project guidance:

- [Content and language rules](.agents/language-and-content.md)
- [Build, scripts, and validation](.agents/development.md)
- [Documentation and changelog](.agents/documentation.md)
- [Git and release workflow](.agents/git-and-release.md)
- [System overview](./_docs/README.md)

Shared skills are maintained in the root `.skills/` folder; Claude Code skill entries under `.claude/skills/` point back to those canonical instructions.

Do not edit `CONTENT/` unless the user explicitly requests content changes. Preserve existing public post slugs and URLs. Never include `dist/` or generated Python cache files in commits.
