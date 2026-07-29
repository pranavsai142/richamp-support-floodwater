---
name: parallel-field-goal
description: >
  Orchestrate parallel fieldgoal executions on independent facets of a complex goal. Each facet runs prospect-first with Brief as contract, delivers smallest verifiable slice using real reference sources named in Brief, verified only via your project's harnesses. Spawn subagents, wait, synthesize evidence and readiness. Use when: "/parallel-field-goal <overall goal>", "run parallel fieldgoals on these facets", "parallel fieldgoal slices for operators".
---

# /parallel-field-goal — Parallel Prospect-First Fieldgoal Orchestration

Executes multiple independent fieldgoal legs simultaneously on separable work while enforcing upfront prospecting, Brief contracts, reference fidelity, and harness-only verification.

## Usage

```bash
/parallel-field-goal deliver three core operators for the foundation using independent slices
```

Optionally provide explicit facet list after the goal description.

## Core Loop

1. Parse overall goal. Decompose into (or accept) independent facets. Use high-level prospect if decomposition unclear.

2. For every facet:
   - Produce or validate a Prospect Brief (foundations, per-slice testability with harnesses, reference sources, success gates, just-go contract).
   - Build task: full persona + Brief + **Mission** (narrative/insights/guardrails) + **Investigate in:** + **Run your project's harnesses if:** + **Deliver with verdicts**.

3. Spawn one subagent per facet in parallel. Prepend the parallel-fieldgoal-runner persona (or canonical equivalents).

4. Track all legs with todo_write. Wait for completion.

5. Lightweight synthesis review: verify shared foundations intact, aggregate evidence, check cross-slice compatibility.

6. Produce combined report + STATUS. Prepare durable layer update via done pattern if work is meaningful.

## Rules

- Brief (prospect-first) is the single source of truth for every parallel leg. No implementation without it for non-trivial facets.
- Strict project-agnosticism everywhere: use only "your project's harnesses/verifiers (as named in the Brief)", "the latest handoff in the durable layer", "reference source(s) named in Brief".
- Parallel only for independent facets. Sequence dependent work.
- Each subagent must execute the exact harnesses and gates listed in its Brief. No visual/demo/theater substitutions.
- Every technical decision and shipped artifact must cite the real reference source(s) named in the Brief.
- Use todo_write for orchestration phases and per-leg tracking.
- Subagent guardrails (from persona): NO code changes unless authorized by the Brief + task. Preserve prior invariants.
- Stop the whole run on any leg that cannot meet its gates. Do not paper over failures.
- Token-efficient reports and prompts.

## Example

User invokes:
```
/parallel-field-goal implement three core operators for the foundation
```

Execution:
- Decomposes (or accepts): Facet A, Facet B, Facet C (independent operators on shared base).
- Per facet: Brief locks shared foundation contract + specific harness gates + reference source citations.
- Spawns three parallel runners (persona + Brief + Mission/Investigate/Run harness/Deliver).
- All three return PASS with verbatim harness output and numeric invariants.
- Synthesis: "Three independent operators delivered. Shared foundation verified intact by all legs. Ready for composition slice."
- Evidence collected; todo status closed.

## Success Criteria

- Every leg completes its Brief with green harness results and verbatim evidence.
- Synthesis confirms no regression on shared foundations and that progress is independently verifiable.
- All code/comments are reference-faithful per the Briefs.
- Orchestration used todo_write and produced clear STATUS.
- The skill itself remains lean, fully agnostic, and portable.

## References

- Meta-system: init (read durable layer first), done (handoffs), handoffs/README, SOUL_DRIVER (north star + invariants), DEV_NOTES (lightweight state).
- Patterns: prospect (Brief as contract), fieldgoal (per-slice prospect + harness discipline), parallel-implement (subagent spawning, STATUS, lightweight reviewer), sequential-implement (when ordering required).
- Personas: parallel-fieldgoal-runner (this skill), plus canonical prospector/implementer/reviewer.
- Skill style: create-metaskill rules (agnostic + lean).
