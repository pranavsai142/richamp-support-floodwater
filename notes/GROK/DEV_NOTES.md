# DEV_NOTES — richamp-support-floodwater (Narrative State of Play)

**Purpose**: Lightweight living summary. Rich history lives in dated handoffs.

Drivers: this file · `SOUL_DRIVER.md` · latest `notes/GROK/handoffs/*`

## Current Big Picture

**Sister of CloudVision.** There: FV3/SHiELD full fidelity. Here: **ADCIRC (+SWAN) full fidelity** + RICHAMP postprocess (this working tree). Unity holds ~2 years of research under:

| Mount | Path | Role |
|-------|------|------|
| home | `/home/pranav_sai_uri_edu` | Floodwater/ecflow configs, miniconda, projects (~58 G) |
| work | `/work/pi_iginis_uri_edu/pranav_sai_uri_edu` | Active work / scenario_files (~152 G) |
| project | `/project/pi_iginis_uri_edu/pranav_sai_uri_edu` | Long archive (~6.4 T raw) |

**Active Mac pull** (tmux `unity-pull`, external drive `Pranav's Hard Drive`): `--only home,work` via scripts in `notes/GROK/ops/scripts/`. Speed ~1.5–2.2 MB/s single stream. ManualRuns **not** recommended on that path without multi-day commitment or Globus.

**Filtered project size** (exclude all `PE*` dirs + all `*.nc`): **~754 GiB** total; **AdcircManualRuns ~550 GiB**. Fits disk; still multi-day at login rsync rates.

## Hard-Won Lessons

### 1. Filter PE* + *.nc before any ManualRuns archive
- 4.9 T ManualRuns → ~550 GiB filtered; ScenarioRuns alone 4.6 T → ~501 GiB earlier sample.
- Aug*ScratchCopy-scale trees are TB unfiltered; full copy outside ScenarioRuns is not viable on a ~1.5 T free drive.

### 2. Login rsync is single-stream by design
- Parallel rsync to login tanks the node and rarely multiplies throughput.
- Prefer **Globus** for bulk; keep rsync for home/work and small curated packs.

### 3. Two simulation pathways
- **Manual**: create rundir, sbatch ADCIRC (+SWAN as configured).
- **Floodwater / ASGS / ecflow**: orchestration + configs concentrated in **home**; this repo is the **postprocess** attach point (`README.md` ASGS setup).

### 4. Gems vs junk
- Gems: postprocess pointing at rundir, obs hooks, QoL netCDF vets, templates, meshes, builds you still use, Floodwater configs.
- Junk/vestigial: PE* trees, bulk field nc, failed runs, duplicate test-builds, multi-TB ManualRuns noise.

### 5. macOS external drive + TCC
- Paths with spaces/apostrophes must be quoted: `"/Volumes/Pranav's Hard Drive"`.
- Terminal needs Full Disk Access / Removable Volumes or mkdir fails with Operation not permitted.
- bash 3.2 + `pipefail` + `rsync --version | head` → silent exit 141 (fixed in pull script).
- rsync 3.4: never combine `--append-verify` with `--partial-dir`.

## How We Work

- Open this repo and run **`/init`** (reads SOUL + DEV_NOTES + latest handoff).
- **Source of truth for cases/binaries/meshes:** external-drive archive only —  
  `"/Volumes/Pranav's Hard Drive/unity-archive/surgical/"` (bootstrap) and tier packs (`t1`, deliverables) under the same `unity-archive/` tree.  
  **Do not SSH to a cluster for day-to-day work.** Run and postprocess from the volume + this repo.
- Ops/scripts under `notes/GROK/ops/scripts/` are archive tooling (status, surgical packs); they are not a login workflow.
- Sister: CloudVision for atmosphere; do not reinvent FV3 here.

## Next Focus

1. **Mac mini always-on host — KIT STAGED, BOOTSTRAP PENDING** (`2026-07-28-macmini-adcirc-always-on-handoff.md`).  
   Host: `pranavs-mac-mini.tail7f4d6b.ts.net` — **Intel i7-8700B x86_64**, 64 GB, SSD `/Volumes/ssd` (~1.3 TiB free).  
   Kit: `"/Volumes/Pranav's Hard Drive/macmini-adcirc-kit/"` (~1.6 GiB) — ADCIRC **source**, this repo (ops), ricv1/ec95d/v18 seeds, MetGet secret, `scripts/bootstrap-macmini.sh`.  
   **Do not copy arm64 padcirc from M3** — rebuild on mini (`/usr/local` brew). Transfer → bootstrap → ec95d smoke → `ec95d latest gfs`.
2. **richamp-support-web / house viz — ORDER 0–11 DONE** (`2026-07-25-richamp-support-web-orders-complete-handoff.md`). Suite shell + coastal fieldpack + wind bridge shipped.
3. **Parametric Lee dual campaign COMPLETE** + **house integration totality DONE** (`2026-07-28-house-integration-totality-done-handoff.md`). Golden: `?preset=lee-met-family`.
4. **Open gaps** (honest): residual ops beyond sub/abs_sub; residual fieldpack export; atmos `meta.roles`; Lee rain time-axis; wave spatial on older goldens; 2D basemap orientation; mini skill path aliases for kit meshes.
5. Continuous analysis (½ h hotstart chain) after durable fort.68 — **prefer on mini** once green.
6. v18 multi-day when kit/meshes on mini.
7. Runup offline only until later handoff.

---

*Update lightly at session end. Detail goes in handoffs.*
