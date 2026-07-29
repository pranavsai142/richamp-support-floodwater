"""D-WIND-PWM — parametric (PWM / windgfdl) wind on its basin lat/lon grid.

The owi2wind product (`*_parametric_wind.nc`) carries the **same variable
names** as the MetGet/GFS post nc (`wind_u` / `wind_v` / `PSFC` / `lon` /
`lat`, minutes since 1990). Honesty therefore lives in metadata, not var
names: this adapter declares stream ``parametric``, grid ``parametric`` and
long_names that say PWM/windgfdl — a parametric field must never read as
"GFS" in the UI (Lee golden law).

Size: the PWM basin grid is 565×625 at 1/12°; a full multi-day hourly pack
would be ~600 MB of wind alone. ``--wind-stride N`` subsamples the grid
spatially (never in time) and the stride is recorded on every field row and
in ``meta.fidelity`` — decimation is explicit or it does not happen.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from ..context import open_with_times
from .base import register

CHUNK = 32


@register
class WindParametricAdapter:
    name = "wind_parametric"
    products = ("wind_parametric",)

    def _path(self, ctx) -> Path | None:
        case = ctx.case_dir or ctx.rundir.parent
        candidates = []
        manifest_rel = (ctx.manifest.get("products") or {}).get("parametric_wind_nc")
        if manifest_rel:
            p = Path(manifest_rel)
            candidates.append(p if p.is_absolute() else case / p)
        met_pwm = case / "met_pwm"
        if met_pwm.is_dir():
            candidates.extend(sorted(met_pwm.glob("*parametric_wind*.nc")))
        return ctx.resolve("wind_parametric", *candidates)

    def available(self, ctx) -> bool:
        return self._path(ctx) is not None

    def export(self, ctx) -> List[Dict[str, Any]]:
        path = self._path(ctx)
        if path is None:
            return []
        stride = int(ctx.manifest.get("_wind_stride") or 0) or 1
        print(f"  wind (parametric PWM): {path} (spatial stride {stride})", flush=True)
        # owi2wind writes minutes-since-1990 exactly like the MetGet post nc,
        # so the Reader GFS path is the correct (and only) time parser here
        ds, _times_unix, times_iso = open_with_times(path, "GFS", "gfs")
        source = ctx.rel_source(path)
        ctx.writer.add_time_stream("parametric", times_iso, source=source)

        lon_full = np.asarray(ds.variables["lon"][:], dtype=float)
        lat_full = np.asarray(ds.variables["lat"][:], dtype=float)
        ctx.writer.add_grid(
            "parametric",
            lon=lon_full[::stride],
            lat=lat_full[::stride],
            source=source,
        )

        u_var, v_var = ds.variables["wind_u"], ds.variables["wind_v"]
        n_t, ny_full, nx_full = (int(s) for s in u_var.shape)
        ny = len(range(0, ny_full, stride))
        nx = len(range(0, nx_full, stride))
        u = np.empty((n_t, ny, nx), dtype=np.float64)
        v = np.empty((n_t, ny, nx), dtype=np.float64)
        for start in range(0, n_t, CHUNK):
            stop = min(start + CHUNK, n_t)
            u[start:stop] = np.ma.asarray(
                u_var[start:stop, ::stride, ::stride]).astype(np.float64).filled(np.nan)
            v[start:stop] = np.ma.asarray(
                v_var[start:stop, ::stride, ::stride]).astype(np.float64).filled(np.nan)
            print(f"    wind {stop}/{n_t}", flush=True)
        units = str(getattr(u_var, "units", "m s-1"))

        stride_extra = None
        if stride > 1:
            stride_extra = {
                "spatial_stride": stride,
                "native_shape": [n_t, ny_full, nx_full],
                "decimation_note": (
                    f"grid stride {stride} ({ny_full}x{nx_full} -> {ny}x{nx}); "
                    "time full; full-resolution nc stays on disk"
                ),
            }
            ctx.note(
                f"parametric wind grid stride {stride}: "
                f"{ny_full}x{nx_full} -> {ny}x{nx} (recorded per field)"
            )

        def _extra() -> Dict[str, Any] | None:
            return dict(stride_extra) if stride_extra else None

        rows = [
            ctx.writer.add_field(
                "wind_u", u, dims=["time", "ny", "nx"], units=units, role="scalar",
                grid="parametric", stream="parametric",
                long_name="10 m wind, parametric PWM (windgfdl), eastward component",
                cmap_hint="RdBu_r", source=source, extra=_extra(),
            ),
            ctx.writer.add_field(
                "wind_v", v, dims=["time", "ny", "nx"], units=units, role="scalar",
                grid="parametric", stream="parametric",
                long_name="10 m wind, parametric PWM (windgfdl), northward component",
                cmap_hint="RdBu_r", source=source, extra=_extra(),
            ),
            ctx.writer.add_field(
                "wind_speed", np.hypot(u, v), dims=["time", "ny", "nx"], units=units,
                role="scalar", grid="parametric", stream="parametric",
                long_name="10 m wind speed, parametric PWM (windgfdl)",
                cmap_hint="speed", range_hint=[0.0, 30.0], source=source, extra=_extra(),
            ),
            ctx.writer.add_vector(
                "wind", "wind_u", "wind_v", units=units, grid="parametric",
                stream="parametric",
                long_name="10 m wind, parametric PWM (windgfdl)",
                convention="uv_earth_relative; direction = atan2(-v, u) per Grapher.vectorDirection",
                cmap_hint="speed", range_hint=[0.0, 30.0],
            ),
        ]

        if "PSFC" in ds.variables:
            p_var = ds.variables["PSFC"]
            p = np.empty((n_t, ny, nx), dtype=np.float64)
            for start in range(0, n_t, CHUNK):
                stop = min(start + CHUNK, n_t)
                p[start:stop] = np.ma.asarray(
                    p_var[start:stop, ::stride, ::stride]).astype(np.float64).filled(np.nan)
            p_units = str(getattr(p_var, "units", "")).lower()
            mean = float(np.nanmean(p))
            if mean > 5000:
                p = p / 100.0
                p_units = "mb"
                ctx.note(f"PSFC mean {mean:.0f} looked like Pa — converted to mb")
            elif not p_units:
                p_units = "mb" if 800 < mean < 1200 else "unknown"
            rows.append(ctx.writer.add_field(
                "pressure_surface", p, dims=["time", "ny", "nx"], units=p_units,
                role="scalar", grid="parametric", stream="parametric",
                long_name="surface pressure, parametric PWM (PSFC — not reduced to sea level)",
                cmap_hint="RdYlBu_r", source=source, extra=_extra(),
            ))
        ds.close()
        return rows
