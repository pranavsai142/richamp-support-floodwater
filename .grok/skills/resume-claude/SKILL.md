---
name: resume-claude
description: >
  Design a high-success continuation prompt for Claude (or similar agent) to produce the next phase of a CLAUDE_README or handoff document. Builds directly on a prior prompt-claude output. Same style and technical rigor, but assumes the target has already received and internalized the previous prompt — no redundant full init, mandatory re-reads of everything, or quiz on basics. Focus on "building on the previous prompt which covered...", updated current state, next ordered phases, and verification. Invoke via "/resume-claude for <next phase or continuation task>".
---

# /resume-claude — Continuation Prompt Designer (Builds on Prior prompt-claude)

This metaskill produces a ready-to-paste follow-on prompt that tells Claude how to author the next durable handoff or section, continuing seamlessly from a previous prompt-claude delivery. It preserves the proven structure, tone, and success patterns while eliminating redundancy.

## Usage

```bash
/resume-claude
/resume-claude for the UI overhaul phase following the stencil creation prompt
/resume-claude for <precise description of the continuation or next north-star slice>
```

The running agent gathers lightweight context from the project's durable layer and the prior prompt's scope, then emits a complete, copy-pasteable continuation prompt (plus guidance on saving the resulting handoff).

## Core Loop

1. **Lightweight context load** — Read the latest handoff in the durable layer, recent DEV_NOTES updates, and any reference to the scope of the previous prompt-claude task (e.g., what was already delivered). Do not simulate a full `/init` or re-read the entire prior prompt's mandatory list unless gaps are explicit.

2. **Extract continuation needs**:
   - What the prior prompt delivered (from latest handoff or summary).
   - Updated honest current state (what is now solid vs. remaining gaps).
   - Next dependency-ordered phases or refinements.
   - Any new contracts/invariants that emerged.
   - Refined verification gates for the remaining work.
   - Anti-spiral reminders carried forward.

3. **Assemble the continuation prompt** (same canonical structure as prompt-claude, but framed as continuation):
   - Strong positioning ("Building on the previous prompt you received...").
   - Immediate instructions focused on continuation ("Do not re-read the full prior mandatory list unless explicitly needed; pick up from where the last handoff left off").
   - Updated North Star / "finished" for the remaining slice.
   - Brief "what was already accomplished" context (short, no rabbit-hole rehash).
   - Current State (precise + honest update).
   - Plan (next phases only; "after each, run the full verification matrix using your project's harnesses").
   - Critical Requirements (carry forward + any new gotchas).
   - Verification Matrix (updated gates).
   - Anti-patterns / Process Rules (require future handoffs to reference the prior one and contain anti-patterns/invariants).
   - Output expectations (produce the continuation handoff, update durable layer via /done, use todo_write).

4. **Harden for seamless continuation** — Emphasize "smallest change preserving all prior contracts", "run verification after every structural change", "report gaps relative to what was already delivered", "internalize only the deltas".

5. **Emit the prompt** — Output the full text in a clean ``` block. Also emit short usage note and suggested continuation handoff filename (e.g. 2026-MM-DD-<topic>-continuation-handoff.md or CLAUDE_<SLICE>_CONTINUATION.md).

## Rules

- The skill file itself must stay strictly project-agnostic: "your project's durable layer", "the latest handoff", "your verification harnesses/skills (as named in context)", "the prior prompt-claude task's scope".
- In the *generated prompt*, reference the prior delivery generically ("the previous prompt which covered X") and use concrete names only for new elements.
- Prioritize the same empirically successful elements as prompt-claude, but stripped of re-initialization.
- Force focus on deltas: the prompt must instruct the target to avoid re-reading everything and instead continue from the last handoff.
- Always require the project's harnesses/verifiers.
- Include anti-spiral: "prune on explicit orders", "smallest change", "invariants > extra diagnostics".
- Keep generated prompts substantial but not bloated (typically shorter than the initial prompt-claude one because of continuation framing).
- Never fabricate claims.

## Example Output (Abstracted Structure)

```
Building directly on the previous prompt you received (which established [short summary of prior scope]), you are Claude, positioned as the model that can complete the next phase of ambitious technical implementations for this project in one strong push.

**Immediate instructions (do not skip — focus on continuation only):**

1. Read the latest handoff from the prior delivery.
2. Read only the new or updated sections relevant to this phase (do not re-read the full prior mandatory list unless a specific gap is called out).
3. ...

**Updated North Star (continuation)**
> Building on the established [prior], now deliver [next]...

What "finished" now means for this phase:
- ...

**What Was Already Delivered**
(Short summary only.)

**Current State (update relative to prior)**
...

**Core Contracts (carry forward + any deltas)**
- ...

**Plan (next phases only)**
Phase N+1: ...
After each: run full verification matrix using your project's harnesses.

**Verification Matrix (updated gates)**
...

**Critical Requirements & Gotchas**
...

**Anti-spiral Rules**
...
```

## Success Criteria

- The emitted prompt, when fed to Claude after the prior one, produces a clean continuation handoff with high first-attempt success, without forcing redundant re-initialization.
- Contains the full successful structural elements, adapted for continuation (positioning as follow-on, deltas-focused current state/plan, carried-forward invariants).
- Immediately actionable and non-redundant.
- The skill itself is project-agnostic and token-efficient.
- Future users in other repos can use it after any prompt-claude-style delivery.

## References

- Meta-system: handoffs/README, /init (light use), /done, prompt-claude (the style this extends), create-metaskill.
- Patterns: continuation after prior prompt, "building on..." framing, same verification harnesses, todo_write for multi-phase.
- Skill writing: lean, agnostic, focused on deltas.

Use todo_write when gathering + synthesizing for the continuation prompt.
