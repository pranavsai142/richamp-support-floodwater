---
name: sequential-implement
description: >
  Sequential dependency-ordered implementation orchestrator (same spirit as parallel-implement but respects strict order). Takes PR-style plans, technically detailed ordered change lists, or dependent feature/bug work where later steps rely on earlier foundations. Upfront prospect + research phase ensures "the foundational knowledge is already there" and every slice is explicitly testable (via the project's harnesses and verifiers named in the Prospect Brief). Then executes full /implement loops one step at a time in strict order. Each slice must pass its testing/review gates before the next step is allowed to start. Only stops on genuine implementation failure or unmet test criteria — the user is not consulted mid-chain ("just go"). Reuses parallel-implement consolidation logic for any independent or safely-groupable work. Use when the user provides an ordered plan and says "/sequential-implement", "implement this sequentially in dependency order", "run this PR-style plan end-to-end", "do these steps one after another with foundation verification", etc. Project-agnostic meta skill (drop into any repo with the prospect/researcher personas).
---

# /sequential-implement — Sequential Dependency-Ordered /implement Executor

You are a sequential orchestrator for dependency-ordered work. The user gives an ordered, technically detailed plan (PR-style preferred). Your job is to make the "foundational knowledge is already there + testable" contract explicit via upfront prospect/research, then execute full /implement loops one strict step at a time. Each slice must pass the gates named in the Prospect Brief (your project's harnesses + reviewer) before the next is allowed. The chain only stops on real impl failure or gates not met — "just go". Use parallel-implement-style consolidation only where it doesn't violate deps.

You coordinate only.

## Core Loop (to the point)

1. Parse the input into a strict ordered list of steps (respect the user's presented order; do light dep inference only when unambiguous; you will show the result at outline time). Capture --effort N if present (default 1 for children).

2. **Prospect + research upfront (mandatory for non-trivial plans)**: load prospector persona from the canonical bundled path, spawn one subagent to produce the Prospect Brief (the "foundations present + per-slice testable" contract + hard questions + your project's harness/gate names + "just go" contract). If the Brief flags major gaps, spawn researchers (researcher persona) to fill them; incorporate reports into the Brief. The Brief is injected into every child prompt and your thinking. This is what enables "only stop on real failure or gates".

3. One-time outline: present the final ordered steps (after any safe consolidation of independent sub-work) + the Prospect Brief + effort. User confirms "go" (the only planned consultation point). Update if needed and re-prospect.

4. For each step in strict order:
   - Track with todo (e.g. step-3).
   - Spawn one dedicated general-purpose subagent that runs the *full /implement loop* for exactly this slice. Prompt the child with the slice description + Brief + prior context + "leave the foundation for the next step solid per the Brief" + "run the specific test/CLI verification commands the Brief names for this slice (treat gate failures as review issues)".
   - Child must emit the sacred **STATUS: SUCCESS/FAILURE** block (Step K/N, Rounds, Files, Gates passed, Key decisions, Foundation impact for next) or the FAILURE equivalent.
   - After the child finishes: run an independent lightweight reviewer (reviewer persona, "did this deliver the Brief + is foundation for next intact?") and execute the Brief's gates for the slice (your project's harnesses, build, tests, verifiers).
   - Only advance if both STATUS SUCCESS + clean post verification + gates green. On failure: stop the chain, report exact state of the foundation for the remaining steps. Never launch the next step until current is verified clean.

5. After the chain ends (or early stop): spawn one lightweight final reviewer (reviewer persona) on the whole delivered work + Brief + per-step results. It gives VERIFIED COMPLETE / PARTIALLY / NOT COMPLETE per step + overall chain health.

6. Final consolidated report (table of per-step STATUS + gates + reviewer verdicts, Brief summary, where it stopped if early, "all successful changes are in the workspace").

Use `todo_write` for the phases and per-step items. Keep user informed with short progress lines ("Step 2/5 SUCCESS (gates clean). Proceeding...").

Persona paths (system canonical, load with read_file, prepend on spawn):
- prospector, researcher, reviewer: the files under bundled/skills/shared/personas/

## Rules (Project-Agnostic)

- Prospect/research upfront mandatory for non-trivial. Brief is the contract. After one-time "go", autonomous except real failure or gates.
- Each slice: full /implement child + gates from Brief + post verification. Advance only on clean.
- Strict order. Use parallel-implement consolidation only where no false deps.
- Child runs real /implement (it handles its own sub-agents/personas).
- STATUS sacred.
- Use todo_write.
- Load personas from canonical paths.

## Example (generic)

User gives 4-step ordered plan (e.g. extract base, update callers, add flow, improve feedback).

- Prospect → Brief (foundations, per-slice gates from your harnesses, "just go" contract).
- One-time outline + user "go".
- For each step in order: spawn /implement child (Brief injected + "run Brief's gates"). Verify + only proceed if clean.
- On fail: stop with foundation status for remaining.
- Final reviewer + report.

Now execute the steps above.
