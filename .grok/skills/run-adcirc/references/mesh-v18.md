# Mesh: v18

**When to load:** user said `v18` / full NE hi-res / england-class.  
**Solver:** mainline `~/projects/adcirc/build/`.

## Stage

```text
…/unity-archive/surgical/project/AdcircManualRuns/ScenarioRuns/v18RunTemplate/
  analysis|forecast fort.13 fort.14 fort.15 fort.20 time_varying_weir.in
```

Gate: fort.14 title family is v18/hsofs NE-hires — not ricv1, not Deb weirpumps-only.

## fort.15

| Item | Value |
|------|--------|
| DT | 0.25 s |
| Hourly NOUTGE NSPOOL | **14400** |
| NSCREEN | large, not every step |
| NWP | match **this** fort.13 (usually 5 attrs including sea_surface_height_above_geoid) |
| np | min(8, ncpu) |

## Met / runtime

- MetGet: `gfs 0.25 -100 5 -55 47` (cover full mesh)  
- ~2.6M nodes → multi-day wall on Mac for multi-day RNDAY — **state ETA before launch**  
- TVW same law: days-since-coldstart  
- Post: medium closest-node threshold

## adcirc-cg?

Only if this mesh revision has IBTYPE **6/26** pumps and mainline rejects them. Stock Floodwater ricv1 does not apply here; v18 template may have weirs without 26.
