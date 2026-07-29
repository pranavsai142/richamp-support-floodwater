"""D-WIND-G — GFS / MetGet wind on its regular lat/lon grid.

`wind_u` / `wind_v` are exported verbatim from the product (m/s, earth-relative
u/v as MetGet writes them). `wind_speed` is derived as `hypot(u, v)` for the
scalar layer; direction is **not** precomputed — the shell derives it with
`Grapher.vectorDirection`'s `atan2(-v, u)` so there is exactly one convention
in the system.

The GFS clock is its own stream: MetGet snaps are typically 15-minutely while
fort.63 is hourly, so this field must never ride the ADCIRC scrubber index.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from ..context import open_with_times
from .base import register

CHUNK = 32


@register
class WindGfsAdapter:
    name = "wind_gfs"
    products = ("wind", "wind_gfs")

    def _path(self, ctx) -> Path | None:
        case = ctx.case_dir or ctx.rundir.parent
        return ctx.resolve(
            "wind_gfs",
            ctx.rundir / "gfs_wind.nc",
            case / "post_wind" / "gfs_wind.nc",
            case / "post_forecast" / "gfs_wind.nc",
        )

    def available(self, ctx) -> bool:
        return self._path(ctx) is not None

    def export(self, ctx) -> List[Dict[str, Any]]:
        path = self._path(ctx)
        if path is None:
            return []
        print(f"  wind (GFS): {path}", flush=True)
        ds, _times_unix, times_iso = open_with_times(path, "GFS", "gfs")
        source = ctx.rel_source(path)
        ctx.writer.add_time_stream("gfs", times_iso, source=source)
        ctx.writer.add_grid(
            "gfs",
            lon=np.asarray(ds.variables["lon"][:], dtype=float),
            lat=np.asarray(ds.variables["lat"][:], dtype=float),
            source=source,
        )

        u_var, v_var = ds.variables["wind_u"], ds.variables["wind_v"]
        n_t, ny, nx = (int(s) for s in u_var.shape)
        u = np.empty((n_t, ny, nx), dtype=np.float64)
        v = np.empty((n_t, ny, nx), dtype=np.float64)
        for start in range(0, n_t, CHUNK):
            stop = min(start + CHUNK, n_t)
            u[start:stop] = np.ma.asarray(u_var[start:stop]).astype(np.float64).filled(np.nan)
            v[start:stop] = np.ma.asarray(v_var[start:stop]).astype(np.float64).filled(np.nan)
            print(f"    wind {stop}/{n_t}", flush=True)
        units = str(getattr(u_var, "units", "m s-1"))

        rows = [
            ctx.writer.add_field(
                "wind_u", u, dims=["time", "ny", "nx"], units=units, role="scalar",
                grid="gfs", stream="gfs", long_name="GFS 10 m wind, eastward component",
                cmap_hint="RdBu_r", source=source,
            ),
            ctx.writer.add_field(
                "wind_v", v, dims=["time", "ny", "nx"], units=units, role="scalar",
                grid="gfs", stream="gfs", long_name="GFS 10 m wind, northward component",
                cmap_hint="RdBu_r", source=source,
            ),
            ctx.writer.add_field(
                "wind_speed", np.hypot(u, v), dims=["time", "ny", "nx"], units=units,
                role="scalar", grid="gfs", stream="gfs",
                long_name="GFS 10 m wind speed", cmap_hint="speed",
                range_hint=[0.0, 20.0], source=source,
            ),
            ctx.writer.add_vector(
                "wind", "wind_u", "wind_v", units=units, grid="gfs", stream="gfs",
                long_name="GFS 10 m wind",
                convention="uv_earth_relative; direction = atan2(-v, u) per Grapher.vectorDirection",
                cmap_hint="speed", range_hint=[0.0, 20.0],
            ),
        ]

        if "PSFC" in ds.variables:
            p_var = ds.variables["PSFC"]
            p = np.empty((n_t, ny, nx), dtype=np.float64)
            for start in range(0, n_t, CHUNK):
                stop = min(start + CHUNK, n_t)
                p[start:stop] = np.ma.asarray(p_var[start:stop]).astype(np.float64).filled(np.nan)
            p_units = str(getattr(p_var, "units", "")).lower()
            # the pressure trap, coastal edition: MetGet writes mb here, but if a
            # product ever hands over Pa the mean gives it away instantly
            mean = float(np.nanmean(p))
            if mean > 5000:
                p = p / 100.0
                p_units = "mb"
                ctx.note(f"PSFC mean {mean:.0f} looked like Pa — converted to mb")
            elif not p_units:
                p_units = "mb" if 800 < mean < 1200 else "unknown"
            # PSFC is *surface* pressure, not sea-level pressure. Over the ocean
            # they nearly coincide, over land they do not — so it keeps the
            # product's own name rather than borrowing the atmosphere's PRMSL.
            rows.append(ctx.writer.add_field(
                "pressure_surface", p, dims=["time", "ny", "nx"], units=p_units,
                role="scalar", grid="gfs", stream="gfs",
                long_name="GFS surface pressure (PSFC — not reduced to sea level)",
                cmap_hint="RdYlBu_r", source=source,
            ))
        ds.close()
        return rows
