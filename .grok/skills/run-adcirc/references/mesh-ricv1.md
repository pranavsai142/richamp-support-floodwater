# Mesh: ricv1 (Floodwater)

**When to load:** user said `ricv1` / skill/obs / station comparison.  
**Solver:** mainline `~/projects/adcirc/build/` only — **not** adcirc-cg.

## Stage

```text
…/unity-archive/home/pranav_sai_uri_edu/floodwater_files/ricv1_noriv_nopump/linked_files/
  ricv1_noriv_nopump.grd          → fort.14   (title must be ricv1_noriv_nopump)
  ricv1_noriv_nopump_fort.13      → fort.13
  ricv1_noriv_nopump_closedbar2.grd  only if user wants closed barrier
```

Also copy `time_varying_weir.in` if present (Fox Point). Keep fort.15 `&TVWControl` if template has it.

**Wrong:** Deb `ec95_v18_weirpumps` (IBTYPE 26 pumps) — different mesh; needs adcirc-cg.

## fort.15

| Item | Value |
|------|--------|
| DT | 0.25 s |
| Hourly NOUTGE NSPOOL | **14400** |
| NSCREEN | large (e.g. 14400), not 1 |
| NWP (exactly 4) | mannings_n_at_sea_floor · primitive_weighting_in_continuity_equation · advection_state · elemental_slope_limiter |
| np | min(8, ncpu) |
| NFFR | **omit** — noriv_nopump has no flux IBTYPE (2/12/22). An extra `0 ! NFFR` after ANGINN → adcprep `elev_stat.151` (negative NSTAE desync) |

No `sea_surface_height_above_geoid` in NWP.

## Met / runtime

- MetGet domain pad: `gfs 0.25 -100 5 -55 47`  
- ~663k nodes → multi-hour+ analysis on Mac; report ETA after first progress  
- TVW times = days since coldstart (stock day-16 often no-ops on RNDAY=11)  
- Post skill: small closest-node threshold (dense RI mesh)

## Default phrase

`/run-adcirc ricv1 latest gfs` → wind, latest cycle, analysis 6 d + forecast 5 d, post water+wind+obs.
