---
name: research
description: >
  Orchestrates prospector (always first) + one or more researcher subagents (parallel when facets are independent). Takes vague or specific requests. The skill runs prospecting to define the problem and path, spawns researchers, waits, and synthesizes precise technical findings with citations, foundation validations, and actionable output. Research is intentionally vague on purpose — the personas turn it into exactly the depth/breadth needed. Output is what sequential-implement (or a human) needs to "just go". Project-agnostic meta skill. Use when the user says "/research <topic>", "research the ... case deeply", "go down the rabbit hole on X and return with the exact context", "prospect then research ...", etc.
---

# /research

**Orchestrates prospector (always first) + one or more researcher subagents (parallel when facets are independent). Turns vague or specific requests into precise, citable context with foundations + testability validated — exactly what sequential-implement needs to "just go".**

## Usage

```bash
/research <topic or request>
```

## Core Loop

1. Parse request + context.
2. **Prospect first**: load prospector persona, spawn subagent for Brief (contract). Brief is source of truth.
3. Plan 1+ facets from Brief (parallel ok for independent areas).
4. Load researcher persona. Spawn general-purpose subagent(s) per facet: prompt = persona + Brief + facet desc. (Researchers may spawn more.)
5. Wait. Extract reports + STATUS from each.
6. (Optional) synthesize if many.
7. Present final report + Brief + citations + next steps (e.g. to /sequential-implement).

Use `todo_write`.

Persona paths (canonical):
- prospector: `/Users/pranav/.grok/bundled/skills/shared/personas/prospector.md`
- researcher: `/Users/pranav/.grok/bundled/skills/shared/personas/researcher.md`

## Rules

- Prospect first always. Brief is the contract.
- When spawning a researcher: prompt = [full researcher persona] + Brief + the detailed task from the request (which may be framed as **Mission** with user insights + **Investigate in:** targets + **Run [harness] if ...** + **Deliver** requirements). Instruct the subagent to follow the persona exactly, address the Mission directly, use the structure in its persona for the report, and validate against the provided narrative.
- Prepend researcher persona for subagents (it defines report format/process – follow it). The persona already encodes good research prompt structure (Mission restatement, Investigate breakdowns, verification runs, verdicts per insight).
- Synthesize with citations.
- Output must be usable by /sequential-implement.
- Use todo_write.

Now execute the steps above.
