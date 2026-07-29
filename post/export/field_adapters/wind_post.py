"""D-WIND-P — RICHAMP / POST downscaled wind (`RICHAMP_wind.nc`, `Main` group).

The product is `spd` (m/s) and `dir` (**meteorological — the direction the wind
is coming from**), on a ~30 m NLCD-resolution grid. A 5-day RI run is ~6 GB;
the full field cannot travel in a browser pack.

Spatial striding is therefore **opt-in and loud**: `--path wind_post=…` plus
`--post-stride N`. The stride is written into the field row and into
`meta.fidelity.decimation`, so a viewer can never mistake a strided field for
the native product. Default `--post-stride 0` means "do not export this
product" rather than silently shipping a thinned one.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from ..context import open_with_times
from .base import register


@register
class WindPostAdapter:
    name = "wind_post"
    products = ("wind_post",)

    def _path(self, ctx) -> Path | None:
        case = ctx.case_dir or ctx.rundir.parent
        return ctx.resolve(
            "wind_post",
            case / "post_wind" / "RICHAMP_wind.nc",
            ctx.rundir / "RICHAMP_wind.nc",
        )

    def available(self, ctx) -> bool:
        return self._path(ctx) is not None

    def export(self, ctx) -> List[Dict[str, Any]]:
        path = self._path(ctx)
        if path is None:
            return []
        stride = int(ctx.manifest.get("_post_stride", 0) or 0)
        if stride <= 0:
            ctx.note(
                f"{path.name} present but --post-stride not set; skipping "
                "(refusing to ship a silently thinned high-res field)"
            )
            return []

        print(f"  wind (RICHAMP post, stride {stride}): {path}", flush=True)
        ds, _t, times_iso = open_with_times(path, "POST", "post")
        source = ctx.rel_source(path)
        ctx.writer.add_time_stream("post", times_iso, source=source)

        lat = np.asarray(ds.variables["lat"][::stride], dtype=float)
        lon = np.asarray(ds.variables["lon"][::stride], dtype=float)
        ctx.writer.add_grid("post", lon=lon, lat=lat, source=source)

        spd_var, dir_var = ds.variables["spd"], ds.variables["dir"]
        n_t = int(spd_var.shape[0])
        ny, nx = lat.size, lon.size
        spd = np.empty((n_t, ny, nx), dtype=np.float64)
        drc = np.empty((n_t, ny, nx), dtype=np.float64)
        for t in range(n_t):
            spd[t] = np.ma.asarray(spd_var[t, ::stride, ::stride]).astype(np.float64).filled(np.nan)
            drc[t] = np.ma.asarray(dir_var[t, ::stride, ::stride]).astype(np.float64).filled(np.nan)
            if (t + 1) % 20 == 0 or t + 1 == n_t:
                print(f"    post wind {t + 1}/{n_t}", flush=True)
        ds.close()

        note = (
            f"spatial stride {stride} applied on export "
            f"({stride}× coarser than the native ~30 m grid); "
            "full resolution remains in RICHAMP_wind.nc and the offline graphs"
        )
        ctx.writer.set_fidelity(decimation=note)
        ctx.note(note)

        rows = [
            ctx.writer.add_field(
                "wind_post_speed", spd, dims=["time", "ny", "nx"],
                units=str(getattr(spd_var, "units", "m s-1")), role="scalar",
                grid="post", stream="post", long_name="RICHAMP downscaled wind speed",
                cmap_hint="speed", range_hint=[0.0, 20.0], source=source,
                extra={"decimation": note, "stride": stride},
            ),
            ctx.writer.add_field(
                "wind_post_dir", drc, dims=["time", "ny", "nx"],
                units=str(getattr(dir_var, "units", "degrees")), role="scalar",
                grid="post", stream="post",
                long_name="RICHAMP wind direction (meteorological, coming from)",
                cmap_hint="phase", range_hint=[0.0, 360.0], source=source,
                extra={"decimation": note, "stride": stride,
                       "convention": "meteorological — direction the wind comes from"},
            ),
        ]
        rows.append(ctx.writer.add_vector(
            "wind_post", "wind_post_speed", "wind_post_dir",
            units=str(getattr(spd_var, "units", "m s-1")), grid="post", stream="post",
            long_name="RICHAMP downscaled wind",
            convention="spd_dir_met",
            cmap_hint="speed", range_hint=[0.0, 20.0],
        ))
        return rows
