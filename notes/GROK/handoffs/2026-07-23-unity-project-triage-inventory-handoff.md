# Handoff — Unity project top-level triage inventory (2026-07-23)

## What was done

Began medical triage of `/project/pi_iginis_uri_edu/pranav_sai_uri_edu` with the atmospheric-twin **prune technique** (`find -prune` on `PE*`/`pe*` dirs and all `*.nc`).

### Durable artifacts

| Artifact | Role |
|----------|------|
| `notes/WIKI/unity-project-triage-inventory.md` | **Full top-level table** (42 entries): filtered GiB, pathway, P0–P3, rationale, next actions |
| `notes/GROK/ops/scripts/unity-prune-filtered-size.sh` | Reusable prune size helper |
| `test/test_unity_triage_inventory.py` + fixture | Completeness + no-bulk-rsync checks |
| Rubric / map / INDEX / DEV_NOTES | Updated with live prune figures |

### Live prune sizes (spot-check vs prior ballparks — all match)

| Tree | Prior | Live |
|------|------:|-----:|
| AdcircManualRuns | ~550 | **550.43 GiB** |
| ecflow_output | ~79 | **78.75 GiB** |
| workBackup32025 | ~72 | **72.22 GiB** |
| v18Runs | ~28 | **27.54 GiB** |
| project total | ~754 | **753.96 GiB** |

### Class takeaway

- **~729 GiB** of filtered mass is **P2** (ManualRuns + ecflow_output + workBackup + v18Runs) — NESE/Globus only, never casual login rsync.
- **P0 gems are small**: `floodwater_files`, `Ricv1Meshes`, `meshes`, QoL `read*Util.py`, Post_*.json, intel Unity build tree, ManualRuns templates/meshes/READMEs (second-level).
- **P3**: test-build clones, temps, empty `work`, regenerable GFS nc-heavy trees.

## Explicit non-action

**Did not** start or recommend `--only manual` / full ManualRuns pull.

## Next session

1. Monitor home+work pull if still running.
2. Deeper golden shortlist from ScenarioRuns + Scenarios.txt (1938, Sandy, Ram, Debby, Henri).
3. Surgical gem pack (configs, meshes, templates, QoL) — not bulk.
4. Optional Globus only for P2 bulk.
5. Cross-check home Floodwater configs vs `floodwater_files` after home pull.

## Verify

```bash
python3 -m unittest test.test_unity_triage_inventory -v
# or: python3 test/test_unity_triage_inventory.py -v
```

---

*Continue coastal archive/triage from this repo. Sister: CloudVision = atmosphere only.*
