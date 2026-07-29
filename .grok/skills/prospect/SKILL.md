---
name: prospect
description: >
  Runs the official prospector persona to ask the hard questions, sharpen a research topic or upcoming implementation plan, identify exactly what foundational knowledge must already be present and verifiable, define per-slice testability, and produce a crisp "Prospect Brief" (the map + what the gold looks like). This is the prerequisite that makes /research deliver exact context and /sequential-implement "just go" (stops only on real failure or gates). Project-agnostic meta skill (drop the prospector persona + this skill into any repo). Use when the user says "/prospect <topic or plan>", "prospect this research area first", "help me sharpen what the researcher needs", "before I sequential-implement this, prospect the foundations and test gates", "ask the hard questions on ...", etc. The output (Prospect Brief) is designed to be injected into researcher or sequential-implement runs.
---

# /prospect

**The hard-questions + foundation-mapping step that makes /research deliver exact context and /sequential-implement "just go" (stops only on real failure or gates).**

## Usage

```bash
/prospect <topic or plan>
```

## Core Loop

1. Read indication + context.
2. Load prospector persona from canonical path. Spawn 1 subagent with persona + request to produce Brief.
3. Wait, extract Brief (contract).
4. Present Brief. Offer to feed to /research or /sequential-implement.

Use todo_write.

Persona path (canonical):
- prospector: `/Users/pranav/.grok/bundled/skills/shared/personas/prospector.md`

## Rules

- The persona defines the Brief format and process – follow it (do not duplicate template here).
- Brief is the contract for downstream (research/sequential).
- Use todo_write.

Now execute.
