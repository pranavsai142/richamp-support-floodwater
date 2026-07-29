---
name: fabel-open-ended
description: >
  Activate Fabel-style handling for open-ended tasks: when a task references analog or external systems (e.g. KSP-like environments, prebuilt sim flows), the agent must first internalize the source brief, then use list_dir + grep + read_file to locate first-party captures of the analog system, produce an explicit categorization/index of the referenced elements via todo_write, leverage background agents for parallel exploration of the current project and the analog, synthesize a map, before any code audit of implementation files or edits. The required trajectory is broad doc discovery on analogs → categorize/index → narrow code reads → plan. Use when user says "/fabel for <open-ended task>", "use Fabel open-ended workflow", etc.
---

# /fabel-open-ended — Fabel-Style Open-Ended Task Research Meta-Skill

Encapsulates the successful workflow for open-ended tasks involving external or analog systems. Extracted from demonstrated successful trajectories: always start with source doc understanding and first-party analog research before implementation.

## Usage

```bash
/fabel for totally externalizing the Environment tab... (full brief describing the task and referencing analog like KSPOS)
```

The agent will prepend the open-ended protocol and follow the core loop below.

## Core Loop

1. **Internalize source**: Fully read and internalize the user's provided task description / brief (the source doc).

2. **Broad discovery on analog**: Use list_dir + grep + read_file to locate and explore first-party captures and documentation of the referenced analog or external system.

3. **Categorize and index**: Produce an explicit categorization/index of the referenced elements (e.g. environments/planets + params, body state/fields, loop steps, observability/debug surfaces, UI contracts, core invariants). Record via internal todo_write. Map "planned vs current" against the index.

4. **Parallel exploration**: Launch background agents or parallel tool calls to explore the current project's architecture and the analog simultaneously.

5. **Synthesize map**: From the reports and index, create a critical synthesis: what to port, what not, bugs in prior attempts, simplifications.

6. **Plan and execute**: Break into ordered phases. Reference the index throughout. Only then audit code or make edits.

## Rules

- Always start with the source brief and analog first-party research (list_dir/grep/read) before touching implementation files.
- Use todo_write to record the categorized index of elements.
- Use background/parallel exploration for current project and analog.
- Synthesize map and identify gaps before code changes.
- Follow the trajectory: broad doc discovery on analogs → categorize/index → narrow → plan.
- The protocol is mandatory for tasks referencing analog/external systems.
- Produce lean, verifiable output with references to the index.

## Example (Generic)

User provides brief for an open-ended task referencing an external "BarOS" system with specific elements (e.g. debug surfaces, env params, UI sidebars).

Agent:
- Internalizes the brief.
- list_dir/grep/read on first-party BarOS docs/captures.
- todo_write: categorized index (debug fields with sparklines, envs, forces, UI contracts...).
- Launches background agents for current project architecture and BarOS.
- Synthesizes: "complete map, prior bugs were X, simplification Y".
- Then plans phases and implements following the index.

## Success Criteria

- Agent performs analog research and categorization/index via todo before any code audit or edits.
- Explicit use of trajectory (broad → categorize → narrow → plan).
- Index is referenced in planning and synthesis.
- High-quality output matching demonstrated successful trajectories (detailed map, bug identification, scope understanding).

## References

- Meta-system: init (read durable layer), done (handoffs), handoffs/README, SOUL_DRIVER/DEV_NOTES (generically).
- Patterns: parallel-implement (background agents for exploration), prospect/research (first-party, Brief as contract).
- Skill style: involved skills with core loop + rules + example + success.
