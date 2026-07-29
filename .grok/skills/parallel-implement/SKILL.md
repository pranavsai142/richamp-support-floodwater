---
name: parallel-implement
description: >
  Spawn 1-5 subagents (one per task) that each independently run the full /implement review-fix loop on a bug fix, improvement, feature, or arbitrary coding task from a provided list. If more than 5 tasks, intelligently consolidate/group into ≤5 coherent bundles first. After all implementers finish, spawn one lightweight reviewer subagent (using the official reviewer persona) that performs a final high-level completion verification across the whole batch and reports per-task status (done / partial / not done). Launch in parallel, wait for everything, collect status, and output a consolidated report with both implementer claims and independent reviewer verdicts. Use when the user provides a list of issues/bugs/fixes/improvements/tasks and says "parallel implement", "batch these with /implement", "run these tasks in parallel via implement loops", "distribute these 7 fixes", or "/parallel-implement".
---

# /parallel-implement — Parallel /implement Executor

You are a batch orchestrator. The user has given you a list of tasks (bug fixes, improvements, features, refactors, or arbitrary work items). Your job is to:

1. Parse the list.
2. Consolidate to **at most 5** tasks if needed.
3. For each resulting task, spawn **one dedicated general-purpose subagent** whose sole mission is to run the **full `/implement` loop** (implement → review → fix until 0 issues) for **exactly that one task**.
4. Launch all implementer subagents in true parallel.
5. Wait for every implementer to complete and collect their raw STATUS claims.
6. Spawn **one additional lightweight reviewer subagent** (using the official `reviewer` persona exactly as the /implement skill does) that performs a final high-level completion verification across the entire batch.
7. Produce a consolidated report that includes both the implementers' self-reported status and the independent lightweight reviewer's verdicts (done / partial / not done) for each task.

You **coordinate only**. You never perform the implementation work yourself.

## Step 0: Setup & Todo Tracking

- Create a todo list immediately with `todo_write`:
  - id: `parse`, content: "Parse and normalize the list of tasks from the user message / history"
  - id: `consolidate`, content: "If >5 tasks, intelligently group into ≤5 coherent bundles"
  - id: `launch`, content: "Spawn up to 5 subagents (each running a full /implement loop)"
  - id: `wait`, content: "Wait for all implementer subagents to finish and collect their STATUS blocks"
  - id: `lightweight-review`, content: "Spawn one reviewer-persona subagent for final batch-wide completion verification"
  - id: `report`, content: "Build and present consolidated status report (implementer claims + reviewer verdicts)"

- Mark the first one in_progress and keep the todo list updated after every major phase.

## Step 1: Parse the Task List

Read the current user question and recent conversation history.

Accept any of these formats (and mixtures):
- Numbered list: `1. Fix the login redirect bug 2. Add rate limiting to /vote`
- Bulleted list (`- ` or `* `)
- "Task A: ... Task B: ..."
- Comma or newline separated items
- "Here are the issues I want done in parallel: ..."
- Reference to a file (e.g. "the tasks in NOTES.md") — read the file if mentioned.

Normalize into a clean array of task strings. Each task should be a self-contained, actionable description (include any file hints, acceptance criteria, or links the user provided).

If the user also supplied `--effort N` (1-5), capture it. Default effort = 1 for child /implement runs.

## Step 2: Consolidate to ≤5 (if necessary)

If you have **6 or more** tasks:

- Group them intelligently into 4–5 coherent bundles.
- Related work goes together (example: all three auth bugs → one "Hardening auth & session handling" bundle; unrelated UI tweaks → another bundle).
- Each bundle becomes **one** task description that a single /implement subagent can handle (still specific, not vague).
- Tell the user exactly what grouping you chose and why (one sentence per group).

Example output to user:
> Consolidated 8 raw items into 5 bundles:
> 1. Auth & session hardening (3 original bugs)
> 2. Voting flow reliability fixes (2 items)
> ...

If ≤5, use the list as-is.

Never create more than 5 subagents.

## Step 3: Build the Child Prompt for Each Subagent

For every (consolidated) task, construct a prompt with this exact structure:

```
You are now running the /implement skill as an autonomous subagent.

The single task you must complete is:

<the exact task description here>

User also provided this extra context (if any): <relevant snippets from conversation>

Instructions:
- Execute the full /implement loop for the task above (exactly as if the user had typed `/implement [--effort N] <task>` in the main chat).
- Use effort level <N> (default 1).
- Spawn your own implementer subagent (with the implementer persona) and the appropriate number of reviewers.
- Run the complete implement → review → fix → re-review cycle until every reviewer reports 0 open issues.
- When the loop finishes with success (0 issues), print the following machine-readable block as the very last thing in your final message:

**STATUS: SUCCESS**
**Task**: <one-line summary of the task you were given>
**Rounds**: <number of review-fix iterations>
**Files changed**: <comma-separated list or "none">
**Key decisions**: <one sentence>
**Notes**: <anything the user should know>

If you cannot complete the task or the loop ends in an unrecoverable state, print instead:

**STATUS: FAILURE**
**Task**: ...
**Reason**: <short technical reason>
**Partial progress**: <what you did manage to do>

Do not ask the original user for clarification unless you are genuinely blocked on an ambiguous requirement that is not in the task description. When in doubt, make a reasonable choice and document it in the status block.

Begin immediately by treating this as a /implement invocation for the task above.
```

