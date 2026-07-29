# 2026-07-27 — Handoff: Parametric wind → knowledge base + house-viz integration design

**Session type:** `/research` + knowledge capture + `/handoff` (no implement)  
**Supersedes for this topic:** nothing prior (new vertical)  
**Depends on:** house ORDER 0–11 complete; owi2wind is306 fix; run-adcirc GFS path  
**Companions:**

| Artifact | Path |
|----------|------|
| Research | `notes/GROK/research/2026-07-27-parametric-wind-pipeline.md` |
| Wiki | `notes/WIKI/parametric-wind-pipeline.md` |
| Plan | `notes/GROK/handoffs/2026-07-27-parametric-wind-house-viz-plan.md` |
| Design | `notes/GROK/handoffs/2026-07-27-parametric-wind-house-viz-design.md` |

---

## 1. One-screen status

| Item | State |
|------|--------|
| Operator parametric recipe (Milton/Erin) | **Captured** in research + wiki |
| fort.15 domain `565 625 51… 0.083333…` | **Bound** to Wind_Inp / `generateParametricInput` / `oceanWeatherGenerator` math |
| owi2wind schema vs house `wind_gfs` | **Compatible vars** (`wind_u`/`wind_v`/`lon`/`lat`/`PSFC`) |
| First-class fieldpack product | **Designed, not implemented** — `wind_parametric` + stream `parametric` |
| windgfdl on Mac | **Cannot run** (Linux ELF) — use golden nc or remote |
| ASGS post_init full auto | **Still TODO** (documented) |
| Parametric rain in pack | **Deferred** |

---

## 2. What this session accomplished

1. Prospect Brief for parametric wind → house viz (foundations + hard questions).  
2. Deep first-party research: track → PWM inputs → `windgfdl` → `.wnd` → `owi2wind` → nc; dual roles drive vs post; domain encodings; footguns.  
3. Knowledge base:
   - Research note under `notes/GROK/research/`
   - New wiki page + INDEX + links from `how-to-construct-an-adcirc-run.md` and `what-we-use-and-need.md`
4. Integration plan + design (requirements, stories, adapter sketch, PR plan, size policy).  
5. Light DEV_NOTES pointer.

**No production code changes** to export/shell (by design).

---

## 3. Operator law (keep forever)

### Manual parametric wind

```text
metget build --domain nhc-…  →  nhc_merge_*.trk
generateParametricInput.main(trk)  →  track.richamp, Wind_Inp.txt, TrackRMW.txt, RICHAMP_rain.nc
./windgfdl  →  richamp.wnd
python owi2wind.py richamp.wnd Wind_Inp.txt -o <stem>  →  <stem>.nc
```

fort.22 track shortcut: `generateParametricInput.main("fort.22")`.

### fort.15 when driving with windgfdl 306

```text
565 625 51.000000 -101.000000 0.083333 0.083333
```

NWS = `6` or `306` (same met; 306 adds SWAN).

### Examples

- Milton: `nhc-2024-al-14-013` → `milton_parametric_wind`  
- Erin: `nhc-2025-al-05-021` → `erin_parametric_wind`

---

## 4. Integration decision (locked for implement)

**P0 preferred:** owi2wind parametric netCDF → new adapter `wind_parametric` (clone `wind_gfs`), stream `"parametric"`, **prefixed field keys** `param_wind_*` so dual-met packs (GFS + parametric) do not collide.

**Do not** silently path-override `wind_gfs` for production honesty.

**Size:** full Atlantic basin hourly multi-day packs need `--wind-stride` or bbox (same spirit as `wind_post` / `--post-stride`).

**Shell:** no new SPA; field-agnostic layers already carry vectors/particles.

---

## 5. Findings worth keeping

1. **Three different lon/lat boxes people mix up:** MetGet track download, PWM basin (−101…−49, 4…51), RI GFS post (−72…−70, 40…43). Only the middle one belongs on fort.15 for windgfdl.  
2. **owi2wind already speaks house language** — adapter work is labeling + stream + size guard, not a new binary format.  
3. **post_init TC_FORCING runs windgfdl but leaves generateParametricInput commented** — manual/pre-staged inputs still the reliable path.  
4. **windgfdl is a black-box Linux binary** in-repo (`file` → ELF); desert-island regen needs Linux or archived products.  
5. **SHiELD wind_bridge and parametric are parallel atmospheric producers** — both can feed NWS 6/306; neither replaces the other in the house.

---

## 6. Open items / next session start

### Implement (when ready)

1. Obtain golden `*.nc` (convert on Linux or pull from scenario_files / surgical archive).  
2. PR2 from design: `wind_parametric.py` + CLI path + fidelity guard + contract doc.  
3. Smoke export on ec95d or v18 case with `--path wind_parametric=…`.  
4. Optional PR3 shell display names; PR4 run-adcirc checklist link.

### Still open elsewhere (unchanged)

- Wave spatial fields unexercised (padcswan golden on unmounted drive)  
- Wind bridge → real ADCIRC ζ comparison (suite loop close)  
- Continuous ½ h hotstart chain  
- Basemap PNG orientation  

### Start prompt for implementer

```text
/init then implement parametric wind fieldpack adapter per
notes/GROK/handoffs/2026-07-27-parametric-wind-house-viz-design.md
Research: notes/GROK/research/2026-07-27-parametric-wind-pipeline.md
P0 only: wind_parametric adapter, stream parametric, param_wind_* keys,
explicit stride/subset for large grids. No windgfdl port. No second SPA.
Golden nc required before claiming G-MULTI.
```

---

## 7. Invariants (do not break)

Carry forward house law (fieldpack SoT, NaN dry, units in meta, stream-aware time, NWS 306=6+SWAN) **plus**:

- Parametric source must not be labeled GFS  
- fort.15 windgfdl domain is the 565×625 basin line unless Wind_Inp is deliberately changed  
- Decimation of science arrays is opt-in and recorded  

---

## 8. Anti-patterns

- Pasting MetGet track bbox into fort.15 for PWM met  
- Calling parametric wind “GFS” in meta because var names match  
- Shipping full-basin 10-day hourly f16 without stride  
- Expecting `./windgfdl` to work on macOS  
- Treating `RICHAMP_wind.nc` (RI downscale) as the same product as basin `richamp.wnd`  
- Roadmap dump into `/run-adcirc` (link wiki; stay thin)  

---

*One system writes the wind and the pressure. Sometimes that system is a parametric vortex on an NHC track. Capture the recipe; give it an honest seat in the house.*
