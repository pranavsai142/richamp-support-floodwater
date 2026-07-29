# handoffs/ — The Durable Memory Layer

Dated handoff documents are the **single source of truth** for project state that survives `~/.grok` flushes and travels with the repository.

## Naming

- `YYYY-MM-DD-<topic>-handoff.md`
- `YYYY-MM-DD-session-close.md`

## How It Works

- `/done` creates a new handoff at the end of meaningful work (or mid-plan checkpoints).
- A handoff contains: what was accomplished, key decisions, hard lessons, current focus, open questions, and what the next session should start on.
- `/init` makes you read the most recent 1–3 handoffs + the two driver files.

## Important

The agent's own `plan.md` files (created during plan mode) stay in `~/.grok/sessions/...`. We do **not** copy them here. A handoff may optionally note the path if the full trace is useful later.

This directory + the three skills (`seed`, `init`, `done`) is the complete portable meta-system. Copy it to any project.