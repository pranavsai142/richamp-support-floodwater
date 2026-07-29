# Project directory medical triage rubric

Goal: **desert-island replication** of case diversity and both run pathways, without keeping multi-TB junk.

## Priority classes

### P0 — Critical for replication (keep / archive first)

- Floodwater / ASGS / ecflow **configs and scripts** (mostly **home**)
- **This postprocess repo** (already local) + any Unity-only forks of post tools
- QoL utilities on project (e.g. `readPostUtil.py`, postprocess drivers that take a rundir)
- **Meshes** and mesh provenance (`meshes`, `Ricv1Meshes`, known good fort.14 sources)
- **Templates** for manual runs (RunTemplate, ManualRunTemplate, FloodwaterRunTemplate) if still used
- **Builds you can still compile from** (one adcirc-cg / intel-unity tree, not five duplicates)
- Documented **golden cases** (small set of storms/advisories that define capability)

### P1 — High value, selective

- `scenario_files` / work scenario packs used for real studies
- One or two **complete** manual run trees **after** PE* + bulk nc strip (inputs + key logs + fort.68-class products if ever re-included)
- `postprocess_files`, useful `post_output` for papers/demos
- RICHAMP advisory packs that are **unique** (not five near-duplicates)

### P2 — Keep on NESE only unless Globus

- Full `AdcircManualRuns/ScenarioRuns` even filtered (~550 G)
- `ecflow_output`, `v18Runs`, `workBackup32025` filtered bulk

### P3 — Amputate / regenerate

- All `PE*` / `pe*` directories
- Bulk `*.nc` field output (re-runnable or regenerable)
- Empty / zero-byte trees, obvious failed runs, duplicate `test-build-*` clones
- Caches, `__pycache__`, junk logs

## Questions for each top-level folder

1. Can we rebuild this from P0 inputs in &lt;1 day of human time?
2. Does postprocess **need** this artifact, or only the rundir path convention?
3. Is there a **newer** sibling that supersedes it?
4. Is it **Floodwater path** or **manual path** evidence?

## Filtered size reference (2026-07-23, historical remote listing)

Exclude: `PE*` dirs + all `*.nc` via `find -prune` (see inventory Method section).

| Path | Filtered (live prune) |
|------|----------|
| AdcircManualRuns | **550.43 GiB** |
| ecflow_output | **78.75 GiB** |
| workBackup32025 | **72.22 GiB** |
| v18Runs | **27.54 GiB** |
| **project total** | **753.96 GiB** |

Full top-level table + classes: [unity-project-triage-inventory.md](unity-project-triage-inventory.md).

## Desired end state

A written **replication kit**:

- How to build ADCIRC(+SWAN) on Unity  
- How to run **manual** vs **Floodwater**  
- How to attach **this repo** for postprocess + obs  
- Inventory of golden cases + where they live (local archive vs NESE)
