# Sister suite + Unity map

## Dual full-fidelity weather suite

| Side | Repo | Physics / stack | Role |
|------|------|-----------------|------|
| Atmosphere | **CloudVision** | FV3 / SHiELD (and related) | Full-fidelity atmospheric prediction, production shield path |
| Coastal | **richamp-support-floodwater** (this repo) | **ADCIRC (+ SWAN)** | Full-fidelity surge/waves, RICHAMP postprocess, obs comparison |

Both are real, recognizable research/production pathways. Neither is a toy.

## Two ways to run coastal simulations (Unity)

### A — Manual ADCIRC

1. Assemble a run directory (mesh `fort.14`, control `fort.15`, met, etc.).
2. Launch with **sbatch** (and SWAN coupling when configured).
3. Outputs land in the rundir (often PE* rank dirs + many `*.nc` / fort files).
4. Point **this repo’s postprocess** at that rundir for plots / product / obs.

### B — Floodwater / ASGS / ecflow

1. Orchestration and **Floodwater config** live largely under **home** on Unity (`/home/pranav_sai_uri_edu` — ecflow configs, related projects).
2. ASGS instance + POSTPROCESS hooks; this repo clones beside ASGS output as **richamp-support** (see root `README.md`).
3. Same postprocess philosophy: products + obs, not re-solving the FEM.

## Unity path map (Pranav)

```
/home/pranav_sai_uri_edu
  Floodwater / ecflow configs, miniconda, small projects   (~58G)

/work/pi_iginis_uri_edu/pranav_sai_uri_edu
  Active work, scenario_files (~152G)

/project/pi_iginis_uri_edu/pranav_sai_uri_edu
  Long-term archive (~6.4T raw / 753.96G filtered PE*+*.nc prune, 2026-07-23)
    AdcircManualRuns/     (~4.9T raw / 550.43G filtered)
    ecflow_output/       (~707G raw / 78.75G filtered)
    v18Runs/, workBackup32025/, builds, meshes, postprocess_*, …
  Inventory: notes/WIKI/unity-project-triage-inventory.md
```

## This repo’s job

- **Post-processing home** for RICHAMP / URI coastal products (see `README.md` for ASGS install on Unity/Hatteras).
- **Two main entry points:**
  - `localGenerator.sh` — manual / point-at-a-rundir graphing & products (`generateGraphs.py`, …)
  - `richamp_scale_and_subset*` — Floodwater/ASGS **full** post path (with post_init wind/rain/MetGet)
- **Side tools:** wind converters + field library seeds, run properties, parametric rain, tracks, runup, obs hooks, Matlab inundation — see [what-we-use-and-need.md](what-we-use-and-need.md).
- **Durable brain** for triage of Unity trees (meta-system under `notes/GROK/`).
- **Not** a dump of every PE* and fort.63 — preserve ability to **rebuild and re-postprocess**.

## External archive (Mac)

- Drive: `/Volumes/Pranav's Hard Drive/unity-archive/` (bootstrap surgical pack + optional t1/deliverables tiers)
- Scripts: `notes/GROK/ops/scripts/unity-pull-*.sh` (archive tooling only; day-to-day work is off the volume, not a remote login)
