---
name: what-we-learned
description: >
  Closing ritual for learnings when there is little or no implementation left to hand off:
  write a dated "what we learned" handoff into the durable layer, state no feature backlog
  (or only optional ops), point next /init at the close—not a coding plan. Use when user
  says "/what-we-learned", "what we learned handoff", "handoff to give up", "learnings close",
  "session was only insights no work to continue", or ends a mission/experiment with
  reflection instead of next features. Complements /done (continue work) and /give-up
  (full product deprecation); does not replace either.
---

# /what-we-learned — Learnings Close (No Work to Continue)

Capture **what the session taught** as durable memory when the primary cargo is insight, not unfinished code.

**Not** `/done` (session close while a build track may continue).  
**Not** `/give-up` (full public deprecation + refuse writes + mission-end archive)—invoke `/give-up` when the *product* must shut down. Use this skill when you need the **handoff shape**: learnings-first, explicit stop, clean next `/init`.

Handoffs under the project's durable notes layer (`notes/…/handoffs/` or equivalent) are the memory that survives flushes.

## Usage

```text
/what-we-learned
/what-we-learned give-up close — no feature backlog
/what-we-learned capture: <bullet insights from chat>
```

If the user already stated the realizations in chat, distill them—do not re-argue them into a new roadmap.

## Core Loop

1. **Read durable layer** — north-star driver, lightweight current-reality notes, latest 1–3 handoffs. Know what *was* claimed so the close is accurate.

2. **Classify the close**
   - **Learnings-only** — experiment/insight session; product may still exist.
   - **Give-up handoff** — mission or product abandoned; **no** next build work (pair with `/give-up` if shut-down surface not already done).
   - **Hybrid** — some ops leftovers only (push, cloud teardown); label them *ops*, not backlog.

3. **Draft the handoff** (do not invent a product plan). Required sections:
   - Lead-in: **closing / give-up / learnings** — *not* mid-feature continuation
   - **What we learned** — numbered, plain language (structural insights, hard lessons, false assumptions)
   - **Key conflicts** (optional short table) — north star vs reality if relevant
   - **What is not handed off** — no open feature stack; refuse “continue building X” as next work
   - **Current state for /init** — abandoned / paused / insights-only (honest one-liner)
   - **For the next session** — **no feature backlog** (or only optional owner ops); point at any investigation archive; forbid inventing a coding plan to revive a closed mission

4. **Propose then write** (unless the user already ordered immediate write) — show proposed body + any one-line driver pointer. After approval (or explicit “just write”), create `notes/…/handoffs/YYYY-MM-DD-what-we-learned-….md` (or project’s handoffs naming convention).

5. **Light drivers only** — one-line pointer in lightweight current-reality notes and/or handoffs README if `/init` discovery needs it. Drivers stay short; **do not** revive active-mission language.

6. **Optional honesty check** — small in-repo test or script that **reads the real handoff file** and asserts markers: “what we learned”, give-up/close identity, “no feature backlog” / “no work to continue”, pointer to archive if one exists. No re-implementation of the essay inside the test.

7. **Commit** when the workspace expects durable memory on the primary branch. Push only if asked or already part of a larger ritual; document auth failure if blocked.

8. **Final message** — path to handoff; one-line “next `/init` reports discontinued/closed/insights-only”; no invented sprint.

## Rules

- **Learnings > unfinished tickets.** If there is no work to continue, the handoff must say so in the lead-in *and* in “For the next session.”
- **Do not smuggle a roadmap.** “Exploration pathway” / open *questions* for thought are fine; label them **not** product backlog.
- **Do not re-open a closed mission** in the handoff’s next steps.
- **Short by omission for drivers.** Rich narrative lives in the dated handoff.
- **Propose before write** unless the user explicitly waived that (goal harness / “just do it”).
- **Pair with `/give-up`** when public surface + mutators + full archive are still undone; this skill alone is the *memory close*, not full deprecation.
- **Pair with `/done`** only if residual *implementation* remains—then prefer `/done` for that track, or two docs with clear roles.
- Use `todo_write` when multi-step (draft → write → pointer → check → commit).
- Stay **project-agnostic** in this skill file; concrete names only in the target repo’s handoff content.

## Example (Abstract)

User: “We only learned the mission fails a structural test; there’s nothing to hand off—write a what-we-learned give-up handoff.”

Agent:

1. Reads drivers + latest handoffs.
2. Writes dated handoff: lead-in “give-up close / no work to continue”; **What we learned** (3–6 bullets from chat); **For the next session** = no feature backlog, read archive if any, do not invent revive plan.
3. One-line pointer in lightweight notes.
4. Optional: disk-read test asserts required phrases.
5. Commits; reports path; tells human next `/init` is a stop signal.

## Success Criteria

- [ ] Dated handoff exists under the durable handoffs directory.
- [ ] Lead-in marks **learnings / give-up / close**, not feature continuation.
- [ ] **What we learned** section present with real session insights (not empty placeholders).
- [ ] **For the next session** states **no feature backlog** (or ops-only) and does not prescribe reviving a closed mission.
- [ ] Points at investigation/archive doc if one exists; does not duplicate it wholesale.
- [ ] Drivers (if touched) stay short and still describe closed/abandoned/insights-only honestly.
- [ ] Optional structural check reads the **real file** and passes.
- [ ] Human can run `/init` next and not invent a coding plan by default.

## References

- Meta-system: `/init` (read durable layer first), `/done` (session handoff when work may continue), `/give-up` (full mission-end deprecation), handoffs as durable layer, north-star + lightweight current-reality drivers.
- Patterns: short drivers, rich dated handoffs; propose-then-write; honesty over sunk-cost continuation.
- Skill craft: lean, portable, zero repo-specific names in the skill text itself.
