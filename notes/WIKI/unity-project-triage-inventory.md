# Unity project estate — triage inventory (begin)

**Host path:** `/project/pi_iginis_uri_edu/pranav_sai_uri_edu`  
**Live listing + prune sizes:** 2026-07-23 (historical remote listing; working archive is now on volume under `unity-archive/`)  
**Rubric:** [project-triage-rubric.md](project-triage-rubric.md)  
**Map:** [sister-suite-and-unity-map.md](sister-suite-and-unity-map.md)  
**What we use/need (meta search model):** [what-we-use-and-need.md](what-we-use-and-need.md) — two post entry points (`localGenerator.sh`, `richamp_scale_and_subset*`), side-tool families, wind library, re-run kits not bulk ScratchCopy.

## Method (atmospheric-twin prune technique)

Primary size method is **not** bare `du -sh` on multi-TB trees. Use `find` with **`-prune`**:

```bash
# Exclude PE*/pe* processor dirs and all *.nc; sum remaining file bytes → GiB
find TARGET \
  \( -type d \( -name 'PE*' -o -name 'pe*' \) -prune \) -o \
  \( -type f -name '*.nc' -prune \) -o \
  -type f -printf '%s\n' 2>/dev/null \
  | awk '{s+=$1} END{printf "%.2f GiB\n", s/1024/1024/1024}'
```

- **Filtered size** below = that prune sum (2026-07-23 live).
- **Raw** multi-TB figures remain historical ballparks only (handoff); not re-measured with full unfiltered walks.
- **Project filtered total (one whole-tree prune walk):** **753.96 GiB** (matches prior ~754 GiB).

Helper (local ops): `notes/GROK/ops/scripts/unity-prune-filtered-size.sh`.

## Priority legend (from rubric)

| Class | Meaning |
|-------|---------|
| **P0** | Critical for desert-island replication — keep / archive first |
| **P1** | High value, selective |
| **P2** | Keep on NESE only unless Globus / curated pack later |
| **P3** | Amputate / regenerate (or drop duplicates) |
| **needs deeper look** | Top-level class ambiguous; second-level triage next |

## Pathway tags

- **manual** — manual ADCIRC rundirs / templates / ScenarioRuns
- **Floodwater-or-ecflow** — Floodwater YAML, ecflow suite trees, orchestration output
- **build-or-mesh** — ADCIRC/ASGS source trees, fort.14 meshes
- **postprocess-or-QoL** — post tools, node maps, wind products, RICHAMP packs
- **unknown** — not yet classified

## Top-level inventory (complete)

Every name from the live `ls -1` of project root appears once. **42 entries.**

