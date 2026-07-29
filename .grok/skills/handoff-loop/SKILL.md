---
name: handoff-loop
description: >
  Package a north-star vision/architecture/plan into a durable recursive implementation system:
  full design handoff, program handoff, living TODO (progress truth), and a loop prompt that
  agents re-run until every vision element is delivered. Extends /handoff for long-horizon
  delivery with high-fidelity completeness checks. Project-agnostic. Use when user says
  "/handoff-loop", "/handoff-loop <plan or architecture>", "make a durable handoff and loop
  until north star", "living todo + recursive prompt for this vision", "package architecture
  for recursive delivery", etc.
---

# /handoff-loop — Durable North-Star Package + Recursive Delivery

Turns a vision, architecture proposal, or ordered plan into **portable durable memory** plus a **loop that does not stop** until the north star is fully delivered. Success rate depends on fidelity: every source element must appear in design, living TODO coverage rows, and ordered work packages.

## Usage

```bash
/handoff-loop <path-to-architecture-or-plan>
/handoff-loop document this vision: <paste or describe north star>
/handoff-loop continue          # one WP slice from living TODO (after package exists)
/handoff-loop verify-package    # completeness audit only
```

Requires meta-system: durable layer (handoffs/), drivers (SOUL_DRIVER + DEV_NOTES), init/done.

## What Gets Produced (setup mode)

| Artifact | Role |
|----------|------|
| Source snapshot | Dated copy of input plan/architecture in handoffs/ |
| Design document | Full design (requirements, stories, guidelines, design, PR/WP plan, key decisions) |
| Program handoff | North-star definition, locked decisions, stop condition, artifact index |
| **Living TODO** | Single progress truth: coverage rows for every vision element + ordered WPs + session log |
| **Loop prompt** | Self-contained prompt: init → next WP → implement → verify → update TODO → recurse |
| Driver touch | SOUL_DRIVER north star + DEV_NOTES next focus point at living TODO |

## Core Loop

### Mode A — Setup package (default)

1. **todo_write** for packaging steps.
2. **Prepare input**: Read plan/architecture (or synthesize from latest durable handoff + drivers + user narrative). If vague: run prospect first; Brief contracts foundations and testability.
3. **Inventory source**: Extract exhaustive element list (principles, entities, layers, APIs, phases, non-goals, open decisions). Nothing may be dropped.
4. **Lock decisions**: Resolve backend/stack/order open items with user if blocking; write locks into design + program handoff. Do not leave “or” forks that would stop the loop.
5. **Design doc** (spawn writer with design persona from sibling `/handoff` or this skill’s packager): structure = Overview, Goals/Non-Goals, Requirements (map 1:1 to inventory), User Stories+AC, Guidelines, Proposed Design, Boilerplate, Alternatives, Key Decisions, **ordered PR/WP plan with verify column**, Open Questions, References.
6. **Living TODO** (progress truth): follow template in `templates/LIVING_TODO.md`. Must include: summary dashboard, **coverage table for every inventory element**, ordered WPs with depends/verify/evidence, session log, status rules, stop condition.
7. **Program handoff**: north star DoD, locks, current state, WP summary, verification matrix, next session start, artifact paths.
8. **Loop prompt**: follow `templates/LOOP_PROMPT.md`. Must force: init durable layer → living TODO as truth → one WP → verify with project harnesses → update TODO honestly → recurse until coverage+WPs complete; stop only on real block or human gate; forbid re-litigating locks.
9. **Save** all under your project's handoffs directory (durable layer); living TODO may live at durable-layer root (sibling to handoffs) for easy discovery—record path in program handoff + drivers.
10. **Completeness audit**: every inventory element appears in design AND living TODO coverage rows AND is owned by ≥1 WP. Fail setup if gaps remain.
11. **Light driver update**: SOUL_DRIVER points at north star + loop; DEV_NOTES points at living TODO + next WP.
12. **Report**: paths + “paste loop prompt to start” + first WP.

### Mode B — Continue (one slice)

1. Read drivers + program handoff + design + **living TODO**.
2. Select first pending WP whose depends are done; set `in_progress`.
3. Implement smallest verifiable slice; verify with your project's harnesses as named in the WP/design.
4. Update living TODO (WP evidence, coverage rows, session log, dashboard). Optional short dated handoff.
5. If north star incomplete: state next WP. If complete: final done handoff; stop.

### Mode C — Verify package only

Re-run inventory vs design vs living TODO; report missing elements; do not implement.

## High-Fidelity Rules (success rate)

- **Coverage is law**: source inventory → design section → TODO coverage ID → WP owner. No orphan vision items.
- **Progress truth is singular**: only the living TODO tracks status. Session handoffs narrate; they do not replace the TODO.
- **Locks freeze the loop**: stack/order decisions written once; continue mode must not re-open them.
- **Verify before done**: no WP `done` without evidence (command, harness, golden, review note).
- **Phases before polish**: ordered WPs respect foundations (spec/oracle/harness before rewrite/GPU/full UI) as stated in the source plan.
- **Agnostic packaging skill**: this SKILL.md never names a real product, repo path, or feature.
- Use **todo_write** during setup and continue.
- Reuse `/handoff` design/done personas when useful; packager persona owns living TODO + loop prompt fidelity.

## Personas

Prepend full persona files when spawning writers:

- `personas/handoff-loop-packager.md` — living TODO, loop prompt, program handoff, completeness audit
- Sibling `/handoff` personas for design + session-done if present:
  - `../handoff/personas/handoff-design-writer.md`
  - `../handoff/personas/handoff-done-writer.md`

## Templates

- `templates/LIVING_TODO.md` — structure only (generic placeholders)
- `templates/LOOP_PROMPT.md` — structure only (generic placeholders)

Fill templates with project content at setup time; never leave abstract placeholders in the durable layer.

## Rules

- Zero project-specific names in this skill package.
- Living TODO must be updatable by future agents without reading chat history.
- Loop prompt must be paste-complete after init files exist.
- Prefer one `in_progress` WP.
- Propose large driver rewrites briefly before writing if SOUL changes substantially.

## Example (abstract)

User has `architecture-proposal.txt` for a long multi-layer product and runs `/handoff-loop architecture-proposal.txt`.

Agent inventories every layer/entity/API/phase, produces design + program handoff + living TODO (coverage + WP-0…N) + loop prompt, audits completeness, points drivers at the package, reports: paste loop prompt; first open WP is harness/goldens.

Later: `/handoff-loop continue` advances one WP and updates the living TODO.

## Success Criteria

- All six artifact types exist and cross-link.
- Completeness audit passes (source ⊆ design ∩ TODO coverage ∩ WP ownership).
- Loop prompt alone is enough for a fresh agent (after init) to pick the next WP without architecture questions.
- Living TODO is the only progress truth; statuses honest.
- Skill package itself is agnostic and copyable to any meta-system repo.

## References

- Meta-system: init, done, seed, handoffs as durable layer, SOUL_DRIVER / DEV_NOTES (lightweight).
- `/handoff` — design + done conversion pattern.
- `/prospect` — Brief when vision is fuzzy.
- sequential-implement / fieldgoal — after package exists, for ordered or gated slices.
- create-metaskill — agnosticism + lean structure.
