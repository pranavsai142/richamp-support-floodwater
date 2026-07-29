"""D-SWH / D-MWD / D-MWP / D-PWP / D-RAD — SWAN wave fields on the ADCIRC mesh.

First-class multiphysics, on the same nodes as ζ. Variable names and the
period naming (`swan_TMM10` → mean period, `swan_TPS` → peak period) follow
`Reader.getValue`, which is what the offline wave product family
(`*_wave_{swh,mwd,mwp,pwp,radstress_*}.png`) was built from.

Radiation stress is a vector (`radstress_x`, `radstress_y` from `rads.64.nc`);
magnitude is derived here so the scalar layer has something to colour, and the
direction is left to the shared `atan2(-v, u)` convention in the shell.

Waves are **not** runup. Nothing here computes Holman/Stockdon, transects, or
total water level at the shoreline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..context import open_with_times
from .base import register

CHUNK = 24

#: pack field -> (default filename, netCDF variable, Reader dataType, units, long name, cmap)
SCALARS: Dict[str, Tuple[str, str, str, str, str, str]] = {
    "wave_swh": ("swan_HS.63.nc", "swan_HS", "swh", "m",
                 "significant wave height", "speed"),
    "wave_mwd": ("swan_DIR.63.nc", "swan_DIR", "mwd", "deg",
                 "mean wave direction", "phase"),
    "wave_mwp": ("swan_TMM10.63.nc", "swan_TMM10", "mwp", "s",
                 "mean wave period (TMM10)", "speed"),
    "wave_pwp": ("swan_TPS.63.nc", "swan_TPS", "pwp", "s",
                 "peak wave period (TPS)", "speed"),
}


def _read_time_node(var, n_t: int, n_node: int) -> np.ndarray:
    out = np.empty((n_t, n_node), dtype=np.float64)
    for start in range(0, n_t, CHUNK):
        stop = min(start + CHUNK, n_t)
        out[start:stop] = np.ma.asarray(var[start:stop]).astype(np.float64).filled(np.nan)
    return out


@register
class WavesSwanAdapter:
    name = "waves_swan"
    products = ("waves",)

    def _find(self, ctx, key: str, default_name: str) -> Optional[Path]:
        return ctx.resolve(key, ctx.rundir / default_name)

    def available(self, ctx) -> bool:
        return any(
            self._find(ctx, key, spec[0]) is not None
            for key, spec in SCALARS.items()
        ) or self._find(ctx, "wave_rad", "rads.64.nc") is not None

    def export(self, ctx) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        stream = None

        for name, (fname, varname, dtype_token, units, long_name, cmap) in SCALARS.items():
            path = self._find(ctx, name, fname)
            if path is None:
                continue
            print(f"  waves: {name} ← {path.name}", flush=True)
            ds, _t, times_iso = open_with_times(path, "FORT", dtype_token)
            source = ctx.rel_source(path)
            stream = self._stream_for(ctx, times_iso, source)
            var = ds.variables[varname]
            n_t, n_node = int(var.shape[0]), int(var.shape[1])
            data = _read_time_node(var, n_t, n_node)
            file_units = str(getattr(var, "units", units)) or units
            ds.close()
            rows.append(ctx.writer.add_field(
                name, data, dims=["time", "node"], units=file_units, role="scalar",
                grid="unstructured", stream=stream, long_name=long_name,
                cmap_hint=cmap,
                range_hint=[0.0, 360.0] if name == "wave_mwd" else None,
                source=source,
            ))
            if name == "wave_swh":
                with np.errstate(invalid="ignore"):
                    wet = np.isfinite(data).any(axis=0)
                    swath = np.full(n_node, np.nan)
                    swath[wet] = np.nanmax(data[:, wet], axis=0)
                row = ctx.writer.add_field(
                    "wave_swh_max", swath, dims=["node"], units=file_units,
                    role="scalar", grid="unstructured", stream=None,
                    long_name="peak significant wave height over the run",
                    cmap_hint="speed", source=source,
                )
                row["static"] = True
                row["derivation"] = "max over time (Grapher swath semantic)"
                rows.append(row)

        rad = self._find(ctx, "wave_rad", "rads.64.nc")
        if rad is not None:
            print(f"  waves: radiation stress ← {rad.name}", flush=True)
            ds, _t, times_iso = open_with_times(rad, "FORT", "rad")
            source = ctx.rel_source(rad)
            stream = self._stream_for(ctx, times_iso, source)
            xv, yv = ds.variables["radstress_x"], ds.variables["radstress_y"]
            n_t, n_node = int(xv.shape[0]), int(xv.shape[1])
            rx = _read_time_node(xv, n_t, n_node)
            ry = _read_time_node(yv, n_t, n_node)
            units = str(getattr(xv, "units", "m2 s-2"))
            ds.close()
            rows.append(ctx.writer.add_field(
                "wave_radstress_x", rx, dims=["time", "node"], units=units,
                role="scalar", grid="unstructured", stream=stream,
                long_name="radiation stress gradient, eastward",
                cmap_hint="RdBu_r", source=source,
            ))
            rows.append(ctx.writer.add_field(
                "wave_radstress_y", ry, dims=["time", "node"], units=units,
                role="scalar", grid="unstructured", stream=stream,
                long_name="radiation stress gradient, northward",
                cmap_hint="RdBu_r", source=source,
            ))
            rows.append(ctx.writer.add_field(
                "wave_radstress_mag", np.hypot(rx, ry), dims=["time", "node"],
                units=units, role="scalar", grid="unstructured", stream=stream,
                long_name="radiation stress gradient magnitude",
                cmap_hint="speed", source=source,
            ))
            rows.append(ctx.writer.add_vector(
                "wave_radstress", "wave_radstress_x", "wave_radstress_y",
                units=units, grid="unstructured", stream=stream,
                long_name="radiation stress gradient",
                convention="uv; direction = atan2(-v, u) per Grapher.vectorDirection",
                cmap_hint="speed",
            ))
        return rows

    @staticmethod
    def _stream_for(ctx, times_iso: List[str], source: str) -> str:
        """SWAN often writes on its own interval — give it its own clock."""
        streams = ctx.writer.meta["time_streams"]
        for sid in ("swan", "adcirc"):
            if sid in streams and streams[sid]["times_utc"] == times_iso:
                return sid
        if "swan" not in streams:
            ctx.writer.add_time_stream("swan", times_iso, source=source)
        return "swan"
