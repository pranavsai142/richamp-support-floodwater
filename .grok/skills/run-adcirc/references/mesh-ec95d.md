# Mesh: ec95d (smoke only)

**When to load:** user said `ec95d` / smoke / pipeline test.  
**Solver:** mainline `~/projects/adcirc/build/`.

## Stage

```text
~/projects/adcirc-local-smoke/ec95d_run/   # fort.13 fort.14 fort.15
```

## fort.15

| Item | Value |
|------|--------|
| DT | 10 s |
| Hourly NOUTGE NSPOOL | **360** |
| np | min(4, ncpu) fine |

## Met / runtime

- MetGet: `gfs 0.25 -98 7.5 -59.5 46.5` (or wider pad)  
- ~31k nodes → multi-day finishes in ~minutes–tens of min  
- **Not science skill** at stations — coarse mesh + far neighbors  
- Proven: 6d+5d wind, 1d waves NOUTGW (see proven-runs.md)
