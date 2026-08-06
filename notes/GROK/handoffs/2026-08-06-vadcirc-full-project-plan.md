# Plan: **vadcirc** — ADCIRC (+SWAN) on VRAM

**Date:** 2026-08-06 (revised north star same day)  
**Product:** `vadcirc` — mainline physics on GPU/VRAM, proven by **identity to CPU**  
**Supersedes:** mesh-centric / fieldpack-centric MVP ladders (ricv1, house post). Those are **optional later integration**, not the goal.

---

## 1. Real north star

**Move ADCIRC (+ eventually SWAN) into VRAM carefully, properly, accurately, and efficiently.**

The point is the **solver**, not:

- a particular coastal mesh (ricv1 / ec95d / v18),
- MetGet / operational chains,
- postprocess, fieldpack, or house viz.

Those may consume vadcirc later. They do not define done.

---

## 2. True MVP (only MVP that matters first)

### MVP-HW: Hello-world identity

| Requirement | Spec |
|-------------|------|
| **Compile** | `vadcirc` builds (device path + host driver) |
| **Run** | Smallest legitimate ADCIRC coldstart that exercises the time loop (tiny mesh or kit smoke fort.14/15; **not** “must be ricv1”) |
| **Compare** | Same inputs → **identical results** GPU vs CPU reference path |
| **Identical means** | Same fort.63 (and fort.61 if stations) to **bit-for-bit** where possible; if FP non-associativity forces a gap, **documented bitwise policy** + still match a **same-codepath CPU device-emulator** and a **strict padcirc golden within a frozen reduction order** — prefer **bit-identical on a single-rank, deterministic kernel path** first |

**Exit:** one command runs hello-world on CPU-oracle and GPU; diff is empty (or zero within explicit exact policy). No science “tol 1e-3 m” as the primary bar for the first kernel slice.

Until MVP-HW is green, **do not** expand to wind, hotstart chains, SWAN, or production skill flags.

---

## 3. Growth model after MVP-HW

**Port more functionality to VRAM incrementally**, each slice:

1. Choose one routine/region (e.g. ELL SpMV, then JCG, then GWCE RHS, then wet/dry, then momentum, then met, then SWAN couple).  
2. Implement on device.  
3. **Identity gate** against CPU for that slice (or full hello-world still identical).  
4. Only then measure efficiency (bandwidth, occupancy, wall).  
5. Never “faster but wrong.”

### Capability track (order of physics, not meshes)

```text
HW: hello-world time loop, identity
S1: sparse matvec (ELL) on device, identity
S2: full JCG on device, identity
S3: GWCE assemble (LHS/RHS) on device, identity
S4: wet/dry on device, identity (hard — do carefully)
S5: momentum on device, identity
S6: common forcings (tides/met stubs as needed for hello-world+)
S7: multi-step + fort.63 spool still identical
S8: padcswan path / SWAN couple — identity on a minimal wave-enabled case
…
Sn: optional: larger meshes, MPI multi-GPU, ops integration
```

**SWAN is in scope for the project** as “ADCIRC(+SWAN)”, not forbidden — but **only after** pure ADCIRC identity path is solid.

---

## 4. Efficiency (why VRAM)

Efficiency work is **second** to identity, but is the *reason* for VRAM:

- Keep state **resident** (no per-step full download).  
- Prefer ELL (native) or measured layout for coalescing.  
- Fuse kernels only after identity.  
- Profile device bandwidth vs FLOP; target memory-bound FE SpMV/assembly.  
- Document GB/s and wall vs CPU for each green slice.

---

## 5. Explicit non-goals for early slices

| Not a goal | Why |
|------------|-----|
| ricv1 / science mesh throughput first | Distraction until identity exists |
| fieldpack / house / generateGraphs | Consumer of outputs, not the port |
| `/run-adcirc` skill flag first | Wire after solver is real |
| “1e-3 m station tol” as first bar | Too loose for a careful port; use identity |
| Speed claims without identity | Forbidden |

---

## 6. First implement slice

**`vadcirc-HW-identity`**

1. Pick/fix minimal fort.14/15 hello-world (smoke seed OK if small).  
2. CPU path: either thin driver calling same kernels in host, or padcirc single-rank golden with frozen options.  
3. Device path: compile + run same case.  
4. Diff outputs → **identity**.  
5. Then S1+ only.

---

## 7. Related docs

| Doc | Role |
|-----|------|
| Design (revised) | Architecture + slice gates under identity rule |
| Handoff | Next agent memory |
| Research summary | LA map + prior art (still valid; MVP ladder replaced) |
