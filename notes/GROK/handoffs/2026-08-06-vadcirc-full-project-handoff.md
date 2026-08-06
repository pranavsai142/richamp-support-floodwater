# 2026-08-06 — Handoff: **vadcirc** (ADCIRC + SWAN → VRAM)

**Status:** North star **revised**. Plan + design updated. Implementation not started.  
**Plan:** `2026-08-06-vadcirc-full-project-plan.md`  
**Design:** `2026-08-06-vadcirc-full-project-design.md`  
**Research:** `notes/GROK/research/2026-08-06-vadcirc-full-conversion-summary.md`

---

## 1. Corrected goal (read this first)

### The project is about the **solver in VRAM**

**Port ADCIRC (and then SWAN) to GPU/VRAM carefully, properly, accurately, and efficiently.**

It is **not** primarily about:

- ricv1 or any science mesh milestone  
- postprocessing / fieldpack / house viz  
- operational `/run-adcirc` GFS chains  

Those may integrate **later**. They are not the MVP and not the definition of “full.”

### True MVP

**Hello-world ADCIRC:**

1. **Compile** vadcirc (device + CPU twin)  
2. **Run** a minimal legitimate coldstart time loop  
3. **Identical results** GPU ↔ CPU (bit-for-bit preferred; see design §3)  

Only then grow: port **more functionality** onto VRAM **one slice at a time**, each slice re-proving identity, then efficiency (residency, bandwidth).

### “Everything is LA”

Still useful: GWCE is ELLPACK + JCG + assembly.  
Not sufficient alone: wet/dry, SWAN, I/O — but the **discipline** is identity-preserving ports of each region, not mesh demos.

---

## 2. One-screen status

| Item | State |
|------|--------|
| North star | **VRAM port of ADCIRC(+SWAN), identity-first** |
| MVP | **Hello-world identical CPU/GPU** — not ricv1/fieldpack |
| Growth | S1…Sn capability ports under identity + efficiency |
| SWAN | **In long-term scope** after ADCIRC core identity |
| Code | **Not started** |
| Live ricv1 case on mini | Independent CPU campaign; do not conflate |

---

## 3. What next session implements

### First slice only: `vadcirc-HW-identity` (HW0–HW2)

| Step | Done when |
|------|-----------|
| HW0 | Scaffold `vadcirc/`, hello fort.14/15 case, CPU twin runs |
| HW1 | Device backend runs same case |
| HW2 | **Bit-diff empty** (or documented exact identity policy met) |

**Do not** start ricv1, MetGet, fieldpack, or skill flags in this slice.

### After HW2

Follow design §5 / §8: SpMV → JCG → assemble → wet/dry → momentum → … → SWAN couple, **identity each time**, efficiency after.

---

## 4. Architecture (unchanged spine, new gates)

```text
vadcirc driver
  ├─ backend=cpu  (twin / reference)
  └─ backend=cuda (VRAM)
same inputs → identical dumps
```

Mainline `adcirc/src` = **spec** (read-only).  
Production `padcirc` stays the ops binary until vadcirc is real.

---

## 5. Explicitly deprecated from prior handoff text

| Old framing | New framing |
|-------------|-------------|
| MVP0 = ec95d tides + fieldpack | **MVP = hello-world identity** |
| MVP1–3 = ricv1 / wind / hotstart as “done” | Optional later; not project definition |
| Waves “out of v1 forever” | SWAN **in** after ADCIRC core identity |
| Station tol 1e-3 m as first bar | **Identity** first |
| House / run-adcirc as center | Solver port is center |

---

## 6. Hard lessons (still true)

- Mini Open MPI: `btl self,sm` (not TCP) for padcirc  
- Wet/dry forces matrix rebuild — port carefully  
- No published full CG/GWCE ADCIRC GPU twin — greenfield with DG-SWEM as engineering reference only  
- Efficiency without identity is failure  

---

## 7. Open items

- [ ] HW0–HW2 hello-world identity  
- [ ] S1+ capability ports under identity  
- [ ] SWAN path after ADCIRC core  
- [ ] Choose device backend (CUDA vs Metal) for first HW1  
- [ ] FP flags for bit-stability  
- [ ] Optional late: ops integration (skill, large meshes, post)  

---

## 8. File index

| Doc | Path |
|-----|------|
| This handoff | `notes/GROK/handoffs/2026-08-06-vadcirc-full-project-handoff.md` |
| Plan | `notes/GROK/handoffs/2026-08-06-vadcirc-full-project-plan.md` |
| Design | `notes/GROK/handoffs/2026-08-06-vadcirc-full-project-design.md` |
| Research | `notes/GROK/research/2026-08-06-vadcirc-full-conversion-summary.md` |

---

## 9. Bottom line for next agent

**MVP is not a coastal product slice.**  
**MVP is: compile, run hello-world ADCIRC, GPU results ≡ CPU results.**  

Then carefully move more of **ADCIRC (+SWAN)** into VRAM for accuracy and efficiency.  
Do not optimize the wrong goal (ricv1/post) until the solver identity path exists.

**Start:** `vadcirc-HW-identity` (HW0–HW2).
