"""D-RAIN — precipitation from a GFS / MetGet rain product.

Two fields, matching the offline Grapher semantics exactly:
  `rain_rate`  — the product's own per-snap precipitation
  `rain_accum` — **sum** over time (accumulation), not the last frame

The offline colour hints are carried over: 0–5 mm/h for rate, 0–500 mm for
accumulation. Units are taken from the file; nothing is converted silently.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from ..context import open_with_times
from .base import register

CHUNK = 32


@register
class RainGfsAdapter:
    name = "rain_gfs"
    products = ("rain",)

    def _path(self, ctx) -> Path | None:
        case = ctx.case_dir or ctx.rundir.parent
        return ctx.resolve(
            "rain",
            ctx.rundir / "gfs_rain.nc",
            case / "post_wind" / "gfs_rain.nc",
            case / "met" / "gfs_rain.nc",
            case / "post_forecast" / "gfs_rain.nc",
        )

    def available(self, ctx) -> bool:
        return self._path(ctx) is not None

    def export(self, ctx) -> List[Dict[str, Any]]:
        path = self._path(ctx)
        if path is None:
            return []
        print(f"  rain: {path}", flush=True)
        ds, _t, times_iso = open_with_times(path, "GFS", "rain")
        source = ctx.rel_source(path)
        stream = "rain"
        if "gfs" in ctx.writer.meta["time_streams"] and \
                len(ctx.writer.meta["time_streams"]["gfs"]["times_utc"]) == len(times_iso):
            stream = "gfs"
        else:
            ctx.writer.add_time_stream(stream, times_iso, source=source)

        grid_id = "rain"
        lat = np.asarray(ds.variables["lat"][:], dtype=float)
        lon = np.asarray(ds.variables["lon"][:], dtype=float)
        gfs_grid = ctx.writer.meta["grids"].get("gfs")
        if gfs_grid and gfs_grid["nx"] == lon.size and gfs_grid["ny"] == lat.size:
            grid_id = "gfs"
        else:
            ctx.writer.add_grid(grid_id, lon=lon, lat=lat, source=source)

        var = ds.variables["precipitation"]
        n_t, ny, nx = (int(s) for s in var.shape)
        rain = np.empty((n_t, ny, nx), dtype=np.float64)
        for start in range(0, n_t, CHUNK):
            stop = min(start + CHUNK, n_t)
            rain[start:stop] = np.ma.asarray(var[start:stop]).astype(np.float64).filled(np.nan)
            print(f"    rain {stop}/{n_t}", flush=True)
        ds.close()
        units = str(getattr(var, "units", "mm"))

        rows = [ctx.writer.add_field(
            "rain_rate", rain, dims=["time", "ny", "nx"], units=units, role="scalar",
            grid=grid_id, stream=stream, long_name="precipitation rate",
            cmap_hint="rain", range_hint=[0.0, 5.0], source=source,
        )]
        accum = np.nansum(rain, axis=0)
        accum[np.all(~np.isfinite(rain), axis=0)] = np.nan
        row = ctx.writer.add_field(
            "rain_accum", accum, dims=["ny", "nx"], units=units, role="scalar",
            grid=grid_id, stream=None, long_name="accumulated precipitation",
            cmap_hint="rain", range_hint=[0.0, 500.0], source=source,
        )
        row["static"] = True
        row["derivation"] = "sum over time (Grapher accumulation semantic)"
        rows.append(row)
        return rows
