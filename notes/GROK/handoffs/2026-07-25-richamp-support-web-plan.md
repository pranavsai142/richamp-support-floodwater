# Plan: richamp-support-web / suite house — scientific fidelity → ORDER 11

**Primary SoT:** `2026-07-25-richamp-support-web-handoff.md` (full integrity bar + ORDER 9 Ida 36h contract)  
**Design:** `2026-07-25-richamp-support-web-design.md`  

---

## Goal

**richamp-support-web** = multiphysics coastal fieldpack export + house layers with **≥ offline RICHAMP scientific integrity**, modern interactive fidelity (globe + 2D), unified with **Path B SHiELD/FV3** (GFS-class atmosphere).

---

## Fidelity bar (non-negotiable)

- Fieldpack SoT; no invented coords/fields  
- Real mesh / real grids; station stencil via Readers  
- Units/conventions (PRMSL **mb**; wind dir parity; swath=max; rain=sum)  
- Multiphysics: water · wind · rain · topo · **waves**  
- Verify harnesses; Path B laws preserved  
- Runup **out** this ladder  

---

## Golden contracts

| Side | Path |
|------|------|
| **Atmos ORDER 9** | `~/projects/SHiELD_OPS/runs/ida-smoke-20260725T232930Z/products/fieldpack/` (36h, tiles 1–6, verify PASS) |
| Coast water graphs | `~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/post_forecast/graphs/` |
| Coast wind graphs | `~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/post_wind/graphs/` |
| Coast waves graphs | `~/projects/richamp-support-floodwater/post_forecast/graphs/` |

Path B open:

```bash
rsync -a --delete $RUN/products/fieldpack/ ~/projects/CloudVision/threejs-shield-live-viz/data/fieldpack/
# server 3412; Play = PRMSL 0..35; globe tiles + nest
```

---

## ORDER 0–11

| O | Deliverable |
|--:|-------------|
| 0 | Law + fidelity bar |
| 1–2 | Coastal export skeleton + mesh/zeta |
| 3–4 | Loader unstructured + globe water |
| 5–6 | Stations + click/time |
| 7 | Multiphysics: wind + rain + **waves** |
| 8 | 2D scientific finality |
| **9** | **Ida 36h FV3 integrate + dual suite + wind bridge** |
| 10 | Deep links + thin ops (`/fv3-viz`, `/run-adcirc`) |
| 11 | House finality / G-DEPRECATE-READY |

ORDER 9 tips: gfdl-fieldpack/v0; PRMSL mb; nest + cube tiles; surface hourly vs 3D 3h clocks; Q=humidity not clouds; no dycore SoT. Full text in handoff §6.A / §7.

---

## Gates

G-PACK · G-LOAD · G-GLOBE · G-STN · G-CLICK · G-MULTI · G-2D · **G-FV3/G-HOUSE** · G-OPS · G-FINAL · G-DEPRECATE-READY · G-EXT

---

*Integrity first. Path B spine. Ida 36h truth. Waves in. Runup later.*
