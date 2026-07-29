"""ORDER 9 wind bridge — SHiELD / FV3 surface winds → ADCIRC met forcing.

One system writes the wind and the pressure; the other writes the water that
hits the coast. This is the seam.

    python -m post.export.wind_bridge \
      --shield ~/projects/SHiELD_OPS/runs/<run>/history/atmos_sos.nest02.tile7.nc \
      --grid   ~/projects/SHiELD_OPS/ic/global_nest_Ida/grid_spec.nest02.tile7.nc \
      --out    <case>/met_shield --stem shield_nest

Writes an Oceanweather **WIN/PRE** pair plus the `fort.22` pointer and
`Wind_Inp.txt`, byte-compatible with what MetGet produces for `NWS=6` — the
same files `run-adcirc` already feeds ADCIRC.

What it reads
-------------
`atmos_sos.nest02.tile7.nc` carries exactly what ADCIRC needs at the surface:

| SHiELD variable | Role | Units |
|-----------------|------|-------|
| `UGRD10m` | 10 m eastward wind | m/s |
| `VGRD10m` | 10 m northward wind | m/s |
| `PRMSL` | sea-level pressure | **mb** (converted to mb in OWI, Pa in fort.22) |

Coordinates come from `grid_spec…nc` (`grid_lont` / `grid_latt`) — the run's
own nest geometry, never synthesised.

The one approximation, stated plainly
-------------------------------------
The SHiELD nest is **curvilinear**; OWI requires a regular lat/lon grid. This
tool therefore resamples the nest onto a regular grid whose spacing matches the
nest's median spacing (or `--dx`/`--dy` if given), by nearest-neighbour lookup
over the nest cells. That is a real interpolation and it is recorded in the
output manifest. It is the same class of step `fregrid` performs in the
atmospheric post — it is not a fabrication, but it is not free either: cells
outside the nest footprint are written as calm (0 m/s) and background pressure
(1013 mb), exactly as MetGet pads its domains.

NWS numbering, settled
----------------------
`NWS = 6` is the gridded met format used here. The waves golden ran `NWS = 306`.
Those are **the same met format**: ADCIRC's 300-series prefix means "coupled to
SWAN", and the trailing digits are the met type. So a run that adds waves keeps
this exact wind bridge and only changes the fort.15 NWS value 6 → 306. No
second met product is needed for waves.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

#: OWI writes 8 values per line at %10.4f
OWI_PER_LINE = 8
BACKGROUND_MB = 1013.0


def _parse_time_units(units: str) -> Tuple[datetime, float]:
    """(epoch, seconds-per-unit) from a CF 'X since Y' string."""
    from Reader import Reader

    base = Reader()._parseColdStartDate(units)
    head = units.strip().split()[0].lower()
    scale = {
        "seconds": 1.0, "second": 1.0,
        "minutes": 60.0, "minute": 60.0,
        "hours": 3600.0, "hour": 3600.0,
        "days": 86400.0, "day": 86400.0,
    }.get(head)
    if scale is None:
        raise ValueError(f"unsupported time units: {units!r}")
    return base, scale


def load_shield_surface(
    shield_nc: Path, grid_nc: Optional[Path]
) -> Dict[str, Any]:
    """Read 10 m winds, MSLP and the nest lon/lat from a SHiELD surface file."""
    import netCDF4 as nc

    ds = nc.Dataset(str(shield_nc))
    for v in ("UGRD10m", "VGRD10m", "PRMSL"):
        if v not in ds.variables:
            raise KeyError(
                f"{shield_nc.name} has no {v} — this bridge needs the surface "
                "(atmos_sos) history file, not the 3-D one"
            )
    u = np.asarray(ds.variables["UGRD10m"][:], dtype=np.float64)
    v = np.asarray(ds.variables["VGRD10m"][:], dtype=np.float64)
    p = np.asarray(ds.variables["PRMSL"][:], dtype=np.float64)
    p_units = str(getattr(ds.variables["PRMSL"], "units", "")).lower()
    base, scale = _parse_time_units(ds.variables["time"].units)
    tvals = np.asarray(ds.variables["time"][:], dtype=float)
    times = [base + timedelta(seconds=float(t) * scale) for t in tvals]
    ds.close()

    if p_units.startswith("pa") or np.nanmean(p) > 5000:
        p = p / 100.0  # the permanent PRMSL trap, in the direction ADCIRC cares about
        p_units = "mb"
    if not (800 < float(np.nanmean(p)) < 1200):
        raise ValueError(
            f"PRMSL mean {np.nanmean(p):.1f} is outside the mb band — refusing to "
            "write met forcing with suspect pressure units"
        )

    lon = lat = None
    if grid_nc is not None and Path(grid_nc).exists():
        g = nc.Dataset(str(grid_nc))
        for lo, la in (("grid_lont", "grid_latt"), ("lon", "lat")):
            if lo in g.variables and la in g.variables:
                lon = np.asarray(g.variables[lo][:], dtype=np.float64)
                lat = np.asarray(g.variables[la][:], dtype=np.float64)
                break
        g.close()
    if lon is None:
        raise FileNotFoundError(
            "no grid_spec with grid_lont/grid_latt — the nest lon/lat must come "
            "from the run's own grid file; this tool will not invent coordinates"
        )
    lon = np.where(lon > 180.0, lon - 360.0, lon)
    if lon.shape != u.shape[1:]:
        raise ValueError(
            f"grid {lon.shape} does not match field {u.shape[1:]} — wrong grid_spec?"
        )
    return {"u": u, "v": v, "p": p, "lon": lon, "lat": lat, "times": times}


def build_regular_grid(
    lon: np.ndarray, lat: np.ndarray, dx: Optional[float], dy: Optional[float]
) -> Tuple[np.ndarray, np.ndarray]:
    """Regular lat/lon target grid covering the nest at its own median spacing."""
    if dx is None:
        dx = float(np.median(np.abs(np.diff(lon, axis=1))))
    if dy is None:
        dy = float(np.median(np.abs(np.diff(lat, axis=0))))
    dx = round(dx, 4)
    dy = round(dy, 4)
    lon_min, lon_max = float(lon.min()), float(lon.max())
    lat_min, lat_max = float(lat.min()), float(lat.max())
    nx = int(np.floor((lon_max - lon_min) / dx)) + 1
    ny = int(np.floor((lat_max - lat_min) / dy)) + 1
    return (
        lon_min + dx * np.arange(nx),
        lat_min + dy * np.arange(ny),
    )


def resample_to_regular(
    field: np.ndarray, lon: np.ndarray, lat: np.ndarray,
    tgt_lon: np.ndarray, tgt_lat: np.ndarray, fill: float
) -> np.ndarray:
    """Nearest-cell resample of a curvilinear field onto a regular grid."""
    from scipy.spatial import cKDTree

    src = np.column_stack([lon.ravel(), lat.ravel()])
    tree = cKDTree(src)
    gx, gy = np.meshgrid(tgt_lon, tgt_lat)
    dist, idx = tree.query(np.column_stack([gx.ravel(), gy.ravel()]), k=1)
    # anything farther than ~2 source cells is outside the nest footprint
    cell = float(np.median(np.abs(np.diff(lon, axis=1))))
    outside = dist > 2.0 * cell
    n_t = field.shape[0]
    out = np.empty((n_t, tgt_lat.size, tgt_lon.size), dtype=np.float64)
    for t in range(n_t):
        flat = field[t].ravel()[idx]
        flat[outside] = fill
        out[t] = flat.reshape(tgt_lat.size, tgt_lon.size)
    return out, int(outside.sum()), int(outside.size)


def _owi_block(values: np.ndarray) -> List[str]:
    flat = values.ravel(order="C")
    lines = []
    for i in range(0, flat.size, OWI_PER_LINE):
        chunk = flat[i:i + OWI_PER_LINE]
        lines.append("".join(f"{v:10.4f}" for v in chunk))
    return lines


def _owi_header(times: List[datetime]) -> str:
    return (
        "Oceanweather WIN/PRE Format"
        + " " * 28
        + times[0].strftime("%Y%m%d%H")
        + "     "
        + times[-1].strftime("%Y%m%d%H")
    )


def _snap_header(ny: int, nx: int, dx: float, dy: float,
                 sw_lat: float, sw_lon: float, when: datetime) -> str:
    return (
        f"iLat={ny:4d}iLong={nx:4d}"
        f"DX={dx:6.4f}DY={dy:6.4f}"
        f"SWLat={sw_lat:8.5f}SWLon={sw_lon:8.4f}"
        f"DT={when.strftime('%Y%m%d%H%M')}"
    )


def write_owi(
    out_dir: Path, stem: str, tgt_lon: np.ndarray, tgt_lat: np.ndarray,
    u: np.ndarray, v: np.ndarray, p_mb: np.ndarray, times: List[datetime]
) -> Dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    dx = float(round(tgt_lon[1] - tgt_lon[0], 4))
    dy = float(round(tgt_lat[1] - tgt_lat[0], 4))
    ny, nx = tgt_lat.size, tgt_lon.size
    head = _owi_header(times)

    win = out_dir / f"{stem}.wnd"
    pre = out_dir / f"{stem}.pre"
    with open(win, "w") as fw, open(pre, "w") as fp:
        fw.write(head + "\n")
        fp.write(head + "\n")
        for t, when in enumerate(times):
            snap = _snap_header(ny, nx, dx, dy, float(tgt_lat[0]), float(tgt_lon[0]), when)
            fw.write(snap + "\n")
            for line in _owi_block(u[t]):
                fw.write(line + "\n")
            for line in _owi_block(v[t]):
                fw.write(line + "\n")
            fp.write(snap + "\n")
            for line in _owi_block(p_mb[t]):
                fp.write(line + "\n")
    return {"win": win, "pre": pre}


def write_wind_inp(
    out_dir: Path, stem: str, tgt_lon: np.ndarray, tgt_lat: np.ndarray,
    times: List[datetime]
) -> Path:
    """`fort.22Wind_Inp.txt` in the same shape run-adcirc already writes."""
    dt_h = (times[1] - times[0]).total_seconds() / 3600.0 if len(times) > 1 else 1.0
    path = out_dir / f"{stem}_Wind_Inp.txt"
    path.write_text(
        "shield\n"
        "3\n"
        f"{times[0].strftime('%Y %m %d %H %M %S')}\n"
        f"{dt_h:.1f}\n"
        f"{len(times)}\n"
        f"{tgt_lon[0]:.4f} {tgt_lon[-1]:.4f}\n"
        f"{tgt_lat[0]:.4f} {tgt_lat[-1]:.4f}\n"
        "10.\n",
        encoding="utf-8",
    )
    return path


def write_fort22(
    out_dir: Path, u: np.ndarray, v: np.ndarray, p_mb: np.ndarray,
    tgt_lon: np.ndarray, tgt_lat: np.ndarray, times: List[datetime]
) -> Dict[str, Path]:
    """NWS=6 `fort.22` (u, v, p-in-Pa per grid point per snap) + `.meta`."""
    out_dir.mkdir(parents=True, exist_ok=True)
    f22 = out_dir / "fort.22"
    with open(f22, "w") as fh:
        for t in range(len(times)):
            ut, vt, pt = u[t].ravel(), v[t].ravel(), p_mb[t].ravel() * 100.0
            for i in range(ut.size):
                fh.write(f"{ut[i]:6.1f} {vt[i]:6.1f} {pt[i]:6.0f}\n")
    dt_s = (times[1] - times[0]).total_seconds() if len(times) > 1 else 3600.0
    meta = out_dir / "fort.22.meta"
    meta.write_text(
        f" {tgt_lat.size:d}  {tgt_lon.size:d}  {tgt_lat[-1]:.1f}  "
        f"{tgt_lon[0]:.1f} {abs(tgt_lon[1] - tgt_lon[0]):.6f} "
        f"{abs(tgt_lat[1] - tgt_lat[0]):.6f} {dt_s:.1f}\n",
        encoding="utf-8",
    )
    return {"fort22": f22, "meta": meta}


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="post.export.wind_bridge")
    p.add_argument("--shield", required=True, help="atmos_sos.nest*.tile*.nc")
    p.add_argument("--grid", help="grid_spec.nest*.tile*.nc (grid_lont/grid_latt)")
    p.add_argument("--out", required=True, help="output directory")
    p.add_argument("--stem", default="shield_nest", help="OWI file stem")
    p.add_argument("--dx", type=float, help="target grid spacing, degrees lon")
    p.add_argument("--dy", type=float, help="target grid spacing, degrees lat")
    p.add_argument("--format", default="owi", choices=("owi", "fort22", "both"))
    p.add_argument("--nws", type=int, default=6,
                   help="NWS value to record (6 met-only; 306 = same met + SWAN)")
    args = p.parse_args(argv if argv is not None else sys.argv[1:])

    shield = Path(args.shield).expanduser().resolve()
    grid = Path(args.grid).expanduser().resolve() if args.grid else None
    out = Path(args.out).expanduser().resolve()

    print(f"wind bridge: {shield.name} → {out}")
    src = load_shield_surface(shield, grid)
    print(f"  source: {len(src['times'])} times, nest {src['lon'].shape}, "
          f"{src['times'][0]:%Y-%m-%dT%H:%MZ} … {src['times'][-1]:%Y-%m-%dT%H:%MZ}")

    tgt_lon, tgt_lat = build_regular_grid(src["lon"], src["lat"], args.dx, args.dy)
    print(f"  target: regular {tgt_lat.size}×{tgt_lon.size} "
          f"dx={tgt_lon[1] - tgt_lon[0]:.4f} dy={tgt_lat[1] - tgt_lat[0]:.4f} "
          f"[{tgt_lon[0]:.3f},{tgt_lon[-1]:.3f}] × [{tgt_lat[0]:.3f},{tgt_lat[-1]:.3f}]")

    u, n_out, n_tot = resample_to_regular(
        src["u"], src["lon"], src["lat"], tgt_lon, tgt_lat, 0.0)
    v, _, _ = resample_to_regular(
        src["v"], src["lon"], src["lat"], tgt_lon, tgt_lat, 0.0)
    p_mb, _, _ = resample_to_regular(
        src["p"], src["lon"], src["lat"], tgt_lon, tgt_lat, BACKGROUND_MB)
    pct = 100.0 * n_out / max(1, n_tot)
    print(f"  resample: nearest-cell; {n_out}/{n_tot} target cells "
          f"({pct:.1f}%) outside the nest → calm / {BACKGROUND_MB:.0f} mb padding")

    written: Dict[str, Path] = {}
    if args.format in ("owi", "both"):
        written.update(write_owi(out, args.stem, tgt_lon, tgt_lat, u, v, p_mb, src["times"]))
        written["wind_inp"] = write_wind_inp(out, args.stem, tgt_lon, tgt_lat, src["times"])
    if args.format in ("fort22", "both"):
        written.update(write_fort22(out, u, v, p_mb, tgt_lon, tgt_lat, src["times"]))

    manifest = {
        "bridge": "shield_fv3_to_adcirc",
        "source": str(shield),
        "grid_spec": str(grid) if grid else None,
        "nws": args.nws,
        "nws_note": (
            "NWS=6 is met-only; NWS=306 is the *same* met format with SWAN "
            "coupling (ADCIRC's 300-series prefix). Switching a run to waves "
            "does not change these files."
        ),
        "variables": {"u": "UGRD10m", "v": "VGRD10m", "p": "PRMSL"},
        "units": {"u": "m/s", "v": "m/s", "p_owi": "mb", "p_fort22": "Pa"},
        "times_utc": [t.strftime("%Y-%m-%dT%H:%M:%SZ") for t in src["times"]],
        "target_grid": {
            "nx": int(tgt_lon.size), "ny": int(tgt_lat.size),
            "dx": float(tgt_lon[1] - tgt_lon[0]), "dy": float(tgt_lat[1] - tgt_lat[0]),
            "lon_range": [float(tgt_lon[0]), float(tgt_lon[-1])],
            "lat_range": [float(tgt_lat[0]), float(tgt_lat[-1])],
        },
        "resampling": {
            "method": "nearest source cell (curvilinear nest → regular lat/lon)",
            "cells_outside_nest": n_out,
            "cells_total": n_tot,
            "fill_outside": {"wind": 0.0, "pressure_mb": BACKGROUND_MB},
        },
        "files": {k: str(v) for k, v in written.items()},
    }
    (out / "wind_bridge_manifest.json").write_text(
        json.dumps(manifest, indent=1), encoding="utf-8"
    )
    for k, v in written.items():
        print(f"  wrote {k}: {v.name} ({v.stat().st_size / 1e6:.1f} MB)")
    print(f"  wrote manifest: wind_bridge_manifest.json")
    print(f"  fort.15: set NWS = {args.nws}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
