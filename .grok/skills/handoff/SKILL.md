---
name: handoff
description: >
  Meta-skill for converting a plan document into a high-quality structured design document (technical requirements, user stories, technical guidelines, boilerplate/placeholder code, key decisions, PR plan) plus a rich done/handoff document. Saves the original plan and the produced design document into the project's durable handoff layer. Captures the spirit of proven prompts that generate clear, implementable artifacts with full traceability. Use at the end of planning, design work, or feature definition. Project-agnostic.
---

# /handoff

**Converts your plan into durable artifacts: a structured design doc and a done-style handoff. Saves plan + design to the handoffs layer in the durable memory. Produces the same high-quality output style that has worked well for technical requirements, stories, guidelines, and boilerplate.**

## Usage

```bash
/handoff <path-to-plan.md or "document the following plan: ...">
# or
/handoff   # (uses current context + latest handoff as source for plan-like summary)
```

## Core Loop

1. **Prepare input**: Read the provided plan document (or synthesize a concise plan summary from current work + latest handoff/drivers in the durable layer). Use todo_write.

2. **Produce the design document** (using writer subagent):
   - Spawn a writer subagent (general-purpose) with the handoff-design-writer persona.
   - Prompt = persona + "Document the plan and convert to: technical requirements, user stories, technical guidelines, boilerplate/placeholder code. Include Key Decisions and PR Plan at bottom."
   - The writer explores relevant harnesses/code patterns (generically), then writes a complete design doc.
   - Output to a temporary or dated design artifact.

3. **Produce the done/handoff document**:
   - Use the handoff-done-writer persona (or follow the done ritual).
   - Capture rich narrative: what was accomplished, decisions, state, open items, next steps, citations to the design doc.
   - Date it appropriately.

4. **Save to durable layer**:
   - Copy/save the original plan to the handoffs directory.
   - Save the new design document to the handoffs directory (alongside the plan).
   - Write the done document as the primary handoff entry (or as a companion).
   - Lightly note in lightweight drivers if relevant (following done principles).

5. **Verify and report**:
   - Confirm files are saved.
   - Present summary: locations of saved plan + design, the done doc content (propose first if writing drivers/handoffs).
   - Success when the artifacts are clear, implementable, and portable.

Use `todo_write` for the steps. Always prospect/validate foundations before deep writing if the plan is vague.

## Personas

When spawning subagents for writing steps, prepend the full content of the lean persona files located alongside this skill:

- `personas/handoff-design-writer.md` (for the design document conversion step)
- `personas/handoff-done-writer.md` (for the rich done/handoff capture step)

These are kept short (<60 lines) and portable. The skill expects them to be present in the same package when the meta-skill is copied.

## Rules

- **Agnosticism first**: Never hardcode project paths, names, dates, specific tool binaries, or feature details. Use "your project's handoffs directory (durable layer)", "the provided plan document", "your project's relevant harnesses/verifiers", "latest handoff".
- The skill must work when copied to any repo that has the meta-system (init/done/seed + handoffs).
- Always produce both the design document and a done document.
- Save the plan + design document into the handoffs layer (the spirit of "save both plan.md and the new technical design doc in handoffs").
- Leverage subagents with the personas above for the writing steps.
- Use todo_write for orchestration.
- Propose handoff/done content before writing to durable layer.
- Token-efficient: keep the skill lean; the personas are short.
- If the input is a completed feature rather than a raw plan, first synthesize a "plan-like" summary before conversion.

## Example (Generic)

User has a plan for "robust along in generalized add" and runs:

`/handoff plan.md`

The skill:
- Reads plan.md
- Spawns writer with handoff-design-writer persona + conversion instructions
- Produces `...-design.md` with requirements, stories ("As a geometry author, I can request large Along..."), guidelines (L/B ownership for protruding stencils, etc.), boilerplate for the dispatch changes, Key Decisions, PR Plan.
- Spawns for done part: produces rich handoff capturing the session + reference to the design.
- Saves plan.md copy + the design.md into the handoffs dir.
- Reports the saved locations and proposes the done handoff.

Output is portable and matches the quality of successful prior runs.

## Success Criteria

- The produced design doc is structured exactly as requested (requirements, user stories with AC, guidelines, boilerplate code, Key Decisions, PR Plan).
- A done/handoff doc is also created.
- plan + design are saved in the handoffs layer.
- All content is project-agnostic in the skill itself.
- Future agents can run the skill in a fresh repo and get usable artifacts.
- Traceability: the design clearly derives from the input plan.

## References

- Meta-system: init (read durable layer), done (rich handoffs + light drivers), seed, handoffs layer as single source of memory.
- Design conversion process: the proven prompt spirit for turning plans into requirements/user-stories/guidelines/boilerplate + saving plan+design.
- Subagent patterns: persona prepending, writer/reviewer loops for quality (adapt from design patterns).
- Related: prospect for upfront validation when needed, sequential-implement for following the PR Plan.

The handoff skill turns good plans into durable, high-quality artifacts that survive across sessions and repos.
