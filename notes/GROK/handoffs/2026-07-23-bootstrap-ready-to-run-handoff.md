# Handoff — Bootstrap archive ready; how to run arbitrary ADCIRC(+SWAN) (2026-07-23)

## What this session accomplished

1. **Medical triage + research** of Unity project estate (P0–P3 inventory, prune sizes, postprocess entry points).  
2. **Surgical pull strategy** refined: whole ManualRuns soft-exclude **fails** size; tiered allowlists required.  
3. **Bootstrap tier launched and completed** (`exit 0`, ~12 GiB on external drive).  
4. **Run design/runbook** written so the next session can start **manual ADCIRC(+SWAN) runs** from that pack without re-triaging Unity.

## Durable artifacts

| File | Role |
|------|------|
| `notes/GROK/handoffs/2026-07-23-bootstrap-adcirc-run-plan.md` | Plan summary |
| `notes/GROK/handoffs/2026-07-23-bootstrap-adcirc-run-design.md` | **Runbook**: what’s in bootstrap, setup gaps, recipes, checklist |
| `notes/WIKI/adcirc-swan-rerun-kit.md` | Size tables, tiers, file matrices |
| `notes/WIKI/what-we-use-and-need.md` | Pathways A/B, post entry points |
| `notes/WIKI/unity-project-triage-inventory.md` | Full project top-level triage |
| `notes/GROK/ops/scripts/unity-pull-surgical-*.sh` | Surgical pull tools |

## Where the bootstrap lives

```text
/Volumes/Pranav's Hard Drive/unity-archive/surgical/
  home/     ~0.9G   floodwater_files, scripts, confs (partial ecflow from earlier partial pull may exist)
  work/     ~1.4G   scenario_files/wind/
  project/  ~9.9G   binaries, meshes, templates, v18 cases
```

**Finished:** 2026-07-23 ~18:10 local — `ALL REQUESTED PACKS OK (tier=bootstrap)`.

### What’s there (enough to run)

- **Solvers:** `padcirc`, `padcswan`, `adcprep`, `adcirc`, `adcswan`, …  
- **Meshes:** englandv18 (**v18**), ricv1, navd88  
- **Cases:** `v18RunTemplate`, `v18SandyRun`, `DebV18Run` (spinup + forecast dirs; inputs only)  
- **Templates:** Manual / Run / Floodwater  
- **Floodwater YAML** (home + project)  
- **Wind txt seeds** (work)  
- **This git repo** for postprocess (`localGenerator.sh`, `richamp_scale_and_subset*`)

### What’s NOT there (must re-create or pull later)

| Missing | Consequence |
|---------|-------------|
| PE* | Run `adcprep` every time |
| fort.68.nc / field fort.63 / swan_*.63 | Must **re-run** for products; no free post without re-sim |
| fort.221/222 bulk | Use case fort.22 or wind library / MetGet |
| Full ASGS + ecflow server | t1/t2; bootstrap is **manual-first** |
| Final RICHAMP graphs for all scenarios | `--tier deliverables` (~25–30 G smart) |
| Guaranteed module recipe | First smoke on Unity must record `module list` |

## Rough setup to run an arbitrary case

1. **Mount drive** (if Mac) or **rsync surgical → Unity work**.  
2. **Copy** `v18RunTemplate` (or Sandy/Deb) to a new work directory.  
3. **Edit** fort.15 (times), fort.22 (met), weir/tides as needed; keep mesh family consistent (prefer v18).  
4. **Modules + PATH** to bootstrap binaries (match Unity intel/MPI/netcdf).  
5. **analysis:** adcprep → `sbatch run_padc.sh`.  
6. **Copy hotstart** fort.68.nc → forecast; fix IHOT.  
7. **forecast:** adcprep → `sbatch run_pads.sh` (waves) or `run_padc.sh`.  
8. **Post:** this repo → `localGenerator.sh` / graphs pointing at forecast products.

Detail + checklist: **`2026-07-23-bootstrap-adcirc-run-design.md`**.

## Current state checklist

- [x] Bootstrap pull complete (~12 GiB)  
- [x] padcswan present in archive  
- [x] v18 + ricv1 meshes in archive  
- [x] Runbook handoff written  
- [ ] Drive remount + Unity stage of bootstrap  
- [ ] First Unity smoke (adcprep + short padcirc) + **document module loads**  
- [ ] Optional: deliverables tier / t1 scenarios  

## Next session (`/init` then)

1. Read this handoff + design runbook.  
2. Confirm drive mounted / archive intact.  
3. Stage one case + binaries to Unity work.  
4. Smoke spinup on `v18RunTemplate/analysis`.  
5. Only then: arbitrary storm edits or Floodwater path B (may need t1 ecflow_configs).

## Open questions

1. Exact Unity `module load` sequence for these Feb 2025 binaries?  
2. Default PE count / sbatch partition for current account?  
3. Prefer always coldstart full chain vs archiving one fort.68 later?  
4. Pull deliverables next, or re-run + post for products?

---

*Coastal sister of CloudVision. Atmosphere stays in CloudVision; here = ADCIRC(+SWAN) + RICHAMP postprocess.*
