"""D-WIND-F — ADCIRC's own wind field from fort.74.nc, on the mesh nodes.

Same nodes as ζ, so the shell reuses the water mesh geometry directly. Units
and sign convention are ADCIRC's (`windx`/`windy`, m/s, earth-relative); the
direction convention is applied once, in the shell, via `atan2(-v, u)`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from ..context import open_with_times
from .base import register

CHUNK = 24


@register
class WindFort74Adapter:
    name = "wind_fort74"
    products = ("wind", "wind_fort74")

    def _path(self, ctx) -> Path | None:
        return ctx.resolve("wind_fort74", ctx.rundir / "fort.74.nc")

    def available(self, ctx) -> bool:
        return self._path(ctx) is not None

    def export(self, ctx) -> List[Dict[str, Any]]:
        path = self._path(ctx)
        if path is None:
            return []
        print(f"  wind (ADCIRC fort.74): {path}", flush=True)
        ds, _t, times_iso = open_with_times(path, "FORT", "fort")
        source = ctx.rel_source(path)
        # fort.74 rides the ADCIRC clock; reuse the stream if water already made it
        stream = "adcirc"
        if stream not in ctx.writer.meta["time_streams"]:
            ctx.writer.add_time_stream(stream, times_iso, source=source)
        elif len(ctx.writer.meta["time_streams"][stream]["times_utc"]) != len(times_iso):
            stream = "adcirc_wind"
            ctx.writer.add_time_stream(stream, times_iso, source=source)
            ctx.note("fort.74 output interval differs from fort.63 — separate stream")

        u_var, v_var = ds.variables["windx"], ds.variables["windy"]
        n_t, n_node = int(u_var.shape[0]), int(u_var.shape[1])
        u = np.empty((n_t, n_node), dtype=np.float64)
        v = np.empty((n_t, n_node), dtype=np.float64)
        for start in range(0, n_t, CHUNK):
            stop = min(start + CHUNK, n_t)
            u[start:stop] = np.ma.asarray(u_var[start:stop]).astype(np.float64).filled(np.nan)
            v[start:stop] = np.ma.asarray(v_var[start:stop]).astype(np.float64).filled(np.nan)
            print(f"    fort.74 {stop}/{n_t}", flush=True)
        ds.close()
        units = str(getattr(u_var, "units", "m s-1"))

        return [
            ctx.writer.add_field(
                "wind_u", u, dims=["time", "node"], units=units, role="scalar",
                grid="unstructured", stream=stream,
                long_name="ADCIRC wind, eastward component",
                cmap_hint="RdBu_r", source=source,
            ),
            ctx.writer.add_field(
                "wind_v", v, dims=["time", "node"], units=units, role="scalar",
                grid="unstructured", stream=stream,
                long_name="ADCIRC wind, northward component",
                cmap_hint="RdBu_r", source=source,
            ),
            ctx.writer.add_field(
                "wind_speed", np.hypot(u, v), dims=["time", "node"], units=units,
                role="scalar", grid="unstructured", stream=stream,
                long_name="ADCIRC wind speed", cmap_hint="speed",
                range_hint=[0.0, 20.0], source=source,
            ),
            ctx.writer.add_vector(
                "wind", "wind_u", "wind_v", units=units, grid="unstructured",
                stream=stream, long_name="ADCIRC wind",
                convention="uv_earth_relative; direction = atan2(-v, u) per Grapher.vectorDirection",
                cmap_hint="speed", range_hint=[0.0, 20.0],
            ),
        ]
