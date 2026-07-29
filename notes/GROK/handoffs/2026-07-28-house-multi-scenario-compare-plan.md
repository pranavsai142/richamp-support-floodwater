# Plan — House multi-scenario compare + Lee fixtures (2026-07-28)

**Goal:** Revise house integration against **completed** parametric Lee + GFS twin; implement export → catalog → generic compare (anything vs anything) **with recursive residuals through 4th order**.

**Design:** `2026-07-28-house-multi-scenario-compare-design.md`  
**Inventory:** `notes/GROK/research/2026-07-28-parametric-scenario-file-inventory.md`

## Phases

1. **Export** both Lee packs from real paths; enrich `meta.scenario` + roles.  
2. **Catalog** cards + `compare_group` / residual preset tree.  
3. **Inspect** track + param wind on param pack.  
4. **Compare + residual engine** — N slots, UTC, multi-series + obs; ResidualNode graph R0–R4.  
5. **Mesh residual maps** + R3/R4 presets; abs/norm ops.  

## Success

- User opens Lee preset, sees parametric vs GFS ζ **and** R1 errors **and** R2 error-superiority without special-case code.  
- User can stack another residual (R3/R4) from residual sources.  
- Same machinery can compare any two catalog packs.  
- Param pack never labeled GFS; track visible; NaN residual policy holds.

## Fixtures

```text
/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_lee_param_20230909
/Volumes/Pranav's Hard Drive/adcirc-local-smoke/ec95d_lee_gfs_20230909
```
