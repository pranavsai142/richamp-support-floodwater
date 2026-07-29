# 2026-07-28 — Handoff: Mac mini always-on ADCIRC kit staged

**Status:** kit **partitioned on external drive**; machine **probed**; bootstrap script ready.  
**Not done on mini yet:** brew install, rebuild, first smoke (needs transfer).  
**Plan:** `2026-07-28-macmini-adcirc-always-on-plan.md`  
**Design:** `2026-07-28-macmini-adcirc-always-on-design.md`  
**Kit:** `/Volumes/Pranav's Hard Drive/macmini-adcirc-kit/` (~**1.6 GiB**, MANIFEST all OK)

---

## 1. One-screen status

| Item | State |
|------|--------|
| Mini SSH | **Reachable** — `pranavs-mac-mini.tail7f4d6b.ts.net` (`~/projects/macmini.sh`) |
| Mini chip | **Intel i7-8700B x86_64**, 12 threads, **64 GB RAM**, macOS 15.7.7 |
| Mini disk | System ~12 GiB free; **`/Volumes/ssd` 1.7 TiB (~1.3 TiB free)** — work home |
| Mini toolchain | **No** brew / gfortran / MPI / netCDF / Docker / ADCIRC / this repo |
| Laptop padcirc | **arm64** — **will not run on mini** |
| Transfer kit | **Staged** on Hard Drive; curated meshes + source + skill + secrets |
| Bootstrap script | `macmini-adcirc-kit/scripts/bootstrap-macmini.sh` |
| First smoke on mini | **Pending transfer** |

---

## 2. What we learned about the machine

```text
ssh pranavs-mac-mini.tail7f4d6b.ts.net
  hostname: Macmini.lan
  uname:    x86_64 Darwin 24.6.0
  CPU:      Intel(R) Core(TM) i7-8700B @ 3.20GHz
  RAM:      64 GB
  projects: ~/projects → /Volumes/ssd/projects
  Xcode+CLT: present
  brew:     missing  → install will use /usr/local (Intel)
```

**Always-on value:** leave multi-day ricv1 analysis + MetGet + forecast attached hotstarts running without the M3 laptop.

**ISA cliff:** every native binary from the laptop ADCIRC build is Mach-O **arm64**. The kit ships **source only** (no `build/`). Parametric `windgfdl` is already **Linux ELF** — Docker still required for S3p on either Mac.

---

## 3. What’s in the kit (partition)

```text
/Volumes/Pranav's Hard Drive/macmini-adcirc-kit/
  README.md MACHINE.md MANIFEST.txt
  scripts/bootstrap-macmini.sh   # brew + cmake padcirc/adcprep/padcswan + pipenv + tide_fac
  scripts/macmini.sh
  secrets/setApiKey.sh           # MetGet (mode 600)
  src/adcirc/                     # source + thirdparty/swan, NO arm64 build
  src/richamp-support-floodwater # skill + post (thesis/fat excluded)
  meshes/ricv1_noriv_nopump/linked_files/  # grd + fort.13 + fort.15
  meshes/ec95d/                  # fort.13/14
  meshes/englandv18/             # v18 mesh pack
  templates/v18RunTemplate/{analysis,forecast}/  # fort inputs only
  smoke-seeds/ec95d_run/         # proven fort.13/14/15
  handoffs/                      # copy of this migration set
```

**Deliberately out:** PE*, fort.63/68, full `unity-archive/surgical` (~32 G), Lee goldens (~10 G), thesis ASSET.

**Optional later rsync to mini SSD:**

| Pack | ~Size |
|------|------:|
| `unity-archive/surgical/` | 32 G |
| `adcirc-local-smoke/` goldens | 10 G |

---

## 4. Transfer recipes

### USB (drive plugged into mini)

