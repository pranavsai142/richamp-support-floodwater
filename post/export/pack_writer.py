"""adcirc-fieldpack/v0 writer — binary law shared with the atmospheric twin.

Binary law (identical to `gfdl-fieldpack/v0`):
  * fields  : float16 little-endian, row-major (C order)
  * coords  : float32 little-endian
  * indices : uint32 little-endian
  * meta.json field rows carry {name, units, dims, shape, path, dtype, endian,
    role, min, max, source}

Divergence from the twin, deliberate and load-bearing
-----------------------------------------------------
The twin maps NaN/Inf -> 0 on write. **Coastal packs must not do that.**
An ADCIRC dry node is not "0.0 m of water"; painting it zero is a science lie
that would show a flat wet sheet over dry land. Coastal fields therefore
default to ``nan_policy="preserve"``: dry / masked nodes are written as float16
NaN and the renderer is required to treat NaN as "dry / no data".

float16 range note
------------------
zeta in metres lives in roughly -5..+10; float16 spacing at 4 m is ~0.004 m
(4 mm) and the format saturates at 65504, so no coastal scalar in these packs
can overflow. Wave periods (s), SWH (m), wind (m/s), rain (mm/h) are all well
inside range. Radiation stress gradients (m^2/s^2) are small. If a future
product needs more than ~3 significant digits, declare ``dtype="float32"``
on that field row rather than silently losing precision.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np

SCHEMA = "adcirc-fieldpack/v0"
GRID_TYPE_UNSTRUCTURED = "adcirc_unstructured"
GRID_TYPE_REGULAR = "regular_latlon"

#: dtype tokens accepted in meta field rows -> numpy little-endian dtype
DTYPES = {
    "float16": np.dtype("<f2"),
    "float32": np.dtype("<f4"),
    "uint32": np.dtype("<u4"),
    "uint8": np.dtype("<u1"),
}

#: file-name suffix per dtype token (mirrors twin `*.f16.bin` / `*.f32.bin`)
SUFFIX = {
    "float16": "f16.bin",
    "float32": "f32.bin",
    "uint32": "u32.bin",
    "uint8": "u8.bin",
}


class PackWriteError(RuntimeError):
    """Raised when a pack cannot be written (exit code 3 at the CLI)."""


def _as_float_array(values: Any) -> np.ndarray:
    """Materialise a (possibly masked) netCDF variable as float64 with NaN fill."""
    arr = np.ma.asarray(values)
    if np.ma.isMaskedArray(arr):
        out = arr.astype(np.float64).filled(np.nan)
    else:
        out = np.asarray(arr, dtype=np.float64)
    return out


def sanitize(
    arr: np.ndarray,
    nan_policy: str = "preserve",
    fill_values: Sequence[float] = (-99999.0,),
    fill_atol: float = 1e-3,
) -> np.ndarray:
    """Normalise sentinel fills to NaN and apply the pack's NaN policy.

    ADCIRC writes ``_FillValue = -99999.0`` for dry nodes; netCDF4 usually
    masks it, but partially-decoded arrays can leak the raw sentinel. Any value
    within ``fill_atol`` of a listed fill becomes NaN before the policy runs.

    nan_policy:
      ``preserve`` (default, coastal law) — NaN stays NaN (= dry / no data)
      ``zero``                            — twin behaviour, NaN/Inf -> 0
    """
    out = np.asarray(arr, dtype=np.float64).copy()
    for fv in fill_values:
        out[np.isclose(out, fv, atol=fill_atol, rtol=0.0)] = np.nan
    if nan_policy == "zero":
        out[~np.isfinite(out)] = 0.0
    elif nan_policy == "preserve":
        out[np.isinf(out)] = np.nan
    else:
        raise PackWriteError(f"unknown nan_policy: {nan_policy!r}")
    return out


def finite_min_max(arr: np.ndarray) -> tuple[Optional[float], Optional[float]]:
    """Min/max over finite entries only; (None, None) if nothing is finite."""
    finite = np.isfinite(arr)
    if not finite.any():
        return (None, None)
    return (float(np.min(arr[finite])), float(np.max(arr[finite])))


class PackWriter:
    """Assembles one ``adcirc-fieldpack/v0`` directory.

    Usage::

        pw = PackWriter(outdir, run_id="ec95d_gfs_5d_2026072512")
        pw.set_mesh(lon, lat, elev, triangles, source="forecast/fort.14")
        pw.add_time_stream("adcirc", times_utc, source="forecast/fort.63.nc")
        pw.add_field("water_zeta", data, dims=["time", "node"], units="m", ...)
        pw.write()
    """

    def __init__(
        self,
        outdir: os.PathLike | str,
        run_id: str,
        grid_type: str = GRID_TYPE_UNSTRUCTURED,
        crs: str = "EPSG:4326",
        vertical_datum: str = "model_native",
        vertical_datum_note: str = (
            "ADCIRC native vertical datum (mesh datum, typically NAVD88 for RI "
            "meshes); CO-OPS obs are pulled at MSL — label both, do not silently "
            "shift one onto the other"
        ),
    ) -> None:
        self.outdir = Path(outdir)
        self.run_id = run_id
        self.grid_type = grid_type
        self.meta: Dict[str, Any] = {
            "schema": SCHEMA,
            "run_id": run_id,
            "grid_type": grid_type,
            "crs": crs,
            "vertical_datum": vertical_datum,
            "vertical_datum_note": vertical_datum_note,
            "dims": {},
            "times_utc": [],
            "time_streams": {},
            "fields": [],
            "grids": {},
            "provenance": {
                "exporter": "post.export.cli",
                "source_files": [],
            },
            "fidelity": {},
        }
        self._n_nodes: Optional[int] = None
        self._default_stream: Optional[str] = None

    # ------------------------------------------------------------------ paths
    def _abs(self, rel: str) -> Path:
        p = self.outdir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    # ------------------------------------------------------------- raw writers
    def _write_bin(self, rel: str, arr: np.ndarray, dtype_token: str) -> int:
        dt = DTYPES[dtype_token]
        buf = np.ascontiguousarray(arr, dtype=dt)
        path = self._abs(rel)
        with open(path, "wb") as fh:
            fh.write(buf.tobytes(order="C"))
        return int(buf.nbytes)

    # ------------------------------------------------------------------- mesh
    def set_mesh(
        self,
        lon: Sequence[float],
        lat: Sequence[float],
        elev_m: Sequence[float],
        triangles: Sequence[Sequence[int]],
        source: str = "fort.14",
        mesh_name: Optional[str] = None,
    ) -> None:
        """Write the real fort.14 geometry. Never synthesise these coordinates."""
        lon_a = np.asarray(lon, dtype=np.float64)
        lat_a = np.asarray(lat, dtype=np.float64)
        elev_a = np.asarray(elev_m, dtype=np.float64)
        tri_a = np.asarray(triangles, dtype=np.int64)

        if not (lon_a.shape == lat_a.shape == elev_a.shape):
            raise PackWriteError(
                f"mesh node arrays disagree: lon{lon_a.shape} lat{lat_a.shape} elev{elev_a.shape}"
            )
        if tri_a.ndim != 2 or tri_a.shape[1] != 3:
            raise PackWriteError(f"triangles must be (M,3), got {tri_a.shape}")
        n = int(lon_a.size)
        m = int(tri_a.shape[0])
        if tri_a.min() < 0 or tri_a.max() >= n:
            raise PackWriteError(
                f"triangle indices out of range: [{tri_a.min()},{tri_a.max()}] for {n} nodes "
                "(fort.14 connectivity must be 0-based on write)"
            )
        if not np.isfinite(lon_a).all() or not np.isfinite(lat_a).all():
            raise PackWriteError("non-finite mesh lon/lat — refusing to write invented coords")

        nodes = np.empty((n, 3), dtype=np.float64)
        nodes[:, 0] = lon_a
        nodes[:, 1] = lat_a
        nodes[:, 2] = elev_a
        self._write_bin("mesh/nodes.f32.bin", nodes, "float32")
        self._write_bin("mesh/triangles.u32.bin", tri_a, "uint32")

        self._n_nodes = n
        self.meta["mesh"] = {
            "n_nodes": n,
            "n_triangles": m,
            "source": source,
            "mesh_name": mesh_name,
            "lon_range": [float(lon_a.min()), float(lon_a.max())],
            "lat_range": [float(lat_a.min()), float(lat_a.max())],
            "elev_range": [float(np.nanmin(elev_a)), float(np.nanmax(elev_a))],
            "elev_note": "elev_m = -depth from fort.14 (positive up), same as offline Grapher",
            "paths": {
                "nodes": {
                    "path": "mesh/nodes.f32.bin",
                    "dtype": "float32",
                    "endian": "little",
                    "dims": ["node", "lon_lat_elev"],
                    "shape": [n, 3],
                },
                "triangles": {
                    "path": "mesh/triangles.u32.bin",
                    "dtype": "uint32",
                    "endian": "little",
                    "dims": ["triangle", "vertex"],
                    "shape": [m, 3],
                    "note": "0-based node indices",
                },
            },
        }
        self.meta["dims"]["node"] = n
        self.meta["dims"]["triangle"] = m
        self._add_source(source)

    # ------------------------------------------------------------------ grids
    def add_grid(
        self,
        grid_id: str,
        lon: Sequence[float],
        lat: Sequence[float],
        source: str = "",
    ) -> None:
        """Register a 1-D regular lat/lon grid (GFS wind / rain, RICHAMP post)."""
        lon_a = np.asarray(lon, dtype=np.float64).ravel()
        lat_a = np.asarray(lat, dtype=np.float64).ravel()
        if not np.isfinite(lon_a).all() or not np.isfinite(lat_a).all():
            raise PackWriteError(f"grid {grid_id}: non-finite lon/lat")
        self._write_bin(f"grids/{grid_id}_lon.f32.bin", lon_a, "float32")
        self._write_bin(f"grids/{grid_id}_lat.f32.bin", lat_a, "float32")
        self.meta["grids"][grid_id] = {
            "grid_type": GRID_TYPE_REGULAR,
            "nx": int(lon_a.size),
            "ny": int(lat_a.size),
            "lon_range": [float(lon_a.min()), float(lon_a.max())],
            "lat_range": [float(lat_a.min()), float(lat_a.max())],
            "coords": {
                "lon": {
                    "path": f"grids/{grid_id}_lon.f32.bin",
                    "dtype": "float32",
                    "endian": "little",
                    "dims": ["nx"],
                    "shape": [int(lon_a.size)],
                    "units": "degrees_east",
                },
                "lat": {
                    "path": f"grids/{grid_id}_lat.f32.bin",
                    "dtype": "float32",
                    "endian": "little",
                    "dims": ["ny"],
                    "shape": [int(lat_a.size)],
                    "units": "degrees_north",
                },
            },
            "source": source,
        }
        if source:
            self._add_source(source)

    # ------------------------------------------------------------ time streams
    def add_time_stream(
        self,
        stream_id: str,
        times_utc: Sequence[str],
        source: str = "",
        make_default: bool = False,
    ) -> None:
        """Register one model clock.

        Coastal runs mix clocks exactly like the atmosphere does (hourly PRMSL
        vs ~3-hourly 3D): fort.63 may be 1-hourly while GFS met is 15-minutely
        and SWAN output is 30-minutely. Fields declare which stream they ride;
        the UI must map scrubbers per stream, never force one clock on all.
        """
        times = [str(t) for t in times_utc]
        self.meta["time_streams"][stream_id] = {
            "n": len(times),
            "times_utc": times,
            "source": source,
        }
        if make_default or self._default_stream is None:
            self._default_stream = stream_id
            self.meta["times_utc"] = times
            self.meta["dims"]["time"] = len(times)
            self.meta["default_time_stream"] = stream_id
        if source:
            self._add_source(source)

    # ----------------------------------------------------------------- fields
    def add_field(
        self,
        name: str,
        data: np.ndarray,
        dims: Sequence[str],
        units: str,
        role: str = "scalar",
        grid: str = "unstructured",
        stream: Optional[str] = None,
        long_name: str = "",
        dtype: str = "float16",
        nan_policy: str = "preserve",
        cmap_hint: Optional[str] = None,
        range_hint: Optional[Sequence[float]] = None,
        source: str = "",
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Write one field binary and append its meta row.

        ``dims`` names must match the pack's dim vocabulary:
        ``time`` · ``node`` · ``ny`` · ``nx``. Shape is recorded verbatim so
        the loader never has to guess a layout.
        """
        if dtype not in DTYPES:
            raise PackWriteError(f"{name}: unsupported dtype {dtype!r}")
        arr = sanitize(_as_float_array(data), nan_policy=nan_policy)
        if arr.ndim != len(dims):
            raise PackWriteError(
                f"{name}: data ndim {arr.ndim} != len(dims) {len(dims)} ({list(dims)})"
            )
        if "node" in dims and self._n_nodes is not None:
            axis = list(dims).index("node")
            if arr.shape[axis] != self._n_nodes:
                raise PackWriteError(
                    f"{name}: node axis {arr.shape[axis]} != mesh n_nodes {self._n_nodes}"
                )
        raw_mn, raw_mx = finite_min_max(arr)
        if dtype == "float16" and raw_mx is not None and max(abs(raw_mn or 0.0), abs(raw_mx)) > 65504.0:
            raise PackWriteError(
                f"{name}: |value| exceeds float16 range (max {raw_mx}); declare dtype='float32'"
            )
        rel = f"fields/{name}.{SUFFIX[dtype]}"
        nbytes = self._write_bin(rel, arr, dtype)
        # stats describe the bytes on disk, not the pre-cast float64 — the UI
        # colorbar reads these and must not promise precision the file lacks
        stored = np.asarray(arr, dtype=DTYPES[dtype]).astype(np.float64)
        mn, mx = finite_min_max(stored)
        n_nonfinite = int((~np.isfinite(arr)).sum())

        row: Dict[str, Any] = {
            "name": name,
            "long_name": long_name or name,
            "units": units,
            "dims": list(dims),
            "shape": [int(s) for s in arr.shape],
            "path": rel,
            "dtype": dtype,
            "endian": "little",
            "role": role,
            "grid": grid,
            # a field without a time axis rides no clock — saying otherwise
            # would let the UI scrub something that never changes
            "stream": (stream or self._default_stream) if "time" in dims else None,
            "min": mn,
            "max": mx,
            "n_nonfinite": n_nonfinite,
            "nan_means": "dry / no data" if nan_policy == "preserve" else None,
            "bytes": nbytes,
            "source": source,
        }
        if cmap_hint:
            row["cmap_hint"] = cmap_hint
        if range_hint is not None:
            row["range_hint"] = [float(range_hint[0]), float(range_hint[1])]
        if extra:
            row.update(extra)
        self.meta["fields"].append(row)
        if source:
            self._add_source(source)
        return row

    def add_vector(
        self,
        name: str,
        u_name: str,
        v_name: str,
        units: str,
        grid: str = "unstructured",
        stream: Optional[str] = None,
        convention: str = "",
        long_name: str = "",
        cmap_hint: Optional[str] = None,
        range_hint: Optional[Sequence[float]] = None,
    ) -> Dict[str, Any]:
        """Declare a vector built from two already-written component fields."""
        have = {f["name"] for f in self.meta["fields"]}
        missing = [c for c in (u_name, v_name) if c not in have]
        if missing:
            raise PackWriteError(f"vector {name}: missing components {missing}")
        row = {
            "name": name,
            "long_name": long_name or name,
            "units": units,
            "role": "vector",
            "grid": grid,
            "stream": stream or self._default_stream,
            "components": [u_name, v_name],
            "convention": convention,
        }
        if cmap_hint:
            row["cmap_hint"] = cmap_hint
        if range_hint is not None:
            row["range_hint"] = [float(range_hint[0]), float(range_hint[1])]
        self.meta["fields"].append(row)
        return row

    # --------------------------------------------------------------- stations
    def add_stations(self, catalog: Dict[str, Any], series: Dict[str, Any]) -> None:
        """Write the station catalog + per-product series JSON."""
        self._abs("stations/catalog.json").write_text(
            json.dumps(catalog, indent=1), encoding="utf-8"
        )
        paths: Dict[str, str] = {}
        for key, payload in series.items():
            rel = f"stations/series/{key}.json"
            self._abs(rel).write_text(json.dumps(payload), encoding="utf-8")
            paths[key] = rel
        self.meta["stations"] = {
            "catalog": "stations/catalog.json",
            "n": sum(len(v) for v in catalog.get("groups", {}).values()),
            "series": paths,
        }

    # ----------------------------------------------------------------- tracks
    def add_tracks(self, catalog: Dict[str, Any], items: Dict[str, Any]) -> None:
        """Write the track catalog + per-track JSON (browser-native polylines).

        ``allow_nan=False`` on purpose: a NaN literal is not JSON and would
        break the browser parse — sentinels must arrive here as ``None``.
        """
        self._abs("tracks/catalog.json").write_text(
            json.dumps(catalog, indent=1, allow_nan=False), encoding="utf-8"
        )
        paths: Dict[str, str] = {}
        for tid, payload in items.items():
            rel = f"tracks/{tid}.json"
            self._abs(rel).write_text(
                json.dumps(payload, allow_nan=False), encoding="utf-8"
            )
            paths[tid] = rel
        self.meta["tracks"] = {
            "catalog": "tracks/catalog.json",
            "items": paths,
            "n": len(paths),
        }

    # ------------------------------------------------------------------- misc
    def set_bookmarks(self, bookmarks: List[Dict[str, Any]]) -> None:
        self.meta["bookmarks"] = bookmarks

    def set_modes(self, **modes: Any) -> None:
        self.meta.setdefault("modes", {}).update(modes)

    def set_phases(self, phases: List[Dict[str, Any]]) -> None:
        self.meta["phases"] = phases

    def set_fidelity(self, **kv: Any) -> None:
        self.meta["fidelity"].update(kv)

    def _add_source(self, source: str) -> None:
        srcs = self.meta["provenance"]["source_files"]
        if source and source not in srcs:
            srcs.append(source)

    def field_names(self) -> List[str]:
        return [f["name"] for f in self.meta["fields"]]

    # ------------------------------------------------------------------ write
    def write(self) -> Path:
        """Flush meta.json. Call once, after all adapters have run."""
        self.meta.setdefault("fidelity", {}).setdefault(
            "dtype_export", "float16 LE fields; float32 LE coords/mesh; uint32 LE triangles"
        )
        self.meta["fidelity"].setdefault(
            "nan_policy",
            "NaN preserved on coastal scalars = dry / no data (never coerced to 0)",
        )
        self.meta["fidelity"].setdefault("decimation", "none — full mesh, full time")
        path = self._abs("meta.json")
        path.write_text(json.dumps(self.meta, indent=1, allow_nan=False), encoding="utf-8")
        return path