| Name | Type | Filtered GiB | Pathway | Class | One-line rationale (replication, not bulk mirror) |
|------|------|-------------:|---------|-------|---------------------------------------------------|
| `adcirc` | dir | 0.11 | build-or-mesh | **P3** | Older/small source clone; superseded by cg/intel Unity trees for compile path. |
| `adcirc-cg` | dir | 0.76 | build-or-mesh | **P1** | Upstream-style cg tree; keep as reference if intel tree fails to rebuild. |
| `adcirc-cg-custom-intel-unity` | dir | 0.81 | build-or-mesh | **P0** | Unity-tuned ADCIRC build tree (buildinfo present); primary candidate for desert-island compile. |
| `AdcircManualRuns` | dir | **550.43** | manual | **P2** (bulk) + **P0 gems inside** | Bulk = P2/NESE+Globus only; **do not** full rsync. Gems: templates, meshes, README/Scenarios, named golden runs. **Aug29ScratchCopy** = thesis-scale (~156 GiB filtered) — keep re-run inputs only, not full download (user intent). |
| `ArashAdcircCG` | dir | 0.14 | build-or-mesh | **P1** | Collaborator/work tree; selective keep if unique patches, else regenerable. |
| `asgs-test-build` | dir | 0.44 | build-or-mesh | **P3** | Test ASGS build; duplicate of production build path. |
| `ec95d` | dir | 0.65 | Floodwater-or-ecflow | **P1** | Early suite layout (analysis/archive/forecast_ensemble); sample for Floodwater pathway evidence. |
| `ec95d_10212023` | dir | 0.65 | Floodwater-or-ecflow | **P3** | Dated snapshot suite; likely superseded by later ricv1 success trees under ecflow_output. |
| `ec95d_11212023` | dir | 2.66 | Floodwater-or-ecflow | **P3** | Dated suite with nested adcirc; keep only if unique config not in home/floodwater_files. |
| `ec95d_lee_hwc` | dir | 0.56 | Floodwater-or-ecflow | **P1** | Lee HWC case evidence; selective for storm diversity until golden set locked. |
| `ec95d_lee_hwc_veerLeftTrack` | dir | 0.16 | Floodwater-or-ecflow | **P1** | Lee track sensitivity; selective, small. |
| `ecflow_output` | dir | **78.75** | Floodwater-or-ecflow | **P3 for archive / P2 NESE** | **Do not pull.** Regenerable via Floodwater + home/project configs. Leave on Unity/NESE only. |
| `floodwater_files` | dir | 0.55 | Floodwater-or-ecflow | **P0** | Floodwater YAMLs, unity.h/slurm heads, ricv1 configs — replication-critical for pathway B. |
| `GFSForecasts` | dir | 0.18 | manual | **P3** | Mostly `*.nc` (pruned); regenerate from MetGet/GFS when needed. |
| `meshes` | dir | 0.00 | build-or-mesh | **P0** | Mesh provenance dir (`ricv1_floodwater_decomp_mesh`); tiny but pathway-critical naming. |
| `pls` | dir | 0.71 | build-or-mesh | **P1** | Full ADCIRC+SWAN source tree (BUILD.md, swan, sandy_Deb); alternate build source. |
| `Post_Nodes.json` | file | ~0.00 | postprocess-or-QoL | **P0** | Station/node map for postprocess; also mirrored in this git repo. |
| `post_output` | dir | 3.14 | postprocess-or-QoL | **P1** | Delivered post products; keep selective demos/papers, not infinite copies. |
| `postprocess_files` | dir | 0.95 | postprocess-or-QoL | **P1** | Post inputs/helpers; selective attach for richamp-support workflows. |
| `postprocess_output` | dir | 0.00 | postprocess-or-QoL | **P3** | Empty/near-empty output stub. |
| `Post_Station_To_Node_Distances.json` | file | ~0.00 | postprocess-or-QoL | **P0** | Distance map for obs/station post; also local repo copies. |
| `post_temp` | dir | 3.88 | postprocess-or-QoL | **P3** | Temp post workspace; regenerable. |
| `post_temppost_wind_data_file.json` | file | 0.39 | postprocess-or-QoL | **P3** | Scratch wind product (~400 MB); regenerate from post pipeline. |
| `readFortUtil.py` | file | ~0.00 | postprocess-or-QoL | **P0** | QoL fort/netCDF vet — gem to copy into git if not already. |
| `readPostUtil.py` | file | ~0.00 | postprocess-or-QoL | **P0** | QoL post netCDF vet — gem to copy into git if not already. |
| `RICHAMP` | dir | 0.07 | postprocess-or-QoL | **P1** | Core RICHAMP pack; selective. |
| `RICHAMPFilesHenri` | dir | 0.02 | postprocess-or-QoL | **P1** | Henri base files; keep one canonical Henri pack. |
| `RICHAMPFilesHenriAdvisory17_1ft` | dir | 0.00 | postprocess-or-QoL | **P1** | Advisory variant (+1 ft); keep if unique vs 1 m siblings. |
| `RICHAMPFilesHenriAdvisory17_1m` | dir | 0.00 | postprocess-or-QoL | **P1** | Advisory variant; near-dup family — consolidate later. |
| `RICHAMPFilesHenriAdvisory18_1m` | dir | 0.00 | postprocess-or-QoL | **P1** | Advisory 18; selective golden advisory. |
| `RICHAMPFilesHenriAdvisory19_1m` | dir | 0.00 | postprocess-or-QoL | **P1** | Advisory 19; selective golden advisory. |
| `RICHAMPHenriAdvisory18-June23` | dir | 0.00 | postprocess-or-QoL | **P1** | Dated Advisory18 snapshot; may supersede or duplicate `…18_1m`. |
| `Ricv1Meshes` | dir | 0.30 | build-or-mesh | **P0** | ricv1 fort.14/13/15 + configs (sea_level / barrier_closed) — mesh gem. |
| `ricv1_preprocesssuccess` | dir | 0.13 | Floodwater-or-ecflow | **P1** | Successful preprocess artifact; selective reference. |
| `scenario_files` | dir | 4.89 | manual | **P1** | **Wind-library seed** (fort.22, wnd, owi scripts); many `*.nc` pruned — non-nc winds are high-value for a curated field library. |
| `test-build-2` | dir | 0.71 | build-or-mesh | **P3** | Duplicate test build; amputate after one compile path proven. |
| `test-build-3` | dir | 0.71 | build-or-mesh | **P3** | Duplicate test build. |
| `test-build-5` | dir | 0.71 | build-or-mesh | **P3** | Duplicate test build. |
| `test-build-asgs` | dir | 0.71 | build-or-mesh | **P3** | Duplicate ASGS test build. |
| `v18Runs` | dir | **27.54** | manual | **P2** | 1938 v18 runs bulk; NESE keep; optional surgical 1938 golden later. |
| `work` | dir | 0.00 | unknown | **P3** | Empty stub (`odir4` only); ignore. |
| `workBackup32025` | dir | **72.22** | Floodwater-or-ecflow | **P2** | Mar-2025 backup of work/ASGS/ecflow; redundant if home+work pull + live trees healthy — NESE only. |

### Spot-check vs prior ballparks (handoff / rubric 2026-07-23)

