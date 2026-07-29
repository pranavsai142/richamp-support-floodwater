---
name: give-up
description: >
  Full project/product give-up ritual: durable mission-end archive (realizations, key conflicts, exploration pathway), public shut-down surface, refuse new participation writes, mark drivers/README abandoned, optional sibling repos, tests for discontinued behavior, commit/push main, external-asset deprecation checklist. Use when user says "/give-up", "full give up routine", "abandon this project", "shut down the product", "discontinue and archive why", or ends a mission with clean public deprecation—not a pivot to a new feature.
---

# /give-up — Full Mission End & Clean Deprecation

Execute an honest **product/project abandonment**: the public surface reads as shut down, memory records *why*, participation is refused, docs stop claiming active mission. Prefer deprecation over history erasure.

This is **not** `/done` (session handoff while work continues). This is **mission closed**.

## Usage

```text
/give-up
/give-up also the sibling repo at <path-or-name>
/give-up full: public shut-down + archive realizations + refuse writes + push main
```

If the user already stated the sociological/strategic *why* in chat, capture it into the durable archive—do not re-argue them out of it.

## Core Loop

1. **Confirm scope** — Full give-up (default) vs soft pause. List targets: this repo + any siblings the user named. Use `todo_write` for multi-step work.

2. **Read durable layer** — SOUL_DRIVER, DEV_NOTES, latest handoff(s). Internalize what *was* claimed so deprecation language is accurate.

3. **Archive the why** — Write one durable investigation doc under the notes/memory layer (e.g. `notes/GROK/…GIVE_UP…` or equivalent). Required sections:
   - **Societal / strategic realizations** (why the mission fails the power/value test)
   - **Key conflicts** (north star vs reality, table or bullets)
   - **Exploration pathway** (open questions for *thought*, explicitly *not* a product roadmap)
   - Short technical epitaph + closing line  
   Keep owner-session honest; do not claim peer review.

4. **Public shut-down surface** — Primary and former product URLs converge on discontinued messaging. Aesthetics: muted “service closed” page, clear give-up notice, no invitation to use the product as live. Escape any user-controlled path/query text before HTML embed (reflected XSS).

5. **Refuse participation** — At the request boundary, mutating membership/governance/write paths return discontinued/gone/forbidden semantics (not silent success). Health/probe endpoints may stay up but must *report* discontinued if the product is dead.

6. **Deprecate docs** — README + SOUL_DRIVER + DEV_NOTES (and sibling mirrors) state **abandoned / discontinued**, point at the archive, and do **not** present “join / vote / train / ship mission X” as current. Dated handoff for the give-up session.

7. **Tests & harnesses** — Assert shut-down HTML + refused writes on the *real* entry path. Skip/rewrite live-feature e2e so green does not mean “product still operates.” Capture evidence under the session scratch dir when a goal harness requires it.

8. **Git** — Commit on `main` (or the repo’s primary branch). Push `origin` primary branch. If auth fails, document the attempt; leave local main complete.

9. **External assets** — Checklist only when credentials allow: hosting, data stores, domains, CI secrets, related services. Owner-only steps are listed, never faked as done.

10. **Close** — Short public summary: what is dead, where the why lives, what the owner must still push/tear down.

## Rules

- **Honest exit > sunk-cost polish.** Do not “make the shut-down addictive” or pivot into a generic SDK unless the user explicitly starts a *new* mission with a new soul.
- **Deprecate, don’t erase history.** Keep code in git; gate behavior at the edge.
- **One shut-down story.** Half-live pages that still invite sign-up are a failed give-up.
- **Archive is the durable why.** Chat is not enough; notes layer survives flushes.
- **Exploration pathway ≠ backlog.** Label it so future `/init` does not revive tickets.
- **Agnostic language in this skill; concrete paths only in the target repo’s files.**
- **Sibling repos** only when named or clearly paired; same abandon story, no half-alive dojo/lab for a dead product.
- **Security on the corpse:** escape embedded request data; discontinued JSON must not 500.
- **Push is part of the ritual** when the user asked for it; auth failure is documented, not ignored.
- Use `todo_write` for the multi-step ritual. Prefer shipped-entry tests over re-implemented page strings in tests.

## Example (Abstract)

User: `/give-up` after realizing the product is process-without-power (or other structural dead-end).

Agent:

1. Writes `notes/…/GIVE_UP_INVESTIGATION.md` with realizations / conflicts / pathway.
2. Adds a discontinued flag + single shut-down HTML for former product routes; writes → 410/403-style discontinued payload.
3. Rewrites README + drivers to “abandoned”; handoff dated today.
4. Tests: home body contains shut-down markers; POST mutator returns discontinued; archive has the three sections.
5. Commits main; attempts push; fills external checklist (hosting suspend = owner-only if no creds).

## Success Criteria

- [ ] Public primary surface is unmistakably discontinued (not operating product UX).
- [ ] Durable archive has realizations, key conflicts, exploration pathway.
- [ ] README + living drivers state abandoned and point at the archive.
- [ ] Mutating participation paths refuse with discontinued semantics.
- [ ] Tests (or harness checks) prove shut-down HTML + refused writes on real entry points.
- [ ] Give-up committed on primary branch; push done or auth failure recorded.
- [ ] Sibling targets (if any) carry the same abandon story.
- [ ] External teardown is checklisted honestly (done / owner-only / N/A).

## References

- Meta-system: `/init` (read truth first), `/done` (session handoff—use *after* or *as part of* give-up for the dated handoff), `notes/GROK/handoffs/`, SOUL_DRIVER (mission closed), DEV_NOTES (current reality = discontinued).
- Patterns: deprecation at request boundary; harness verification with real entry paths; evidence in session scratch when required.
- Skill craft: keep this file lean; copy to any repo with the pragmatic notes layer and it still applies.
