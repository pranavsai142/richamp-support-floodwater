# run-adcirc preflight / postflight checklist

## Before any launch

### Disk & tools
- [ ] Free space adequate (multi-day + hourly NOUTGE: plan ~1–5 GB; nspool=1 multi-day = multi-GB)
- [ ] Prefer external volume if internal free &lt; ~15 GB
- [ ] `padcirc` / `adcprep` at `~/projects/adcirc/build/`
- [ ] For waves: `padcswan` exists; else NWS=6 only
- [ ] `mpirun`; `DYLD_LIBRARY_PATH` has netcdf + hdf5 (Homebrew)
- [ ] `source ~/projects/setApiKey.sh` → METGET_API_KEY set
- [ ] `pipenv run metget credits` (or `which metget` on PATH) works
- [ ] Native `tide_fac` binary (arm64 Mach-O), not Linux ELF `a.out`

### Stage (S0)
- [ ] Unique `$WORK/$RUN_ID/{analysis,forecast}`
- [ ] fort.13, fort.14, fort.15 both phases
- [ ] Mesh from `meshes.md`; fort.14 **title** matches (ricv1 ≠ Deb weirpumps)
- [ ] fort.15 NWP names match fort.13 (ricv1 = 4 attrs)
- [ ] Time window stated: coldstart, forecast_start, forecast_end, both RNDAYs
- [ ] Mesh family consistent (ricv1 **or** v18 **or** ec95d — not mixed)
- [ ] mainline solver unless IBTYPE 6/26 pumps

### Clocks (S1)
- [ ] analysis base_date == forecast base_date
- [ ] analysis RNDAY = days coldstart → forecast start
- [ ] forecast RNDAY = days coldstart → storm **end**
- [ ] analysis IHOT=0 (or 368 continue); forecast IHOT=368 when attaching
- [ ] NOUTGE netCDF (−5/−3); TOUTF ≤ RNDAY; multi-day NSPOOL ~360 @ DT=10
- [ ] forecast NHSTAR / analysis NHSTAR=3 sensible

### Tides (S2)
- [ ] tide_fac with XDAYS=**forecast** RNDAY and coldstart BHR IDAY IMO IYR
- [ ] FF/FACE patched both fort.15s by constituent name
- [ ] analysis FF/FACE == forecast FF/FACE
- [ ] open-boundary amp/phase not rewritten

### Met (S3–S5) — wind/waves (GFS default)
- [ ] Domain covers **full mesh**
- [ ] fort.22 exists; NWS=6 (padcirc) or 306 (padcswan)
- [ ] Met line after REFTIM matches fort.22.meta (GFS) **or** PWM 565×625 line (parametric)
- [ ] **NOUTM + NSTAM** on forecast when NWS≠0
- [ ] **NOUTGW** on forecast when NWS≠0
- [ ] **No** NOUTM/NOUTGW on analysis NWS=0
- [ ] Enough snaps: coldstart → forecast end
- [ ] P in Pascals in fort.22

### Met (S3p) — parametric only (see `met-parametric.md`)
- [ ] Loaded `references/met-parametric.md`
- [ ] Track = **best track** for historical golden (not OFCL merge tail alone)
- [ ] `Wind_Inp` NHOURS set to campaign length (not 0 from BEST hours field)
- [ ] `haversine` available; generateParametricInput ran explicitly
- [ ] windgfdl via Docker: stdout discarded; product written in container `/tmp` then copied
- [ ] fort.15 met line is **565 625 51 −101 0.083333…** (not MetGet track box)
- [ ] Spot-check: domain max near track; no basin-wide blow-up (same-hour spike all stations)
- [ ] Optional: end met before deep ET / north-boundary blow-up

### Waves (S6)
- [ ] fort.26 dates retargeted; padcswan; RSTIMINC aligned (600 ↔ fort.26)
- [ ] NWS=306; met line has 8th field RSTIMINC
- [ ] **NOUTGW = −3/−5 with real spool** (not `0`) — swan products follow NOUTGW not NOUTGE
- [ ] SWANOutputControl HS/DIR/…=T (necessary, not sufficient alone)
- [ ] `swaninit` copied into each PE\* after adcprep
- [ ] launch `padcswan` (not padcirc); np ranks == PE count (N PIDs = one MPI job)

### Hotstart (S8)
- [ ] analysis fort.68.nc + terminating normally
- [ ] `cp analysis/fort.68.nc forecast/fort.68.nc`
- [ ] no cldir `rm *.nc` after copy

### Launch (S7)
- [ ] adcprep `--np` == mpirun `-np`
- [ ] cwd = phase dir with PE*
- [ ] Optional: analysis running while MetGet still building

---

## After solver

- [ ] `ADCIRC terminating normally` (and MPI 0) — or 100% COMPLETE + full ntimes if log quiet
- [ ] fort.63.nc netCDF with time/x/y/zeta
- [ ] waves: `swan_HS.63.nc` (+ DIR/TMM10/TPS) ntimes &gt; 0; ideally `rads.64.nc`
- [ ] time.units parses
- [ ] fort.68.nc if NHSTAR on
- [ ] `run_manifest.json` written

## After post (default stripped)

- [ ] Ran **without** `--generateRunup` unless user asked
- [ ] Log contains skip of USGS transect overlays (or no GetObsElevation)
- [ ] graphs/ non-empty (station `*_water.png`, `all_stations_water.png`, …)
- [ ] waves: swh/mwd/mwp/pwp(/rad) PNGs if `--wavesExists`
- [ ] `tempDir` trailing `/`
- [ ] If `--obsExists true`: obs_water_data_file.json has n_times &gt; 0 for most stations
- [ ] Model+obs overlay visible on water PNGs when dates real
- [ ] **Closest-node threshold matches mesh** (ricv1 small / v18 medium / ec95d large)
- [ ] **Do not over-read ec95d station skill** — process smoke only; science → ricv1/v18
- [ ] Scars appended to skill/research if anything new failed

---

## Quick “latest GFS wind + post” summary

```
coldstart = GFS_cycle − analysis_days (default 6)
analysis  = NWS=0, RNDAY=analysis_days, NHSTAR=3 → fort.68.nc
met       = MetGet owi (coldstart→end) → OceanweatherTo306 → forecast/fort.22
forecast  = IHOT=368, NWS=6, NOUTM+NOUTGW, RNDAY=analysis_days+forecast_days
launch    = local mpirun padcirc (analysis ∥ MetGet OK)
post      = generateGraphs water+mesh+obs; no runup/transects
```
