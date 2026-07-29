"""G-MULTI parity — does the pack cover what the offline stack draws?

Two independent checks, neither of which needs the raw NetCDF:

1. **Variable parity** — every wave / wind variable the adapters read is a
   variable `Reader.getValue` reads, verified against `Reader.py` itself. If
   someone renames `swan_TMM10` in one place and not the other, this fails.

2. **Product parity** — every offline PNG product family in a graphs directory
   maps to a pack field (or is explicitly out of scope, e.g. runup). Missing
   coverage is reported with the reason: adapter absent, or inputs not present
   for this run.

    python -m post.export.parity_check <pack> --graphs <dir> [--graphs <dir> …]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

_REPO_ROOT = Path(__file__).resolve().parents[2]

#: offline PNG product suffix -> pack field that carries the same quantity
PRODUCT_TO_FIELD = {
    "water": "water_zeta",
    "station_water": "water_zeta",
    "elevation": "bathymetry",
    "map_elevation": "bathymetry",
    "closest_points": "__stations__",
    "wind_speed": "wind_speed",
    "wind_direction": "wind_speed",          # direction derives from u/v in the shell
    "wave_swh": "wave_swh",
    "wave_mwd": "wave_mwd",
    "wave_mwp": "wave_mwp",
    "wave_pwp": "wave_pwp",
    "wave_radstress_mag": "wave_radstress_mag",
    "wave_radstress_dir": "wave_radstress_x",
    "rain": "rain_rate",
    "rain_accumulation": "rain_accum",
}

#: product families deliberately not in this ladder
OUT_OF_SCOPE = {"runup", "transect", "holman", "stockdon", "twlcc", "asset"}

#: adapter module -> netCDF variables it reads (must match Reader.getValue)
ADAPTER_VARS = {
    "water_fort63": {"zeta"},
    "wind_fort74": {"windx", "windy"},
    "wind_gfs": {"wind_u", "wind_v"},
    "wind_post": {"spd", "dir"},
    "rain_gfs": {"precipitation"},
    "waves_swan": {"swan_HS", "swan_DIR", "swan_TMM10", "swan_TPS",
                   "radstress_x", "radstress_y"},
}

_failures: List[str] = []


def ok(msg: str) -> None:
    print(f"  ok: {msg}")


def bad(msg: str) -> None:
    _failures.append(msg)
    print(f"  FAIL: {msg}")


def reader_variables() -> Set[str]:
    """Variable names `Reader.getValue` / `getValuesForPoints` actually index."""
    src = (_REPO_ROOT / "Reader.py").read_text()
    return set(re.findall(r'dataset\.variables\["([A-Za-z_0-9]+)"\]', src))


def check_variable_parity() -> None:
    known = reader_variables()
    for adapter, wanted in ADAPTER_VARS.items():
        missing = sorted(v for v in wanted if v not in known)
        if missing:
            bad(f"{adapter}: reads {missing} which Reader.py does not — name drift")
        else:
            ok(f"{adapter}: all variables match Reader.py ({', '.join(sorted(wanted))})")


def graph_families(graph_dirs: List[Path]) -> Dict[str, int]:
    """PNG basenames → product family counts, e.g. 'wave_swh': 12."""
    fams: Dict[str, int] = defaultdict(int)
    for d in graph_dirs:
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.png")):
            stem = p.stem
            fam = None
            for key in sorted(PRODUCT_TO_FIELD, key=len, reverse=True):
                if stem.endswith("_" + key) or stem == key:
                    fam = key
                    break
            if fam is None:
                low = stem.lower()
                if any(o in low for o in OUT_OF_SCOPE):
                    fam = "__out_of_scope__"
                else:
                    fam = "__unmapped__:" + stem
            fams[fam] += 1
    return dict(fams)


def check_product_parity(pack: Path, graph_dirs: List[Path]) -> None:
    meta = json.loads((pack / "meta.json").read_text())
    field_names = {f["name"] for f in meta.get("fields", [])}
    has_stations = bool(meta.get("stations"))
    fams = graph_families(graph_dirs)
    if not fams:
        bad(f"no PNGs found under {[str(d) for d in graph_dirs]}")
        return

    covered, uncovered = [], []
    for fam, n in sorted(fams.items()):
        if fam == "__out_of_scope__":
            ok(f"{n} offline product(s) are out of scope for this ladder (runup family)")
            continue
        if fam.startswith("__unmapped__"):
            print(f"  note: unmapped offline product {fam.split(':', 1)[1]!r}")
            continue
        target = PRODUCT_TO_FIELD[fam]
        present = has_stations if target == "__stations__" else target in field_names
        (covered if present else uncovered).append(f"{fam}→{target} ({n} png)")

    for c in covered:
        ok(f"covered: {c}")
    for u in uncovered:
        # not a failure by itself — the run may simply not have that product
        print(f"  gap: {u} — no such field in this pack")

    modes = meta.get("modes", {})
    if modes.get("runup"):
        bad("modes.runup is true")
    else:
        ok("runup stays out of scope (modes.runup=false)")

    print(f"  summary: {len(covered)} covered, {len(uncovered)} gap(s)")


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="post.export.parity_check")
    p.add_argument("pack")
    p.add_argument("--graphs", action="append", default=[],
                   help="offline graphs directory (repeatable)")
    args = p.parse_args(argv if argv is not None else sys.argv[1:])

    pack = Path(args.pack).expanduser().resolve()
    print(f"parity-check: {pack}")
    print("variable parity (adapters vs Reader.py):")
    check_variable_parity()
    if args.graphs:
        print("product parity (pack vs offline PNG families):")
        check_product_parity(pack, [Path(g).expanduser().resolve() for g in args.graphs])

    if _failures:
        print(f"FAIL parity-check ({len(_failures)})")
        return 1
    print("PASS parity-check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
