---
name: done
description: >
  Closing ritual. Captures the session as a rich dated handoff in notes/GROK/handoffs/ (the durable portable memory layer), lightly updates the lightweight drivers, and leaves a clean handoff for the next /init. Use at end of meaningful work or mid-plan. Part of the portable seed/init/done meta-system.
---

# /done — Session Close & Handoff Ritual

Turn raw session work into durable project memory so future sessions (after flushes, across machines, or in other repos that adopt this system) can continue without re-deriving context.

**Handoffs under `notes/GROK/handoffs/` are the single durable memory layer.** The agent's `plan.md` (from plan mode) stays in `~/.grok/sessions/...` — we never copy it into the repo.

## Ritual Steps

1. **Capture** a rich narrative of what happened, decisions, hard lessons, current state of active work, open questions, and what the next session must start with.

2. **Review** (in order):
   - `notes/GROK/SOUL_DRIVER.md`
   - `notes/GROK/DEV_NOTES.md` (keep this one short)
   - The most recent 1–3 files in `notes/GROK/handoffs/`

3. **Design the handoff** (and any minimal driver updates). Handoffs live in `notes/GROK/handoffs/YYYY-MM-DD-<slug>.md` (or `-session-close.md`).

4. **Propose first** — always show the user the exact proposed handoff content + any DEV_NOTES diffs **before** writing anything. Only create/edit files after explicit approval.

5. **Write** the approved handoff (and the approved driver edits).

**Optional:** In step 3, if the session produced important new mental models or invariants, consider adding a short dated note under `notes/WIKI/` (if the project uses it). Include in the same proposal shown to the user. Zero cost if skipped.

## Principles

- **Short by omission for drivers.** Rich history, decisions, and "what we just did" go into the dated handoff. DEV_NOTES stays a lightweight "current reality + forward direction" document.
- **No PLANNING/ promotion.** There is only one durable layer: the dated handoffs. Do not copy or reference the session's `plan.md` except optionally as a footnote when the full design trace might be useful later.
- The three skills + `handoffs/` are the complete portable meta-system. Drop them into any project.

## Final Message

> Session closed.
> - Handoff: `notes/GROK/handoffs/2026-05-23-xxx.md`
> - Drivers lightly updated (see proposal)
> - Run `/init` next time.

Follow the loop. Handoffs keep the memory alive.