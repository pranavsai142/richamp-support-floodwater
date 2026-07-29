"""G-PACK — Python-side verification of an adcirc-fieldpack/v0 directory.

Structural checks always run. With ``--source-check`` the pack is additionally
cross-examined against the *original* fort.14 / fort.63.nc it claims to come
from: node and triangle counts, node coordinates, and a random sample of ζ
values must agree with the raw model output (within float16 tolerance).

    python -m post.export.verify_pack <pack> [--source-check] [--rundir …] [--mesh …]

Exit 0 pass, 1 fail.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

SCHEMA = "adcirc-fieldpack/v0"
DTYPES = {"float16": "<f2", "float32": "<f4", "uint32": "<u4", "uint8": "<u1"}

_failures: List[str] = []


def ok(msg: str) -> None:
    print(f"  ok: {msg}")


def bad(msg: str) -> None:
    _failures.append(msg)
    print(f"  FAIL: {msg}")


def _load(pack: Path, rel: str, dtype: str) -> np.ndarray:
    return np.fromfile(pack / rel, dtype=np.dtype(DTYPES[dtype]))


def verify_structure(pack: Path, meta: Dict[str, Any]) -> None:
    if meta.get("schema") != SCHEMA:
        bad(f"schema {meta.get('schema')!r} != {SCHEMA!r}")
        return
    ok(f"schema {meta['schema']}")

    mesh = meta.get("mesh")
    if not mesh:
        bad("meta.mesh missing")
        return
    n_nodes, n_tri = int(mesh["n_nodes"]), int(mesh["n_triangles"])

    nodes = _load(pack, mesh["paths"]["nodes"]["path"], "float32")
    if nodes.size != n_nodes * 3:
        bad(f"nodes length {nodes.size} != n_nodes*3 {n_nodes * 3}")
    else:
        nodes = nodes.reshape(n_nodes, 3)
        if not np.isfinite(nodes[:, :2]).all():
            bad("non-finite mesh lon/lat")
        else:
            ok(f"mesh nodes {n_nodes} finite lon/lat")
        lon, lat = nodes[:, 0], nodes[:, 1]
        if lon.min() < -180.001 or lon.max() > 180.001:
            bad(f"lon outside [-180,180]: [{lon.min()}, {lon.max()}]")
        if lat.min() < -90.001 or lat.max() > 90.001:
            bad(f"lat outside [-90,90]: [{lat.min()}, {lat.max()}]")
        else:
            ok(f"lon/lat ranges [{lon.min():.4f},{lon.max():.4f}] [{lat.min():.4f},{lat.max():.4f}]")

    tris = _load(pack, mesh["paths"]["triangles"]["path"], "uint32")
    if tris.size != n_tri * 3:
        bad(f"triangles length {tris.size} != n_triangles*3 {n_tri * 3}")
    else:
        if tris.max() >= n_nodes:
            bad(f"triangle index {tris.max()} >= n_nodes {n_nodes}")
        else:
            ok(f"mesh triangles {n_tri} indices in range (0-based)")

    streams = meta.get("time_streams") or {}
    if not streams:
        bad("no time_streams")
    for sid, s in streams.items():
        times = s.get("times_utc") or []
        if len(times) != int(s.get("n", -1)):
            bad(f"stream {sid}: n={s.get('n')} but {len(times)} times")
        elif not times:
            bad(f"stream {sid}: empty times_utc")
        else:
            ok(f"stream {sid}: {len(times)} times {times[0]} … {times[-1]}")

    fields = meta.get("fields") or []
    if not fields:
        bad("no fields")
    for f in fields:
        name = f.get("name")
        if f.get("role") == "vector":
            comps = f.get("components") or []
            have = {g["name"] for g in fields}
            missing = [c for c in comps if c not in have]
            if missing:
                bad(f"vector {name}: missing components {missing}")
            else:
                ok(f"vector {name} = {comps} [{f.get('units')}]")
            continue

        path = pack / f["path"]
        if not path.exists():
            bad(f"{name}: missing binary {f['path']}")
            continue
        arr = _load(pack, f["path"], f["dtype"])
        expect = 1
        for s in f["shape"]:
            expect *= int(s)
        if arr.size != expect:
            bad(f"{name}: {arr.size} values != shape product {expect} {f['shape']}")
            continue
        if f.get("endian") != "little":
            bad(f"{name}: endian {f.get('endian')!r} != little")
        dims = f.get("dims") or []
        if "node" in dims:
            axis = dims.index("node")
            if int(f["shape"][axis]) != n_nodes:
                bad(f"{name}: node axis {f['shape'][axis]} != mesh n_nodes {n_nodes}")
        stream = f.get("stream")
        if "time" in dims:
            axis = dims.index("time")
            n_t = int(f["shape"][axis])
            if stream not in streams:
                bad(f"{name}: declares time but stream {stream!r} not in time_streams")
            elif int(streams[stream]["n"]) != n_t:
                bad(f"{name}: time axis {n_t} != stream {stream} n={streams[stream]['n']}")
        if not f.get("units"):
            bad(f"{name}: no units")

        finite = np.isfinite(arr)
        n_fin = int(finite.sum())
        if n_fin == 0:
            bad(f"{name}: zero finite values")
            continue
        mn, mx = float(arr[finite].min()), float(arr[finite].max())
        for key, val in (("min", mn), ("max", mx)):
            declared = f.get(key)
            if declared is None:
                bad(f"{name}: meta {key} missing")
            elif not math.isclose(float(declared), val, rel_tol=1e-6, abs_tol=1e-6):
                bad(f"{name}: meta {key}={declared} but data {key}={val}")
        ok(
            f"{name} {f['dtype']} {f['shape']} {f['units']} "
            f"[{mn:.4g}, {mx:.4g}] finite {n_fin}/{arr.size}"
        )

    if meta.get("modes", {}).get("runup"):
        bad("modes.runup is true — runup is out of scope for this ladder")


def verify_against_source(pack: Path, meta: Dict[str, Any], rundir: Path, mesh_file: Path) -> None:
    """The real fidelity gate: pack values must equal the model output."""
    import netCDF4 as nc

    print("source cross-check:")
    mesh = meta["mesh"]
    n_nodes, n_tri = int(mesh["n_nodes"]), int(mesh["n_triangles"])

    with open(mesh_file) as fh:
        fh.readline()
        ne, np_ = (int(x) for x in fh.readline().split()[:2])
    if (np_, ne) != (n_nodes, n_tri):
        bad(f"fort.14 says {np_} nodes / {ne} elements; pack says {n_nodes} / {n_tri}")
    else:
        ok(f"fort.14 counts match: {np_} nodes / {ne} elements")

    nodes = _load(pack, mesh["paths"]["nodes"]["path"], "float32").reshape(n_nodes, 3)
    water = rundir / "fort.63.nc"
    if not water.exists():
        bad(f"no fort.63.nc under {rundir} for source check")
        return
    ds = nc.Dataset(str(water))
    x = np.asarray(ds.variables["x"][:], dtype=np.float64)
    y = np.asarray(ds.variables["y"][:], dtype=np.float64)
    if x.size != n_nodes:
        bad(f"fort.63 node count {x.size} != pack {n_nodes}")
    else:
        dlon = float(np.max(np.abs(x - nodes[:, 0])))
        dlat = float(np.max(np.abs(y - nodes[:, 1])))
        # float32 storage of ~-94.4 deg → ~7.6e-6 deg quantum
        if dlon > 1e-4 or dlat > 1e-4:
            bad(f"node coords differ from fort.63: max dlon={dlon:.2e} dlat={dlat:.2e}")
        else:
            ok(f"node coords match fort.63 (max dlon={dlon:.2e}, dlat={dlat:.2e} deg)")

    row = next((f for f in meta["fields"] if f["name"] == "water_zeta"), None)
    if row is None:
        ok("no water_zeta in pack — skipping ζ sample check")
        ds.close()
        return
    n_t = int(row["shape"][0])
    if len(ds.dimensions["time"]) != n_t:
        bad(f"fort.63 has {len(ds.dimensions['time'])} times; pack water_zeta has {n_t}")
    zeta_pack = _load(pack, row["path"], row["dtype"]).reshape(n_t, n_nodes)

    rng = np.random.default_rng(20260725)
    n_bad = 0
    worst = 0.0
    for ti in rng.integers(0, n_t, size=min(8, n_t)):
        raw = np.ma.asarray(ds.variables["zeta"][int(ti), :]).astype(np.float64).filled(np.nan)
        got = zeta_pack[int(ti), :].astype(np.float64)
        both = np.isfinite(raw) & np.isfinite(got)
        if int(both.sum()) == 0:
            bad(f"t={ti}: no jointly finite ζ values")
            continue
        # float16 relative precision is 2^-11
        tol = np.maximum(np.abs(raw[both]) * 2.0 ** -10, 1e-3)
        diff = np.abs(raw[both] - got[both])
        n_off = int((diff > tol).sum())
        worst = max(worst, float(diff.max()))
        dry_raw = int((~np.isfinite(raw)).sum())
        dry_pack = int((~np.isfinite(got)).sum())
        if dry_raw != dry_pack:
            bad(f"t={ti}: dry-node count {dry_pack} in pack != {dry_raw} in fort.63")
        if n_off:
            bad(f"t={ti}: {n_off} ζ values beyond float16 tolerance")
            n_bad += 1
    if n_bad == 0:
        ok(f"ζ samples match fort.63 within float16 tolerance (worst |Δ| = {worst:.2e} m)")
    ds.close()


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="post.export.verify_pack")
    p.add_argument("pack")
    p.add_argument("--source-check", action="store_true")
    p.add_argument("--rundir")
    p.add_argument("--mesh")
    args = p.parse_args(argv if argv is not None else sys.argv[1:])

    pack = Path(args.pack).expanduser().resolve()
    print(f"verify-pack: {pack}")
    try:
        meta = json.loads((pack / "meta.json").read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"  FAIL: meta.json: {e}")
        return 1

    verify_structure(pack, meta)

    if args.source_check:
        rundir = Path(args.rundir).expanduser().resolve() if args.rundir else None
        mesh_file = Path(args.mesh).expanduser().resolve() if args.mesh else None
        if rundir is None or mesh_file is None:
            bad("--source-check needs --rundir and --mesh")
        else:
            verify_against_source(pack, meta, rundir, mesh_file)

    if _failures:
        print(f"FAIL verify-pack ({len(_failures)} problem(s))")
        return 1
    print("PASS verify-pack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
