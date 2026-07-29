# Worknotes — house integration totality (2026-07-28)

Working index + quiz for the totality implementation session. Final report:
`2026-07-28-house-integration-totality-done-handoff.md` — **all phases
completed and gated**; every "missing" row in the index below shipped
(F3 wind_parametric · F4 track_export · F5 scenario/roles · F6 catalog+preset ·
F8 track layer · F9 CompareSession · F11 residual graph · F12 Lee preset ·
F13 gates G-LEE-*/G-COMPARE-*/G-RES-R1…R4/G-RES-MAP + test-residual.js 27/27).

## Fabel index (first-party analogs · planned vs current)

| ID | Element | First-party location | Planned | Current (verified this session) |
|----|---------|----------------------|---------|--------------------------------|
| F1 | fieldpack export mesh+ζ | `post/export/` (cli, pack_writer, water_fort63, mesh_adapter) | Lee both cases | works; Lee forecast fort.63 = 72 hourly snaps 2023-09-15T01→09-18T00 |
| F2 | wind_gfs adapter | `field_adapters/wind_gfs.py` | honest GFS twin (`gfs_wind.nc` 217×157×155, lat asc) | exists, registered |
| F3 | wind_parametric | NEW `field_adapters/wind_parametric.py` | param nc 216×565×625 (lat asc 4→51), stream `parametric`, honest long_names, explicit `--wind-stride` | **missing** |
| F4 | track export | NEW `post/export/track_export.py` | `tracks/drive_track.json` + `tracks/catalog.json` from `lee_best_track.trk` (BEST ATCF, 141 rows incl. radii dupes) + `track.richamp` (55 rows) | **missing** |
| F5 | meta.scenario + roles | `cli.py` + writer meta | `scenario{storm, met.family, wind_mode, default_utc}`, `roles{water_surface, water_max, wind_10m_*}`, `modes.wind` string, `modes.track` | partial: run_id + coldstart_utc only; modes.wind collapsed to bool |
| F6 | packs.json catalog | VIZ `data/packs.json` | Lee param + GFS cards (id, met_family, default_utc, compare_group) + `compare_presets` residual tree | only Ida + coast-ec95d `{label,url,suite}` |
| F7 | loadPack single | `suite-shell.js` loadPack | keep; add default_utc snap + tracks load | done (ORDER 0–11) |
| F8 | track layer | `suite-shell.js` NEW buildTrackLayer + loader `tracks/` | polyline + positions, default ON when `met.family=parametric` / `modes.track` | **missing** |
| F9 | CompareSession N slots | `suite-shell.js` NEW compare mode | N slots (UI min 2), merged-UTC master timeline, role binding | **missing** (1 pack at a time) |
| F10 | SuiteChart multi-trace | `suite-chart.js` `plot([])` | R0…R4 + obs series | already multi-trace (station panel proves it) |
| F11 | ResidualNode graph R0–R4 | NEW `suite-residual.js` (pure UMD) | SourceRef pack\|obs\|residual; op `sub` (+`abs_sub`); recursive order ≥4; cycle reject; NaN propagate; `window_mean` reduce; station override | **missing** |
| F12 | Lee residual preset | packs.json `compare_presets` | R1_po, R1_go, R1_pg, R2_err + R3_err_anom, R4_cross_stn | **missing** |
| F13 | Harnesses | verify_pack.py / verify-fieldpack.js / verify-shell.js / test-suite-modules.js | + G-LEE-*, G-COMPARE-*, G-RES-R1..R4, `test-residual.js` | ORDER 11 baseline PASS set |
| F14 | DiffGrapher analog | `DiffGrapher.py` L932–935 (Forecast + Diff + Tide co-plot) | generalized to residual-tree multi-series | offline only |

### Session-verified fixture facts

- `fort.14` **md5-identical** between the two Lee cases → mesh fingerprint match is guaranteed for residual maps.
- Streams: adcirc forecast 72 hourly (09-15T01→09-18T00) · parametric 216 h (09-09T00→09-17T23) · gfs 217 h (09-09T00→09-18T00). No shared index possible; UTC matching required.
- `default_utc` hint 2023-09-16T00:00Z → adcirc forecast index 23.
- `RICHAMP_rain.nc` has **time=1** (single snapshot) → rain export skipped; documented gap, not blocking.
- Adapter registry today: water_fort63 · wind_fort74 · wind_gfs · wind_post · rain_gfs · waves_swan · maxele.
- Local regression pack: `~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/products/fieldpack` (staged as `data/coast-ec95d`).
- Both wind grids lat-ascending; both time units minutes since 1990-01-01 (Reader GFS format).

## Quiz answers (from sources)

- **Q1** Display SoT is the fieldpack (meta.json + LE binaries). Science arrays never enter the browser as NetCDF; geometry is never free-painted (invariant 1).
- **Q2** `$CASE_P/met_pwm/lee_parametric_wind.nc` — time=216, latitude=565, longitude=625; vars time/lon/lat/PSFC/wind_u/wind_v; minutes since 1990-01-01. Tracks: `met_pwm/lee_best_track.trk` (BEST ATCF) + `met_pwm/track.richamp` (PWM geometry), copies in `properties/`.
- **Q3** Under pure `sub`, (A−obs)−(B−obs) ≡ A−B; R2 stays a node because operators think in error space (pedigree label "param err − GFS err") and non-linear ops (abs/norm/skill) break the identity. Deleting it loses operator language.
- **Q4** Master scrub is an index on the master stream; every other field maps by **timestamp** — `timeIndexFor()` → `nearestTimeIndex(own.times_utc, master.times_utc[i])`. Never index sharing.
- **Q5** Orders-complete §7: (1) fieldpack is display SoT; (2) NaN = dry, never 0; (3) coordinates from the run; (4) every field declares a stream, scrub by timestamp; (5) PRMSL is mb; (6) units live in meta → colorbar; (7) swath = max, rain accum = sum; (8) wind dir `atan2(-v,u)` once in shell; (9) decimation explicit + recorded; (10) `modes.runup` false; (11) stencils from Reader.py; (12) one shell, one loader, one schema allowlist.
- **Q6** G-EXT: a new product = one adapter file + one import line in `field_adapters/__init__.py`; unknown fields still plot with units from meta, no chrome edit.
- **Q7** `met_pwm/richamp.wnd` (~2.2 G raw 306 grid) and `forecast/fort.22` (~2.2 G drive met): raw drive files already summarized in the nc; multi-GB payloads have no place in a browser pack.
- **Q8** "Anything vs anything" = N slots bound to catalog packs / obs / residual nodes, paired by `meta.roles` (fallback identical field names), master clock absolute UTC, presets as data in `compare_presets` — no `if (gfs && parametric)` code path.

## Wind stride decision (explicit, recorded)

Param wind 216×565×625 would be 4 fields × 152 MB f16 = ~610 MB in one pack —
unusable next to a second pack. Export uses `--wind-stride 3` → 216×189×209
(stride lands exactly on the last row/col: 564=3·188, 624=3·208), ~17 MB/field,
1/4°-class spacing (comparable to the GFS twin). Recorded in
`meta.fidelity.decimation` and per-field rows; full-resolution nc stays on disk.
