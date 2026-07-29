# NORTH STAR TODO — <short program name>

**Purpose:** Durable living progress tracker for the recursive implementation loop.  
**Contracts:** design handoff · program handoff · loop prompt · source vision/plan  
**Rules:** (1) This file is the single progress truth. (2) Status: `pending` | `in_progress` | `done` | `blocked` | `cancelled`. (3) One `in_progress` WP. (4) No `done` without Evidence. (5) Do not reorder phases; may split WPs into sub-bullets. (6) On block: set `blocked` + reason. (7) Stop when all coverage rows and WPs are `done`.

**Last updated:** <date>  
**Current focus:** <WP-id>  
**Locked stack:** <one-line locks>

---

## Summary dashboard

| Phase | Label | Progress |
|------:|-------|----------|
| 0 | <spec/foundations> | |
| 1 | <first delivery phase> | |
| … | … | |

**Overall:** <phrase> · next = **<WP-id>**

---

## Vision coverage (every source element)

Group by source sections. One row per element.

| ID | Item | Status | Notes / WP |
|----|------|--------|------------|
| VIS-001 | <element from inventory> | pending | WP-? |
| VIS-002 | … | pending | |

*(Add groups: principles, entities, APIs, compute, UI, phases, etc. IDs stable forever.)*

---

## Work packages (implementation order)

| ID | Title | Status | Depends | Verify | Evidence |
|----|-------|--------|---------|--------|----------|
| WP-0 | <foundations already done if any> | done/pending | — | <how> | |
| WP-1 | <first open slice> | pending | — | <harness/command> | |
| WP-N | … | pending | WP-… | … | |

---

## Session log (append-only)

| Date | Session | WP | What changed | Next |
|------|---------|-----|--------------|------|
| <date> | package setup | WP-0 | Living TODO created | WP-1 |

---

## How to update

After each slice: mark WP done + evidence → flip related VIS-* rows → append log → update dashboard + Current focus.