| Tree | Prior filtered | Live prune (this session) | Δ |
|------|---------------:|--------------------------:|---|
| AdcircManualRuns | ~550 GiB | 550.43 GiB | match |
| ecflow_output | ~79 GiB | 78.75 GiB | match |
| workBackup32025 | ~72 GiB | 72.22 GiB | match |
| v18Runs | ~28 GiB | 27.54 GiB | match |
| **project total** | **~754 GiB** | **753.96 GiB** | match |

## Second-level notes (only where top-level class needs structure)

### `AdcircManualRuns/` (P2 bulk; P0/P1 gems)

| Child | Role | Suggested class |
|-------|------|-----------------|
| `ManualRunTemplate`, `RunTemplate`, `FloodwaterRunTemplate` | Pathway A/B rundir skeletons | **P0** |
| `meshes/` (`ricv1`, `navd88`, `englandv18`) | Mesh copies for manual runs | **P0** |
| `README.txt`, `Scenarios.txt` | How-to + scenario index (Deb → Greg/Pranav) | **P0** |
| `ScenarioRuns/` (1938*, Sandy*, Ram*, Debby*, v18*, *Template*, ScratchCopy) | Case diversity bulk | **P2** bulk; **P1** after golden shortlist |
| `1938_*`, `SandyManualRun`, `Ram*`, `DebRICV1Sample` | Named historical manuals | **P1** candidates for golden set |
| `Aug29ScratchCopy` (thesis runup tree: Dec2022/23, Erin, temps; ~156 GiB filtered) | Significant work | **P0 re-run kit** + **P3 bulk products** — do not full-download; extract inputs/scripts per golden case |
| empty `Scenario5/7`, junk fort.22 at top | Scratch / incomplete | **P3** |
| Top-level `fort.68.nc` | Hotstart product | **P3** under filter policy (all `*.nc` out of archive) |

**ScenarioRuns names (2026-07-23):**  
`1938ClosedManualRun`, `1938ManualRun`, `ClosedBarrierRunTemplate`, `DebV18Run`, `FloodwaterRunTemplate`, `May5ScratchCopy`, `Nov18ScratchCopy`, `ParametricDebbyManualRun`, `RamClosedManualRun`, `RamManualRun6`, `SandyClosedManualRun`, `SandyManualRun`, `SeaLevelRunTemplate`, `v18RunTemplate`, `v18SandyRun`.

### `ecflow_output/` (P2)

- ~35 suite dirs; mix of `ricv1_*Success*`, `ricv1_LeeTotalSuccess`, Lee/Debby, and many `tra*` / `trash*` failures.
- **Surgical gem later:** list SUCCESS-named suites only; do not pack trash trees.

### `floodwater_files/` (P0)

- `ricv1.yaml`, `ricv1_postprocess*.yaml`, `ricv1_sea_level*`, `ec95d.yaml`, `unity.yaml`, `unity.h`, `slurm_head_unity.h`, `credentials.yaml` (secrets — do not git-commit).
- Complements **home** Floodwater/ecflow configs for pathway B.

### Build forest (one survivor)

Prefer **`adcirc-cg-custom-intel-unity`** as P0 compile path; keep **`adcirc-cg`** or **`pls`** as P1 backup; mark all `test-build-*` + `asgs-test-build` **P3** once rebuild is verified.

## Explicit non-actions (this phase)

- **Do not** start `--only manual` / full AdcircManualRuns rsync at login-node rates.
- **Do not** parallel-rsync the Unity login node.
- **Do not** delete anything on Unity from this inventory alone (classification only).

## Next actions (triage / surgical / Globus only)

1. **Triage deeper:** golden shortlist (1938, Sandy, Ram, Debby, Henri, thesis Dec2022/23/Erin) — re-run kits, not full leaf PE*.
2. **Surgical gem packs** (see [what-we-use-and-need.md](what-we-use-and-need.md)): orchestration (Floodwater/ASGS home), binaries+one build, meshes+templates, **wind library v0**, thesis re-run kits, Unity-richamp delta vs git.
3. **ecflow_output surgical:** SUCCESS suite names only; same prune method.
4. **Globus later:** only if P2 bulk must leave NESE.
5. **Home+work full rsync:** optional insurance — **not required** if gems land; cancel OK if stuck on miniconda/Desktop; prefer surgical follow-up.
6. **Build proof:** rebuild once from custom-intel-unity before dropping test-build clones.
7. **Map side tools** as found (wind/rain/track/runup/obs/Matlab/FUNWAVE) into the what-we-use doc — expect more than the initial list.

## Class rollup (top-level)

| Class | Count (approx) | Dominant mass |
|-------|---------------:|---------------|
| P0 | 8 rows | tiny filtered (configs, meshes, QoL) |
| P1 | 18 rows | ~15 GiB class (scenario_files, posts, ec95d*, RICHAMP*, builds) |
| P2 | 4 rows | **~729 GiB** (ManualRuns + ecflow + workBackup + v18) |
| P3 | 12 rows | duplicates, temps, empty, regenerable nc-heavy |

---

*Begin inventory only — not full golden-case leaf catalog. Update when second-level triage or home pull changes class of a row.*
