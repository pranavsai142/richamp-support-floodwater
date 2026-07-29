---
name: prompt-claude
description: >
  Design a high-success prompt for Claude (or similar agent) to produce a complete CLAUDE_README.md or handoff document. Encapsulates the structure, sections, tone, and content that delivered strong one-shot results on complex slices: explicit north star, mandatory reads in order, current state, core contracts/invariants, ordered plan, verification matrix, anti-spiral guardrails, and measurable "finished" bar. Invoke via "/prompt-claude", "/prompt-claude for <task>", or "design a claude prompt for a handoff on <work>".
---

# /prompt-claude — High-Success CLAUDE_README / Handoff Prompt Designer

This metaskill produces a ready-to-paste prompt that tells Claude how to author a durable, high-fidelity CLAUDE_README or follow-on handoff. It is built directly from the elements that produced reliable progress on ambitious, multi-phase technical work.

## Usage

```bash
/prompt-claude
/prompt-claude for delivering the full analysis path on top of a trusted geometry core
/prompt-claude for <precise description of the ambitious slice or north-star outcome>
```

The running agent gathers context from the project's durable layer then emits a complete, copy-pasteable prompt (and optionally guidance on where to save the resulting handoff).

## Core Loop

1. **Load the durable layer** — Read SOUL_DRIVER (north star + philosophy + anti-spiral rules), latest DEV_NOTES (narrative state), the 1-3 most recent handoffs, any existing CLAUDE_README or prior handoff documents, living mental-model docs (wiki chapters or equivalents), and key source files. Simulate or run the project's `/init` equivalent.

2. **Extract what worked**:
   - Verbatim north-star quote and philosophy.
   - Concrete "finished looks like" (human-sittable behaviors + "the X must be boring").
   - Mandatory reads list in the exact order that forced internalization.
   - Honest current state (solid parts + admitted gaps).
   - Core contracts and invariants, captured verbatim where possible (hygiene sequences, ownership rules, identity rules, buffer discipline, etc.).
   - Research/priors synthesis (oracles, papers, reference code mappings) if relevant.
   - Verification matrix and harness usage patterns that replaced "vibes".
   - Anti-spiral lessons (prune rules, invariants > instrumentation, explicit sections future handoffs must contain).

3. **Assemble the prompt using the proven canonical structure** (use this order and emphasis):
   - Strong positioning ("You are positioned as the model that can complete ambitious long-running technical implementations in one strong push").
   - Immediate instructions + "do not skip" + quiz questions ("if you cannot answer these, re-read").
   - North Star section (verbatim quote + what "finished" means for a human tester).
   - Brief history / rabbit-hole context (enough to avoid re-living it).
   - Core Fundamentals / Key Concepts (condensed, with direct mapping to code constructs).
   - Current State (precise + honest, citing recent work and remaining glitches).
   - Plan to completion (dependency-ordered phases or steps; "after each phase, run the full verification matrix"; "use your project's harnesses").
   - Critical Requirements and known gotchas (arclength discipline, specific mappings, etc.).
   - Verification Matrix (ruthless, concrete gates using harnesses + parity + human "feels right").
   - Anti-patterns / Process Rules (include explicit requirement that future handoffs contain anti-patterns and invariants sections).
   - Output expectations (produce the handoff document, update durable layer via your /done equivalent, use todo_write for multi-step, etc.).

4. **Harden for one-shot success** — Add repetition of "internalize before any code", "smallest change that preserves contracts", "run verification after every structural change", "report gaps explicitly rather than paper over".

5. **Emit the prompt** — Output the full text in a clean ``` block labeled for easy copy-paste. Also emit a short usage note and suggested handoff filename (e.g. CLAUDE_<SLICE>_HANDOFF.md or 2026-MM-DD-<topic>-handoff.md).

## Rules

- The skill file itself must stay strictly project-agnostic: "your project's durable layer", "SOUL_DRIVER equivalent", "latest handoff", "your verification harnesses/skills (as named in context)", "the L/B-style ownership paradigm or equivalent invariant".
- In the *generated prompt*, use the concrete file names, chapter numbers, function names, and invariant wording gathered from the target project's sources.
- Prioritize empirically successful elements: mandatory reads first and strict, north star + "boring" repeated, verbatim contracts, explicit human tester success bar, phase-by-phase verification gates, positioning as capable of one strong push.
- Force internalization: include a short list of questions Claude must be able to answer from the sources before touching code.
- Always require use of the project's harnesses/verifiers instead of "looks good".
- Include anti-spiral instructions: prune on explicit orders, follow "smallest change", invariants > extra diagnostics.
- Keep generated prompts substantial (detailed enough for one-shot) but not bloated. Typical successful ones are 250-700 lines for complex slices.
- Never fabricate unverifiable technical claims inside the prompt.

## Example Output (Abstracted Structure)

```
You are Claude (or the target agent), positioned as the model that can complete ambitious, long-running technical implementations in one strong push for this project.

**Immediate instructions (do not skip):**

1. Read `SOUL_DRIVER.md` in full...
2. Read the latest handoff...
3. Read these specific chapters...

**North Star**
> We are building a stable, arbitrarily attachable, high-order ... system ...

What "finished" actually means:
- A human can sit down and ...
- Every seam must pass harness X with zero issues.
- ...

**Mandatory Reads (strict order)**
...

**Current State**
...

**Core Contracts (never break)**
- Ownership rule: ...
- Post-mutation hygiene: autoLink + bumpVersion + ...
- ...

**Plan (ordered)**
Phase 1: ...
After Phase 1: run full verification matrix using ...
Phase 2: ...

**Verification Matrix**
- Gate A: all suites 0 failures.
- Gate B: reproduce reference cases within tolerance.
- Gate C: human tester pass: create/save/reload/continue with full trust.

**Critical Requirements**
- Use equal-physical-spacing / arclength discipline...
- Smallest change preserving contracts.

**Anti-spiral Rules**
...
```

## Success Criteria

- The emitted prompt, when fed to Claude (or equivalent), produces a handoff that reliably drives correct, verifiable completion with high first-attempt success rate (matching the two high-success examples that motivated this skill).
- The prompt contains the full set of structural elements proven to correlate with success (positioning, north star, mandatory reads, invariants verbatim, current state, ordered plan, verification matrix, anti-spiral).
- Output is immediately actionable: user can copy the block and paste to Claude with minimal editing.
- The skill itself contains zero project-specific references, paths, dates, or feature names.
- Future users in other repos can drop the skill in and get equivalent prompt quality.

## References

- Meta-system: handoffs/README (durable layer + required anti-patterns/invariants sections in handoffs), /init (read SOUL_DRIVER + DEV_NOTES + latest handoff(s)), /done (capture progress as dated handoff).
- SOUL_DRIVER: north star quotes, "the X must be boring", anti-spiral enforcement, user-is-tester, smallest change that preserves contracts.
- DEV_NOTES: living lightweight narrative state.
- Proven patterns: strong upfront internalization requirement + quiz, explicit measurable human success bar, phase-gated verification using project harnesses, verbatim contracts, honest gap reporting.
- Related: create-metaskill (this is one), create-skill, init, done, sequential-implement / parallel-implement patterns (Brief + Mission/Investigate/Deliver for sub-work), prospect (for sharpening the task description before prompt design).

Use todo_write when the task of gathering + synthesizing for a large slice is itself multi-step.
