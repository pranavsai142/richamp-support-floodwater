---
name: fieldgoal
description: >
  Corrective prospect-first meta-skill for goal work. Enforces upfront prospect + Brief (single source of truth/contract for foundational knowledge + per-slice testability), real reference sources, smallest verifiable slices, honest tests via your project's harnesses (no gamed visuals or demo-driven success). Orchestrates sub-slices using sequential/parallel patterns internally. Personas for subagents. Use when: "/fieldgoal <goal description>", "/fieldgoal deliver proper numerical grid foundation...", "run fieldgoal on the north star deliverable". Replaces patterns that let visuals drive impl. Project-agnostic, lean, token-efficient.
---

# /fieldgoal — Prospect-First Corrective Goal Delivery

The skill that enforces what goal-directed work must do: prospect first, lock Brief as contract, ground in real references, deliver only verifiable honest progress with your project's harnesses.

## Usage

```bash
/fieldgoal deliver proper numerical grid foundation for localized atmospheric model
```

```bash
/fieldgoal <detailed goal description, with reference sources to use and expected invariants>
```

Copy-paste the trigger + goal. The agent will prospect, create Brief, then execute.

## Core Loop

1. Parse goal. For trivial: deliver directly. For non-trivial: mandatory upfront work.

2. **Prospect + Brief creation (mandatory for non-trivial)**: Load prospector persona from canonical bundled path. Spawn subagent to produce Prospect Brief that explicitly defines: foundations present, per-slice testability using your project's harnesses/verifiers, real reference sources to ground against, honest success signals (numerical invariants, equality, no NaN), "just go" contract. Brief is injected everywhere.

3. Fill gaps if Brief flags them: spawn researcher(s) (researcher persona) using Mission + Investigate in: structure. Incorporate into Brief.

4. Decompose into smallest verifiable slices. Use sequential orchestration internally for dependent work; parallel for independent facets (reuse patterns).

5. For each slice:
   - Track with `todo_write`.
   - Frame task as **Mission** (narrative + insights + guardrails) + **Investigate in:** + **Run your project's harnesses if:** + **Deliver with verdicts**.
   - Spawn general-purpose subagent (full /implement loop) or direct impl, prepending appropriate persona. Inject Brief.
   - Execute slice. Run your project's harnesses/verifiers for gates (as named in Brief).
   - Post-slice: lightweight reviewer (reviewer persona) + harness results. Advance only on SUCCESS + clean gates + foundation intact for next.

6. Synthesize delivered artifacts against Brief. Confirm real verifiable progress (evidence-driven functions, reference fidelity).

7. Deliver final report + updated latest handoff in durable layer. Emit STATUS.

Use `todo_write` for all orchestration phases and slices.

## Rules

- **Strict agnosticism**: Zero project-specific paths, dates, tool names, concrete features, or local names anywhere. Use only "your project's harnesses", "the latest handoff in the durable layer", "real reference source (as specified)", abstract plans/examples. Every sentence must pass before commit.

- **Prospect-first always**: Brief is the single source of truth/contract. No implementation without it for non-trivial goals. "Just go" after one-time validation — stops only on real failure or unmet gates.

- **Personas for subagents**: Prepend full persona (prospector, researcher, reviewer, implementer) from canonical bundled paths when spawning. Subagents get Brief + task. Guardrails: "NO code changes unless authorized", "follow Brief exactly", "use persona report format".

- **Task framing**: All sub-work uses **Mission + Investigate in: + Run your project's harnesses if: + Deliver with verdicts**. Cite real observations.

- **Use `todo_write`**: For phases, per-slice tracking, and status.

- **Smallest verifiable slice + evidence-driven**: Ship only what passes real tests against reference. No invented dynamics.

- **Honest gates**: Always "Run your project's harnesses if:" per Brief (self-tests on pure modules, serve+manual+headless, numerical checks, build gates). No visual theater, painted metrics, or demo-only success.

- **Orchestration**: Internally delegate dependent slices to sequential patterns; independent to parallel. One lightweight final reviewer across all.

- **Reference fidelity**: Ground every technical claim or impl in the real reference source named in Brief. Evidence must drive shipped functions.

- **Durable layer**: Reference the latest handoff in durable layer for context. Update via done pattern if work crosses sessions.

## Example

User invokes:
```
/fieldgoal deliver proper numerical grid foundation for localized atmospheric model
```

Execution:
- Prospect (prospector persona) produces Brief locking "foundational knowledge + per-slice testability".
- Brief example (generic north star grid case):
  ```
  ## Prospect Brief: Numerical grid foundation for atmospheric model

  **Sharpened Objective**
  Deliver clean projection + full metrics + topology + minimal honest selfTest (boundary equality, spherical area conservation, no NaN) + data seeding hook. Solid reusable foundation ready for real multilayer solver work.

  **Success / "Done" Criteria**
  - Numerical invariants match reference exactly (no NaN, correct topology, conservation).
  - Per-slice selfTest passes using your project's harnesses (pure module tests, boundary/area checks).
  - Reference-faithful: uses only real reference source (grid utils, core invariants). No invented dynamics.

  **Critical Foundations...**
  - Projection math, metrics, topology from reference.
  - Test harnesses for selfTest on pure + serve/manual/headless variants.

  **Proposed Path**
  1. Core projection + metrics (smallest slice).
  2. Topology + selfTest harness integration.
  3. Data seeding hook.

  **Testability & Verification per Slice**
  - Run your project's harnesses: selfTest on pure functions; numerical equality; serve + manual + headless.
  - Reviewer: foundation solid for next + no visual-gamed criteria.

  **"Just Go" Contract**
  ...
  ```
- Decompose + orchestrate (sequential for slices here).
- Each subagent: persona + Brief + Mission/Investigate/Run harnesses/Deliver.
- Gates: harness selfTest (boundary/area equality, no NaN) + reviewer verdicts.
- Result: clean projection + metrics + full test + hook as reference-faithful deliverable. Ready for real work.

## Success Criteria

- Real verifiable progress against reference: passing exact numerical checks (equality, invariants, conservation), selfTest outputs clean, no NaN, correct counts/topology. Honest, not gamed.
- Per-slice testability gates (your project's harnesses named in Brief) + reviewer verdicts all green before advance.
- Brief created upfront; all work traceable to it.
- Skill file itself: lean, fully follows structure, zero specific references, actionable when dropped in any repo.
- Delivered work is solid, reusable, reference-faithful foundation (ready for next solver layers) not demo-only.
- Prevents dysfunctional goal patterns: forces reference + Brief + harness gates; never lets visual/demo success criteria substitute for verification.

## References

- Meta-system: init (read durable layer first), done (handoffs), handoffs/README, SOUL_DRIVER (north star + anti-spiral) generically.
- Patterns: parallel-implement (consolidation, STATUS blocks, lightweight reviewer, persona prepending), prospect/research/sequential-implement (Brief contract, just-go after upfront, Mission/Investigate/Deliver structure support).
- Skill creation: create-metaskill (project-agnostic, lean, prospect-first, involved skill structure).
- Research/prospect: Brief as contract, real reference grounding, honest testability.
