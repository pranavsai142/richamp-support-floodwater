---
name: create-metaskill
description: >
  Create a new project-agnostic meta-skill (research, prospect, sequential-implement, etc.) or supporting persona. Encapsulates all learnings for portable, token-efficient skills: strict agnosticism (generic language only: "your project's harnesses", "the latest handoff", abstract plans; zero project paths, tool names, features, dates), token conservation (lean files, prune junk/duplication/bloat/philosophy dumps), structure (concise skills with purpose + how-to + success; involved skills with checklists + core loop + rules + example + success + minimal references, always stripped of local details), persona-driven subagents, prospect-first + Brief as contract for orchestration/research/seq skills, "just go" after upfront validation, support for structured tasks (Mission + Investigate in: + Run if: + Deliver with verdicts). Use when user says "/create-metaskill <name> for <orchestration purpose>", "make a new agnostic meta-skill like research...", etc.
---

# /create-metaskill — Project-Agnostic Meta-Skill Creator

You know how to create skills. This encapsulates the hard-won rules for meta-skills that are truly portable across any repo using the pragmatic system (init/done/seed + handoffs as durable layer).

## Core Principles (Enforce on Every Creation)

- **Project-Agnostic**: The skill you produce must never mention specific projects, paths, tools (e.g. no project-harness-name), features, handoffs by date, or local code. Use only: "your project's harnesses/verifiers (as named in the Brief or task)", "the latest handoff in the durable layer", "a 4-step ordered plan (extract base, update callers, add flow, improve feedback)". Abstract examples only.

- **Token Conservation**: Files lean. No junk. No duplicated persona templates in the skill. No long philosophy sections (SOUL_DRIVER etc. only minimal in References). Prune verbose text into "Core Loop (pruned)". Aim for brevity where possible.

- **Structure of Produced Skill**:
  - Tight frontmatter (name, description with auto-invoke triggers like "/<name>", "make a new meta skill for...").
  - Short intro.
  - ## Usage (copy-paste generic examples).
  - ## Core Loop (numbered, concise).
  - ## Rules (focus on agnosticism, personas, prospect-first, just-go).
  - ## Example (fully generic/abstract).
  - ## Success Criteria.
  - ## References (meta-system only: init/done, handoffs/README, SOUL_DRIVER/DEV_NOTES generically, parallel-implement patterns, create-skill, concise skill style, involved skill style for checklists).

- **Personas**: For any skill that spawns subagents, create/update lean personas (role + process bullets + required output format + guardrails like "NO code changes unless authorized", "follow Brief"). Keep <60 lines. Reference canonical bundled paths.

- **Prompt Construction (for orchestration skills)**: Prospect first (Brief = contract for foundations/testability/"just go"). When spawning: prompt = [full persona] + Brief + task. Encourage tasks framed as **Mission** (with narrative/insights) + **Investigate in:** + **Run [harness] if:** + **Deliver** (with file:line, ranked gaps, per-task verdicts). Instruct to use persona's report format exactly.

- **Orchestration Meta-Skills** (research/prospect/seq-impl): Always prospect-first. Brief is single source of truth. Spawn with persona, wait, synthesize. Only stop on real failure or gates not met. Subagents get full context via Brief + task.

- **Creation Mechanics**:
  1. Parse request for name + purpose.
  2. mkdir -p the target .grok/skills/<name> (project scope by default).
  3. Write SKILL.md via search_replace (old_string empty).
  4. Create personas via same if needed (bundled for system personas).
  5. Verify (cat or wc -l).
  6. Report: usage, line count, confirmation it's agnostic + lean.

## Usage

```bash
/create-metaskill research for orchestrating prospect-first deep research with researcher subagents. Support Mission + Investigate in: + Run harness if: + Deliver with verdicts. Keep fully agnostic and lean.
```

The agent will produce the complete files following every principle.

## Core Creation Steps

1. Parse: skill name (kebab-case), exact purpose (orchestration? research? sequential with upfront prospect?).

2. Decide scope/personas: Default project .grok/skills/. If subagents involved, plan persona(s) too.

3. Design the content in your mind following Principles + Structure above. Draft mentally, then cut bloat.

4. Create dir with run_terminal_command: mkdir -p <absolute project .grok/skills/<name>>

5. Write the SKILL.md (and personas) with search_replace, old_string="".
   - Persona example (lean): role statement, Process: numbered, required ## Report format, Rules/guardrails, "Use tools. Cite. Follow Brief."

6. Verify the written files contain no specific project references.

7. Present to user: the created skill is ready, how to invoke it, that it is project-agnostic and token-efficient.

## Rules

- Every sentence in the target skill must pass the agnostic test before writing.
- Enforce token conservation ruthlessly — the produced skill must be immediately usable with minimal tokens.
- For research-like: the skill + its persona must support detailed but structured input (Mission + user narrative + Investigate targets + verification steps + per-task verdicts).
- Always include "Use todo_write" for multi-step orchestration.
- After creation, the skill must teach future agents the same principles.
- If the request is for a persona only, still produce a minimal SKILL.md wrapper if it makes sense, or just the persona.

## Example (Generic)

User asks for a meta-skill "foo-orchestrator" for running prospect then N subagents with "bar" persona on facets, Brief as contract, synthesize.

You produce:
- Dir
- SKILL.md with Usage, Core Loop (prospect, plan facets, spawn with persona+Brief, wait, synthesize), Rules (prospect first, prepend persona, etc.), generic Example, Success, References to meta only.
- If needed: update/create bar persona with process + output format.

## Success Criteria

- Produced files are lean (compare to concise skills for simple, involved skills with checklists for complex).
- Zero project-specific references anywhere in the created content.
- The skill is immediately actionable for an agent.
- Follows prospect-first + persona patterns where orchestration is involved.
- User can copy the skill to another repo and it works without changes.

## References

- Meta-system: init (read durable layer first), done (handoffs), handoffs/README, SOUL_DRIVER (north star + anti-spiral), DEV_NOTES (lightweight state).
- Patterns: parallel-implement (consolidation, STATUS blocks, lightweight reviewer, persona prepending), prospect/research/sequential-implement (Brief contract, just-go after upfront, Mission/Investigate/Deliver structure support).
- Skill writing: concise skills (purpose + how-to + success), involved skills style (checklists + core loop + rules + example + success + references) but always stripped of local details.
- Creation mechanics: create-skill process (but specialized here for meta/agnostic focus).

Now execute the steps above for the requested meta-skill.