Store the constructed prompt for each task.

Also prepare a short `description` for the spawn call (e.g. "Implement bundle 2: Auth hardening").

## Step 4: Launch All Subagents in Parallel

In a **single response**, emit multiple `spawn_subagent` tool calls (one per task, max 5).

Parameters for each:

- `subagent_type`: `"general-purpose"`
- `prompt`: the full child prompt you built in Step 3
- `description`: short label like `"Task 1/3: Voting fixes"`
- `background`: `true`
- `isolation`: `"none"` (default — all subagents share the live workspace).  
  **Important note for the user (print once):** If any tasks might edit the same files, the subagents may race. In that case the user should re-run with non-overlapping groups. (We can add worktree isolation + merge in a future version if requested.)

Capture every returned `subagent_id` (and any task_id the system gives you) and store them in your todo state.

Announce to the user:

> Launched N parallel subagents. Each is now running its own full /implement loop.
> Waiting for completion...

Mark the `launch` todo complete and the `wait` todo in_progress.

## Step 5: Wait for Completion and Collect Results

Use the waiting tools to block until all subagents finish:

- Prefer `wait_commands_or_subagents` with `mode: "wait_all"` when you have the list of task_ids.
- Or call `get_command_or_subagent_output` (with `block: true`) for each one in parallel where supported.

You may poll in a small loop (sleep 2–4s between checks) if the strict wait tool is not available for your exact ids.

For every subagent that finishes:

- Read its final output (the full transcript tail or the complete last message).
- Look for the **STATUS:** block you instructed it to emit.
- If the block is missing, fall back to the last 15–20 lines and infer success/failure + summary.

Record for each:
- original task / bundle description
- STATUS (SUCCESS / FAILURE)
- rounds
- files changed
- subagent_id (for debugging / resume if needed later)
- raw final message excerpt (if interesting)

If any subagent errors on launch or during wait, record it as FAILURE with the error and continue — do not abort the whole batch.

## Step 6: Lightweight Batch Reviewer (Final Verification)

After the implementer subagents have all finished and you have their raw **STATUS** blocks + summaries (from Step 5), run an independent lightweight reviewer that uses the official reviewer persona.

### 6.1 Load the Reviewer Persona

The reviewer persona lives at the same location used by the real `/implement` skill:

```
/Users/pranav/.grok/bundled/skills/shared/personas/reviewer.md
```

Use `read_file` to load its full contents into `reviewer_persona_instructions`.

### 6.2 Build the Lightweight Reviewer Prompt

Construct a single prompt for one new `general-purpose` subagent:

```
<reviewer_persona_instructions>

---

You are acting as a **lightweight batch completion reviewer** for a set of parallel implementation tasks.

The user originally asked for the following tasks (or bundles):

<list the original parsed + consolidated tasks here, numbered>

The implementer subagents have just finished. Below are the **STATUS blocks** and summaries they produced for each task:

<for each task paste the exact **STATUS: ...** block + files changed + key decisions + any notes the implementer emitted>

Your job is **not** to perform a full deep code review or write a classic /tmp/grok-review-*.md file with dozens of bugs/suggestions/nits.

Instead, perform a **lightweight, high-level completion verification**:

For each task / bundle, answer clearly:
- Was the requested work actually delivered?
- Does the delivered work appear to address the original request at a practical level?
- Are there any obvious gaps, missing pieces, or things that were claimed but not really done?
- Overall verdict for this task: **VERIFIED COMPLETE**, **PARTIALLY COMPLETE**, or **NOT COMPLETE** (or **NEEDS FOLLOW-UP**).

Be concise but specific. You may run `git diff`, `git status`, or read a few key files the implementers mentioned to form your opinion. You are allowed to be opinionated about whether the spirit of the request was fulfilled.

Output format (use this exact structure):

## BATCH VERIFICATION — LIGHTWEIGHT REVIEWER

**Overall batch health**: (one sentence summary)

### Task 1: <short title>
**Verdict**: VERIFIED COMPLETE / PARTIALLY COMPLETE / NOT COMPLETE
**Justification**: (2-4 sentences. Be specific about what you checked and what you found. Cite files or STATUS claims.)
**Missing or weak areas** (if any): (bullet list or "none")

### Task 2: ...
...

### Task N: ...

**Recommendation for the user**:
- Any tasks that need immediate follow-up work?
- Any systemic issues across the batch (e.g. "three different tasks touched auth without coordinating")?

When you are finished, simply output the report above. Do not spawn further implementers or reviewers unless a task is so broken that you cannot even evaluate it.
```

