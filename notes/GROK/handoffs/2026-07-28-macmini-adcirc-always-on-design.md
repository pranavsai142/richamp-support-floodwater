# Design — Mac mini always-on ADCIRC host + transfer kit

**Plan:** `2026-07-28-macmini-adcirc-always-on-plan.md`  
**Kit root:** `/Volumes/Pranav's Hard Drive/macmini-adcirc-kit/`  
**SSH:** `pranavs-mac-mini.tail7f4d6b.ts.net`

---

## 1. Technical requirements

### TR-1 Machine identity
- Host must be treated as **x86_64 Intel macOS 15**, not a clone of the M3 laptop.
- All native binaries (padcirc, adcprep, padcswan, tide_fac, gfortran-linked tools) **build on the mini**.
- Homebrew install prefix: **`/usr/local`** (Intel). Skill text that hardcodes `/opt/homebrew` must be overridden via `adcirc-env.sh` / operator note until skill is path-agnostic.

### TR-2 Storage contract
| Path | Role |
|------|------|
| `/Volumes/ssd/projects/` | Code, build, kit mirror, `adcirc-local-smoke` |
| `~/projects` | Symlink → SSD projects (already) |
| System Data (~12 GiB free) | OS only — **gate fail** if work_root would land here |

### TR-3 Transfer pack contents (minimum runnable set)

| Component | Why |
|-----------|-----|
| ADCIRC **source** + `thirdparty/swan` | Rebuild padcirc + padcswan |
| `richamp-support-floodwater` (ops core) | `/run-adcirc` skill, post, MetGet glue, tide_fac.f |
| ricv1 linked_files | Preferred skill mesh |
| ec95d fort.13/14 + smoke fort.15 | Fast pipeline smoke |
| v18RunTemplate inputs | Full NE mesh family |
| `setApiKey.sh` | MetGet auth |
| `bootstrap-macmini.sh` | One-shot toolchain + build |

**Excluded:** arm64 binaries, PE*, field nc, thesis ASSET, full surgical (optional later).

### TR-4 Bootstrap sequence
1. Install Homebrew if missing.  
2. `brew install cmake gcc open-mpi hdf5 netcdf netcdf-fortran python@3.13 pipenv`.  
3. `cmake` ADCIRC with `BUILD_PADCIRC`, `BUILD_ADCPREP`, `BUILD_PADCSWAN`, netCDF ON.  
4. Build targets `adcprep padcirc padcswan`.  
5. Gate: `file padcirc` contains **x86_64**.  
6. `pipenv install` (+ `metget`, `haversine`).  
7. `gfortran -O2 -o tide_fac tide_fac.f`.  
8. Write `adcirc-env.sh` with correct `DYLD_LIBRARY_PATH` for brew prefix.

### TR-5 `/run-adcirc` path mapping on mini

| Concern | Laptop | Mini |
|---------|--------|------|
| Solver | `~/projects/adcirc/build` | same (after build) |
| DYLD | `/opt/homebrew/opt/...` | `/usr/local/opt/...` |
| ricv1 stage | surgical home floodwater linked_files | `$MACMINI_ADCIRC_KIT/meshes/ricv1_noriv_nopump/linked_files/` |
| v18 stage | surgical ScenarioRuns/v18RunTemplate | `$MACMINI_ADCIRC_KIT/templates/v18RunTemplate/` |
| ec95d stage | `~/projects/adcirc-local-smoke/ec95d_run` | kit `smoke-seeds/ec95d_run` or copy to work |
| work_root | external Hard Drive or ~/projects | **`$SSD/adcirc-local-smoke`** preferred |
| MetGet | `source ~/projects/setApiKey.sh` | same path on SSD projects |
| np | min(8,ncpu) | min(8–10, 12) fine |

### TR-6 Parallelism / always-on
- Analysis (NWS=0) may run while MetGet builds (unchanged skill law).  
- Prefer continuous analysis hotstart chain once first multi-day fort.68 exists.  
- Mini 64 GB RAM supports ricv1 np=8 without the memory fear of a 16 GB laptop.

### TR-7 Parametric (deferred install)
- `windgfdl` in repo is **Linux x86-64 ELF** — still not a Mac binary.  
- Docker Desktop (or colima) is a **separate** install after GFS path is green.  
- Do not block GFS `/run-adcirc` on Docker.

---

## 2. User stories

### US-1 Transfer kit
**As** the operator, **I can** copy `macmini-adcirc-kit` to the mini SSD in one rsync/USB step, **so that** no cluster SSH is required for day-to-day coastal runs.

**AC:**
- Kit ≤ ~2 GiB, all MANIFEST critical files `OK`.  
- No arm64 `padcirc` inside kit.

