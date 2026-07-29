---
name: seed
description: >
  Bootstraps the pragmatic meta-system (notes/GROK/ + seed/init/done skills + handoffs/ as the durable layer) into any repository. Ships pre-baked canonical READMEs from readmes/. Use on fresh projects or when porting the meta-system.
---

# /seed — Bootstrap the Pragmatic Meta System

Installs the complete portable memory system (`seed`/`init`/`done` + `handoffs/`) so every future session starts with real, durable context.

## What Gets Created

```
notes/GROK/
  SOUL_DRIVER.md
  DEV_NOTES.md
  README.md
  handoffs/
    README.md
    ARCHIVE/
      README.md
notes/WIKI/
  INDEX.md                (starter for project wikis / living docs)
.grok/skills/seed/, init/, done/
```

## Steps

1. **Ask for source material** — existing vision docs, notes.md, philosophy, current state, or a short conversation. This is the most important step.

2. **Create directories**:
   - `notes/GROK/handoffs/ARCHIVE/`

3. **Copy the canonical READMEs** (do not generate them):
   - Copy `.grok/skills/seed/readmes/GROK_README.md` → `notes/GROK/README.md`
   - Copy `.grok/skills/seed/readmes/HANDOFFS_README.md` → `notes/GROK/handoffs/README.md`
   - Copy `.grok/skills/seed/readmes/ARCHIVE_README.md` → `notes/GROK/handoffs/ARCHIVE/README.md`

4. **Create wiki starter**:
   - Copy `.grok/skills/seed/readmes/WIKI_INDEX.md` → `notes/WIKI/INDEX.md` (light starter for project wikis).

5. **Seed the drivers**:
   - Copy `SOUL_DRIVER_TEMPLATE.md` and `DEV_NOTES_TEMPLATE.md` from `readmes/` as starting points.
   - Customize them heavily using the source material the user provided.
   - (Optional) Create a first handoff recording the initial state.

5. **Install the three skills** into `.grok/skills/` if they are missing (copy the whole `seed/`, `init/`, `done/` directories).

6. **Final message** listing exactly what was created and instructing the user to run `/init` next.

## Principles

- Pre-baked READMEs in `readmes/` guarantee consistency across all projects that adopt this meta-system.
- Only `SOUL_DRIVER.md` and `DEV_NOTES.md` need to be synthesized per project.
- Handoffs are the durable layer. The agent's `plan.md` never gets copied into the repo.
- `notes/WIKI/` is the standard place for project-specific living documentation and mental models.
- This entire `seed/` skill (including its `readmes/`) is what you copy when porting the system.