# Handoff — Seed this sister + continue Unity triage / archive (2026-07-23)

## What this session established

### Sister-suite framing (non-negotiable context)

There is a **dual high-fidelity weather suite**:

| | **CloudVision** | **richamp-support-floodwater** (this repo) |
|--|-----------------|--------------------------------------------|
| Fidelity target | FV3 / SHiELD atmosphere | **ADCIRC (+ SWAN)** coastal |
| Status | Active production-shield work | **Already established** — wake it, don’t reinvent |
| Working tree | `~/projects/CloudVision` | `~/projects/richamp-support-floodwater` |
| Meta-system | notes/GROK seeded earlier | **Seeded this session** |

This is not a random postprocess folder. It is the **coastal peer** of CloudVision. Postprocess + obs live here; multi-year Unity simulation estate lives on Unity under Pranav’s home/work/project.

### What was installed here

```
notes/GROK/
  SOUL_DRIVER.md          # sister suite soul
  DEV_NOTES.md            # current reality + lessons
  README.md               # canonical meta README
  ops/scripts/
    unity-pull-research-archive.sh
    unity-pull-tmux.sh
    unity-pull-status.sh
  handoffs/
    this file
    ARCHIVE/
notes/WIKI/
  INDEX.md
  sister-suite-and-unity-map.md
  project-triage-rubric.md
.grok/skills/
  seed/, init/, done/, handoff/
```

Root **already had** setup pathways:

- `README.md` — full **ASGS → richamp-support postprocess** setup on Hatteras & Unity (MetGet, modules, POSTPROCESS hooks).
- `README.txt` — Deb’s Unity notes: `INP.txt` → rundir, `sbatch runmu` / `runW`, paths under `/work/pi_iginis_uri_edu/djc/...`.

### Unity transfer work (ported from CloudVision session)

**Working source of truth (current):** external drive archive only —  
`"/Volumes/Pranav's Hard Drive/unity-archive/"` (bootstrap surgical + tiers). No remote-login workflow for day-to-day ops.

**External drive:** `/Volumes/Pranav's Hard Drive` (~1.3–1.4 TiB free; quote the apostrophe).

**Live job (as of handoff write):** tmux session `unity-pull`, command `--only home,work`. Home was mid-transfer (~20 G+ on disk, ~2 MB/s, hundreds of thousands of small files). Work not finished. **Leave it running** unless user stops it.

**Sizes (Unity):**

| Tree | Full (approx) | Filtered (no PE*, no *.nc) |
|------|---------------|----------------------------|
| home | 58 G | (pull excludes .cache only) |
| work | 152 G | mostly scenario_files |
| project | 6.4 T | **~754 GiB** |
| └ AdcircManualRuns | 4.9 T | **~550 GiB** |
| └ ScenarioRuns | 4.6 T | ~501 GiB (earlier) |
| └ ecflow_output | 707 G | ~79 GiB |
| └ v18Runs | 363 G | ~28 GiB |
| └ workBackup32025 | 362 G | ~72 GiB |

**Filter policy for any ManualRuns / project bulk archive:**

```text
--exclude 'PE*/' --exclude 'pe*/' --exclude '*.nc'
```

(All netCDF out — including fort.68.nc — per latest user direction. PE* out everywhere under ManualRuns.)

**Do not** parallel-rsync login. **Do not** casually start `--only manual` at 1.5 MB/s without accepting multi-day runtime (~4–6 days for 550–754 G). Prefer **Globus** for bulk; triage gems first.

**Script bugs already fixed (in ops/scripts):**

- bash 3.2 `pipefail` + `rsync --version | head` → exit 141 silent death  
- `--append-verify` incompatible with `--partial-dir` on rsync 3.4  
- macOS TCC / Removable Volumes for external drive  
- Default sources: home+work only; `--only manual` = filtered AdcircManualRuns  

### Two run pathways (for desert-island doc)

1. **Manual ADCIRC** — build rundir, sbatch, optional SWAN; postprocess points at rundir.  
2. **Floodwater / ASGS / ecflow** — configs in **home**; this repo attaches as richamp-support postprocess (`README.md`).

### North star for *next* work (medical triage)

> Categorize and clean `/project/.../pranav_sai_uri_edu`. Figure out what is required for **full replication** of case diversity and both pathways. Save gems (QoL scripts, postprocess, templates, meshes, golden cases, Floodwater config). Discard vestigial multi-TB junk. Prefer **surgical archive** over bulk mirror.

Rubric: `notes/WIKI/project-triage-rubric.md` (P0–P3).

---

## Current state checklist

- [x] Meta-system seeded in this repo  
- [x] Pull scripts + size measurements documented  
- [x] Sister framing written into SOUL_DRIVER  
- [ ] home+work pull completed on external drive  
- [ ] Project triage inventory (keep/golden/discard per top-level dir)  
- [ ] Desert-island replication doc (build ADCIRC, manual vs Floodwater, postprocess)  
- [ ] Decision: Globus vs never pull ManualRuns vs curated gem pack only  
- [ ] Optional: wake Floodwater config path verification on Unity home  

---

## What the next session must do (`/init` here)

1. **Read** `SOUL_DRIVER.md`, `DEV_NOTES.md`, **this handoff**, wiki sister-suite + triage rubric.  
2. **Check pull:**  
   ```bash
   cd ~/projects/richamp-support-floodwater/notes/GROK/ops/scripts
   ./unity-pull-status.sh "/Volumes/Pranav's Hard Drive"
   ```  
3. **If home+work still running** — do not kill; optionally start **triage planning** (docs only) in parallel.  
4. **If home+work done** — do **not** auto-start manual; first produce a **triage table** of project top-level (P0–P3) from archive listings / prune-size tooling on the volume.  
5. **Primary goal:** medical triage + “desert island kit” definition — not finishing a 550 G rsync.  
6. **Secondary:** document Floodwater path using home tree + this repo’s README.  
7. Treat CloudVision as sister: no FV3 work here; coastal full fidelity only.

### Kickoff ManualRuns *only if user explicitly wants multi-day*

```bash
tmux kill-session -t unity-pull   # only if previous job fully finished/idle
cd ~/projects/richamp-support-floodwater/notes/GROK/ops/scripts
./unity-pull-tmux.sh "/Volumes/Pranav's Hard Drive" --only manual
```

---

## Open questions

1. Which **golden storms/cases** define “diversity” for desert-island (1938, Sandy, Henri, Lee, runup, …)?  
2. Is **workBackup32025** redundant after work pull succeeds?  
3. One **canonical ADCIRC build** path among adcirc-cg* / test-build-*?  
4. Globus endpoint availability for Pranav on Unity → external drive?  
5. Where exactly is **Floodwater** install vs config on home (paths for wiki)?  
6. Should gem QoL scripts on project be **copied into this git repo** (not only external drive)?

---

## Success for the next arc

A future human+agent can:

1. Explain the **sister suite** in one breath.  
2. Stand up **manual** and **Floodwater** paths with a written checklist.  
3. Point **this postprocess repo** at a rundir and produce products + obs.  
4. Know which Unity trees are **P0 vs amputate**, without re-du’ing 6 T blindly.  
5. Not waste a week rsyncing PE* and fort.63s at 1.5 MB/s.

---

*Origin: CloudVision session on Unity archive + seed into richamp-support-floodwater. Continue all coastal archive/triage work from **this** repo.*