### 6.3 Launch and Wait for the Lightweight Reviewer

- Spawn **one** `general-purpose` subagent (you can do this with `background: false` or `true` + wait — either is fine since it's the final step).
- `description`: "Lightweight batch reviewer (reviewer persona)"
- Pass the full prompt you constructed (persona prepended + verification instructions).
- Wait for it to complete using `get_command_or_subagent_output(..., block: true)`.
- Capture its output. This is the authoritative independent view of whether the batch actually delivered what was asked.

Mark the `lightweight-review` todo complete.

Print a short message to the user:
> Lightweight reviewer (using the official reviewer persona) has finished its batch verification.

## Step 7: Final Consolidated Report

After the lightweight reviewer has reported, update your todo and produce the final user-facing report that combines the implementers' self-reported status with the independent reviewer's verdicts:

```markdown
## /parallel-implement — Batch Complete

**Tasks processed**: 5 (2 raw items were consolidated into bundle #3)
**Effort per child**: 1
**Lightweight reviewer**: used official `reviewer` persona for final verification

| # | Task / Bundle                          | Implementer | Rounds | Reviewer Verdict          | Files Changed                 |
|---|----------------------------------------|-------------|--------|---------------------------|-------------------------------|
| 1 | Fix login redirect after OAuth         | SUCCESS     | 2      | VERIFIED COMPLETE         | LoginPage.py, auth utils      |
| 2 | Add rate limiting to vote endpoint     | SUCCESS     | 1      | VERIFIED COMPLETE         | VotePage.py                   |
| 3 | Auth hardening bundle (3 bugs)         | SUCCESS     | 3      | PARTIALLY COMPLETE        | User.py, Session.py, 2 others |
| 4 | Improve error messages on draft save   | FAILURE     | 1      | NOT COMPLETE              | (partial) DraftPage.py        |
| 5 | Refactor Plotter to use new data model | SUCCESS     | 2      | VERIFIED COMPLETE         | Plotter.py, PlotterApp.py     |

### Lightweight Reviewer Summary
- Task 3: Rate limiting was added but the new headers are not being returned on the /vote path (see the reviewer's justification).
- Task 4: The implementer hit an early blocker and only made partial progress.

### Raw Implementer STATUS blocks
(collapsed for brevity — the full blocks from each subagent are available in the transcript)

All changes from successful tasks are already in the workspace.
```

End with something like:
> Batch finished. The lightweight reviewer (reviewer persona) has provided independent verdicts above.
> Any follow-up work on the PARTIALLY COMPLETE or NOT COMPLETE items, or shall we review the changes that landed?

Mark the final `report` todo complete.

## Rules & Edge Cases

- **Never >5 subagents** — consolidation is mandatory above that number.
- **Child subagents run real /implement** — they will themselves spawn implementer + reviewer sub-sub-agents. This is intended and supported.
- **Status block is sacred** — instruct children clearly and parse it reliably.
- **Shared workspace** — assume tasks are independent. If two subagents edit the same line simultaneously you may get a race; the user can split the list to avoid it.
- **Memory & personas** — each child /implement run will correctly load the workspace memory file and the persona files from the bundled implement skill. The final lightweight reviewer is also given the official `reviewer` persona (prepended exactly like the real /implement skill does for its reviewers).
- **Resuming a child** — if a subagent dies mid-loop you can later resume it manually using its subagent_id and the `resume_from` parameter on a new spawn if the system still holds its state.
- **Keep the user informed** — after launch, after every major completion, and at the very end. Use short progress lines.
- **Use todo_write aggressively** — this is a multi-subagent orchestration; the todo list is your source of truth for the user.
- **Lightweight reviewer is final and independent** — it runs once after all implementers, uses the real reviewer persona, and gives high-level "was the task actually done?" verdicts. It does **not** trigger another full implement-review-fix loop (unless it explicitly recommends one). It is allowed to look at git diffs and source files to form an opinion. Its verdicts are shown alongside the implementers' self-reported STATUS in the final table.

## Example Invocation

User: "Parallel implement these three things:

1. Fix the bug where submitting an amendment doesn't clear the draft
2. Add a confirmation dialog before deleting a policy
3. Improve the loading state on the election monitor page"

You will:
- Parse → 3 tasks
- Launch 3 implementer subagents (each runs a full /implement loop)
- Wait for them, then spawn **one lightweight reviewer** subagent (reviewer persona prepended)
- The reviewer gives independent VERIFIED COMPLETE / PARTIALLY COMPLETE / NOT COMPLETE verdicts for the batch
- Return a table combining both the implementer claims and the reviewer's final verification

This skill turns a flat list of work into a true parallel implementation swarm, each member running the full rigorous implement-review-fix process, followed by one independent lightweight reviewer (using the official reviewer persona) that verifies whether the requested work was actually delivered.

Now execute the steps above.
