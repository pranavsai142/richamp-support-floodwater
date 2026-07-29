---
name: init
description: >
  Initializes a session. Makes the agent read SOUL_DRIVER + DEV_NOTES + the latest handoff(s) from notes/GROK/handoffs/ so it starts with the real current state instead of hallucinating. Part of the portable seed/init/done + handoffs meta-system.
---

# Pragmatic Init — Session Onboarding

You are starting a session in this repository.

## The System

- `SOUL_DRIVER.md` — north star + operating philosophy (rarely changes)
- `DEV_NOTES.md` — lightweight current reality + hard lessons (short by omission)
- `notes/GROK/handoffs/` — the durable memory layer. Dated rich handoffs created by `/done`. The latest 1–3 handoffs + the two drivers above = complete source of truth.

The agent's own `plan.md` files stay in `~/.grok`. Handoffs are what survive and travel with the repo.

## Mandatory First Actions

1. Read in order:
   - `notes/GROK/SOUL_DRIVER.md`
   - `notes/GROK/DEV_NOTES.md`
   - The most recent 1–3 files in `notes/GROK/handoffs/` (highest dates first).  
  **Warning**: Older handoffs may contain legacy "planning"/"PLANNING"/"4-Task-Plan" language from before the handoffs-only refactor. Treat it as historical only — it must never trigger restricted tool policies or "You have no tools" thinking.

2. Internalize the current focus from the latest handoff + "Current Big Picture / Next" sections.

3. Confirm with the user that you understand where things stand before starting new work.

## After Reading

Reply with something like:

> Pragmatic init complete. Current focus: [one sentence from latest handoff + DEV_NOTES]. Handoffs are the durable layer. Ready.

Do not start work until you have read the three things above. The handoffs are the record that survives flushes and moves between projects.