### US-2 Bootstrap
**As** the operator, **I can** run `bootstrap-macmini.sh` once, **so that** padcirc/adcprep/padcswan and post env exist.

**AC:**
- `file padcirc` → Mach-O x86_64.  
- `mpirun -np 2` short run can be staged from smoke-seeds.  
- `pipenv run python -c "import netCDF4"` succeeds.

### US-3 Skill parity
**As** an agent on the mini, **I can** execute `/run-adcirc ec95d latest gfs` using the same S0–S9 order, **so that** overnight runs do not need the laptop open.

**AC:**
- Mesh cards resolve via kit paths when surgical path absent.  
- MetGet key sources.  
- Post PNGs land under case `post_*/graphs/`.

### US-4 Always-on analysis
**As** the operator, **I can** leave a durable analysis rundir with fort.68 and attach forecasts, **so that** multi-day coldstarts are rare.

**AC:** Documented in handoff next steps; not required for first smoke.

---

## 3. Technical guidelines

1. **Never ship laptop `build/`** to the mini.  
2. **Never put PE* or multi-day fort.63 on system Data.**  
3. Prefer **env file** (`adcirc-env.sh`) over editing skill for brew prefix until skill is dual-prefix aware.  
4. Mesh family isolation still holds (ricv1 ≠ v18 ≠ Deb weirpumps).  
5. Keep secrets mode `600`; kit contains MetGet key — treat drive as sensitive.  
6. Optional second pack: `unity-archive/surgical` (~32 GiB) if Floodwater YAML beyond meshes is needed.  
7. Goldens under `adcirc-local-smoke/` are **reference**, not required for first green GFS run.

---

## 4. Boilerplate / env (mini)

```bash
# ~/.zshrc fragment (after bootstrap)
source /Volumes/ssd/projects/adcirc-env.sh
# optional:
# source /Volumes/ssd/projects/setApiKey.sh

# Stage ricv1 from kit
KIT=/Volumes/ssd/projects/macmini-adcirc-kit
CASE=$ADCIRC_WORK_ROOT/ricv1_$(date -u +%Y%m%d%H)
mkdir -p "$CASE"/{analysis,forecast}
for ph in analysis forecast; do
  cp "$KIT/meshes/ricv1_noriv_nopump/linked_files/ricv1_noriv_nopump.grd" "$CASE/$ph/fort.14"
  cp "$KIT/meshes/ricv1_noriv_nopump/linked_files/ricv1_noriv_nopump_fort.13" "$CASE/$ph/fort.13"
done
# fort.15 from template / prior proven case — never invent physics
```

```bash
# Stage ec95d smoke seed
CASE=$ADCIRC_WORK_ROOT/ec95d_smoke
mkdir -p "$CASE"
cp $KIT/smoke-seeds/ec95d_run/fort.{13,14,15} "$CASE/"
```

---

## 5. Key decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Kit size | Curated ~1.6 GiB | Full surgical 32 G optional; first path is rebuild + smoke |
| Binaries | Rebuild on mini | ISA mismatch arm64→x86_64 |
| Work disk | `/Volumes/ssd` | System volume too small |
| Brew prefix | `/usr/local` on mini | Intel Homebrew convention |
| Parametric Docker | Defer | GFS path first; windgfdl still Linux |
| Secrets in kit | Yes (mode 600) | MetGet required for default wind mode |
| Host discovery | `macmini.sh` Tailscale | Already operator path |

---

## 6. PR / implement plan (on mini after transfer)

| PR | Work | Gate |
|----|------|------|
| **M0** | USB/rsync kit → SSD; layout projects | paths exist |
| **M1** | Run `bootstrap-macmini.sh` | x86_64 padcirc + padcswan |
| **M2** | ec95d tides 6 h smoke | terminating normally |
| **M3** | ec95d latest gfs + post water+wind | PNGs + obs |
| **M4** | Patch skill/mesh cards if kit paths need first-class aliases | `/run-adcirc ricv1` stages without surgical |
| **M5** | Optional: Docker + parametric lee smoke | windgfdl in container |
| **M6** | Optional: rsync surgical + goldens | parity with laptop archive |

---

## 7. Risk register

| Risk | Mitigation |
|------|------------|
| cmake netCDF find fails on Intel brew | bootstrap falls back; set `-DNETCDF_DIR` |
| System python 3.9 too old | brew python@3.13 + PIPENV_PYTHON |
| Internal disk full mid-run | work_root gate on SSD free space |
| Tailscale down | USB transfer of kit still works |
| Skill hardcodes /opt/homebrew | adcirc-env.sh + M4 path fix |

---

*Design for desert-island mini: rebuild local, stage meshes from kit, run the same skill law.*
