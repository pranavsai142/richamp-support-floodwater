# notes/GROK/ — Durable Project Memory

This directory holds the portable, long-lived memory for the project using the `seed` / `init` / `done` meta-system.

## Core Files

- `SOUL_DRIVER.md` — North star and operating philosophy (changes rarely).
- `DEV_NOTES.md` — Lightweight current state + hard-won lessons (kept short by omission).
- `handoffs/` — The single durable memory layer. Rich, dated handoff documents written by `/done`.

The latest 1–3 handoffs + `DEV_NOTES.md` + `SOUL_DRIVER.md` are the complete source of truth for any new session.

Run `/init` at the start of every session. Run `/done` when finishing meaningful work.

Everything here is designed to survive memory flushes, machine moves, and being copied to other projects.