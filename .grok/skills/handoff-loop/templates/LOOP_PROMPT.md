# LOOP PROMPT — <program short name>

**Copy everything below the line into a new agent session. Re-run until the living TODO shows all coverage rows and WPs done.**

---

You are implementing **<north star one-liner>** for this repository until the vision is fully delivered.

## Mandatory init (every session)

1. Read in order:
   - Your project's SOUL_DRIVER (durable layer)
   - Your project's DEV_NOTES
   - The program handoff (path filled at setup)
   - The design document (path filled at setup)
   - **The living TODO** (path filled at setup) ← single progress truth
   - Any wiki/spec chapters required by the active WP
2. Do **not** re-open locked decisions listed in the program handoff.

## North star (stop condition)

Deliver **every** vision element tracked as coverage rows in the living TODO, via ordered WPs.  
**Done only when** all coverage rows and all WPs are `done` with verification evidence.

Until then: **continue the loop**—do not stop after one WP unless blocked by real failure or an explicit human gate.

## Loop body (repeat)

### 1. Select work
- Open the living TODO.
- First `pending` WP whose dependencies are `done` → set `in_progress` (only one).
- If all WPs done: verify coverage rows; write final done handoff; **stop**.
- If blocked with no alternative: document and stop for human input.

### 2. Implement smallest verifiable slice
- Only what that WP requires (see design PR/WP plan).
- Prefer buildable/testable tree.
- Follow technical guidelines in the design; do not invent outside contracts.
- Respect phase order (foundations/oracle/harness before rewrite/acceleration/full UI polish as stated in locks).

### 3. Verify
- Run the Verify column for that WP using your project's harnesses/verifiers named in the design/TODO.
- Capture evidence. No `done` without evidence.

### 4. Update durable progress
Edit the living TODO: WP → done + Evidence; flip related coverage rows; append session log; update dashboard + Current focus.  
Lightly update DEV_NOTES if narrative state changed.

### 5. Session close
- Meaningful slice → short dated handoff in the durable handoffs layer.
- If incomplete: name next WP and continue if context allows; else end with “paste this LOOP PROMPT again.”
- If blocked: status `blocked` + reason; stop.

## Priority order

Follow WP order in the living TODO. Do not jump phases.

## Stack locks

<filled at setup: languages, runtimes, oracle, non-negotiables>

## First action right now

If the first open WP is still pending: execute it, update the living TODO, then proceed to the next WP if possible in-session.

**Begin.**