```bash
KIT="/Volumes/Pranav's Hard Drive/macmini-adcirc-kit"
SSD=/Volumes/ssd/projects
rsync -a --info=progress2 "$KIT/" "$SSD/macmini-adcirc-kit/"
rsync -a "$KIT/src/adcirc/" "$SSD/adcirc/"
rsync -a "$KIT/src/richamp-support-floodwater/" "$SSD/richamp-support-floodwater/"
cp -p "$KIT/secrets/setApiKey.sh" "$SSD/setApiKey.sh" && chmod 600 "$SSD/setApiKey.sh"
mkdir -p "$SSD/adcirc-local-smoke"
bash "$SSD/macmini-adcirc-kit/scripts/bootstrap-macmini.sh"
```

### Tailscale rsync (drive stays on laptop)

```bash
HOST=pranavs-mac-mini.tail7f4d6b.ts.net
KIT="/Volumes/Pranav's Hard Drive/macmini-adcirc-kit"
rsync -a --info=progress2 -e ssh "$KIT/" "$HOST:/Volumes/ssd/projects/macmini-adcirc-kit/"
ssh $HOST 'bash /Volumes/ssd/projects/macmini-adcirc-kit/scripts/bootstrap-macmini.sh'
# (bootstrap rsyncs src → ~/projects/adcirc + repo if missing)
```

---

## 5. Path law after bootstrap

| Role | Mini path |
|------|-----------|
| padcirc / adcprep / padcswan | `~/projects/adcirc/build/` (**x86_64**) |
| DYLD / brew | **`/usr/local/opt/{netcdf,netcdf-fortran,hdf5}`** — not `/opt/homebrew` |
| Env helper | `source ~/projects/adcirc-env.sh` (written by bootstrap) |
| MetGet | `source ~/projects/setApiKey.sh` |
| Work root | `~/projects/adcirc-local-smoke/` on SSD |
| ricv1 mesh | `~/projects/macmini-adcirc-kit/meshes/ricv1_noriv_nopump/linked_files/` |
| v18 template | `…/templates/v18RunTemplate/` |
| ec95d seed | `…/smoke-seeds/ec95d_run/` |

`/run-adcirc` skill still applies end-to-end (S0–S9, contracts, checklist). Only **host paths** and **binary rebuild** differ.

---

## 6. Next session on the mini (`/init` then)

```text
1. Confirm kit on /Volumes/ssd/projects/macmini-adcirc-kit (MANIFEST OK)
2. bootstrap-macmini.sh if not already run
3. Gate: file ~/projects/adcirc/build/padcirc | grep x86_64
4. Smoke: stage smoke-seeds/ec95d_run → short tides padcirc np=2
5. /run-adcirc ec95d latest gfs  (or manual S1–S9)
6. If skill mesh cards still point only at surgical Hard Drive paths:
   point ricv1/v18 stage paths at MACMINI_ADCIRC_KIT (PR-M4 in design)
7. Optional: Docker Desktop → parametric lee
8. Optional: continuous analysis hotstart chain
```

---

## 7. Gates (this session vs next)

| Gate | This session | On mini later |
|------|--------------|---------------|
| Mini probed (chip/disk/tools) | **PASS** | — |
| Kit staged + MANIFEST critical OK | **PASS** | verify after copy |
| x86_64 padcirc built | — | required |
| ec95d smoke terminating normally | — | required |
| MetGet + post graphs | — | required for “parity” |
| ricv1 multi-day | — | after ec95d green |

---

## 8. Anti-patterns

- Copying M3 `~/projects/adcirc/build/*` to the mini and expecting it to run.  
- Filling the 113 GiB system volume with fort.63 / PE*.  
- Assuming `/opt/homebrew` exists on Intel mini.  
- Blocking first GFS run on Docker/windgfdl.  
- Shipping multi-GB `richamp.wnd` in the minimum kit.

---

## 9. Open items

- [ ] User transfers kit to mini SSD  
- [ ] Run bootstrap on mini  
- [ ] First ec95d + GFS green run  
- [ ] Skill mesh-card path aliases for kit (if surgical absent)  
- [ ] Docker for parametric  
- [ ] Optional surgical/golden rsync  
- [ ] Continuous ½ h analysis after durable fort.68  

---

*Laptop is the authoring brain; mini is the always-on body. Rebuild on the body. Same skill law.*
