#!/usr/bin/env python3
"""Audit generateGraphs temp JSON series for missing/NaN model or obs data.

Usage:
  pipenv run python audit_post_json.py path/to/temp/
  pipenv run python audit_post_json.py path/to/temp/gfs_wind_data_file.json

Walks known post JSON names (gfs/adcirc/post wind, water, obs) and reports per-station
finite counts so outside-hull NaNs / empty obs are obvious without loading graphs.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

KNOWN = [
    "gfs_wind_data_file.json",
    "adcirc_wind_data_file.json",
    "post_wind_data_file.json",
    "adcirc_water_data_file.json",
    "obs_wind_data_file.json",
    "obs_water_data_file.json",
    "gfs_rain_data_file.json",
]

# field candidates by file family
SERIES_KEYS = (
    ("windsX", "windsY"),
    ("speeds", "directions"),
    ("water",),
    ("speeds",),
    ("rain",),
    ("zeta",),
)


def _load_stations(stations_path: Path | None) -> dict:
    if stations_path and stations_path.is_file():
        with open(stations_path) as f:
            return json.load(f).get("NOS", {})
    return {}


def _series_arrays(rec: dict) -> list[tuple[str, np.ndarray]]:
    out = []
    for keys in SERIES_KEYS:
        if all(k in rec for k in keys):
            for k in keys:
                out.append((k, np.asarray(rec[k], dtype=float)))
            return out
    # fallback: any list/array numeric field except times
    for k, v in rec.items():
        if k in ("times", "nodeIndex", "latitude", "longitude", "closestNodes"):
            continue
        if isinstance(v, (list, tuple)) and v and isinstance(v[0], (int, float)):
            out.append((k, np.asarray(v, dtype=float)))
    return out


def audit_file(path: Path, stations: dict) -> int:
    """Return number of problem stations (all-NaN or empty)."""
    with open(path) as f:
        data = json.load(f)
    print(f"\n=== {path.name} ({path.stat().st_size // 1024} KiB) ===")
    keys = [k for k in data if k != "map_data"]
    if not keys:
        print("  (no station keys)")
        return 0
    problems = 0
    for sk in sorted(keys, key=lambda x: int(x) if str(x).isdigit() else 0):
        rec = data[sk]
        name = stations.get(str(sk), stations.get(sk, {})).get("name", "?")
        times = rec.get("times") or []
        series = _series_arrays(rec)
        if not series:
            print(f"  key={sk} {name}: n_times={len(times)} NO series fields")
            problems += 1
            continue
        parts = []
        all_bad = True
        for field, arr in series:
            n = arr.size
            n_fin = int(np.isfinite(arr).sum()) if n else 0
            n_nan = int(np.isnan(arr).sum()) if n else 0
            if n_fin:
                all_bad = False
                parts.append(
                    f"{field}: finite={n_fin}/{n} min={np.nanmin(arr):.3g} max={np.nanmax(arr):.3g}"
                )
            else:
                parts.append(f"{field}: ALL_NAN_OR_EMPTY n={n} nan={n_nan}")
        flag = " ** PROBLEM" if all_bad else ""
        if all_bad:
            problems += 1
        print(f"  key={sk} {name}: n_times={len(times)}; " + "; ".join(parts) + flag)
        if "nodeIndex" in rec:
            print(f"    nodeIndex={rec.get('nodeIndex')} lat={rec.get('latitude')} lon={rec.get('longitude')}")
    if "map_data" in data:
        print(f"  map_data present keys={list(data['map_data'].keys())}")
    print(f"  summary: {len(keys)} stations, {problems} problem(s)")
    return problems


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("path", type=Path, help="temp/ dir or a single JSON file")
    p.add_argument(
        "--stations",
        type=Path,
        default=Path("OBS_STATIONS.json"),
        help="stations JSON for names (default OBS_STATIONS.json)",
    )
    args = p.parse_args()
    stations = _load_stations(args.stations)
    target = args.path.expanduser()
    files: list[Path] = []
    if target.is_file():
        files = [target]
    elif target.is_dir():
        for name in KNOWN:
            f = target / name
            if f.is_file():
                files.append(f)
        # also pick up any other *data_file*.json
        for f in sorted(target.glob("*data_file*.json")):
            if f not in files:
                files.append(f)
    else:
        print(f"path not found: {target}", file=sys.stderr)
        return 2
    if not files:
        print(f"no post JSON found under {target}", file=sys.stderr)
        return 2
    total = 0
    for f in files:
        total += audit_file(f, stations)
    print(f"\nTOTAL problem station-records: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
