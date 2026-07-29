"""D-MAX (native) — ADCIRC's own `maxele.63.nc`.

This adapter exists as much as a demonstration as a product: adding it took one
file and one import line, no change to `pack_writer`, the loader, the verifier,
or any web chrome. That is the G-EXT contract.

It is also a real cross-check. `water_max` is the maximum over the *written*
output snapshots; `zeta_max` is ADCIRC's maximum over *every internal timestep*.
`zeta_max ≥ water_max` should hold everywhere, and the gap tells you how much
peak the output interval is missing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from ..context import iso_utc, open_with_times
from .base import register


@register
class MaxeleAdapter:
    name = "maxele"
    products = ("maxele", "water")

    def _path(self, ctx) -> Path | None:
        return ctx.resolve("maxele", ctx.rundir / "maxele.63.nc")

    def available(self, ctx) -> bool:
        return self._path(ctx) is not None

    def export(self, ctx) -> List[Dict[str, Any]]:
        import netCDF4 as nc

        path = self._path(ctx)
        if path is None:
            return []
        print(f"  maxele: {path}", flush=True)
        ds = nc.Dataset(str(path))
        source = ctx.rel_source(path)
        rows: List[Dict[str, Any]] = []

        zmax = np.ma.asarray(ds.variables["zeta_max"][:]).astype(np.float64).filled(np.nan)
        row = ctx.writer.add_field(
            "water_max_native", zmax, dims=["node"],
            units=str(getattr(ds.variables["zeta_max"], "units", "m")),
            role="scalar", grid="unstructured", stream=None,
            long_name="peak water surface elevation (ADCIRC maxele, all timesteps)",
            cmap_hint="balance", source=source,
        )
        row["static"] = True
        row["derivation"] = "ADCIRC internal maximum over every timestep"
        rows.append(row)

        if "time_of_zeta_max" in ds.variables:
            tvar = ds.variables["time_of_zeta_max"]
            tmax = np.ma.asarray(tvar[:]).astype(np.float64).filled(np.nan)
            # seconds since coldstart -> hours, which is what a reader can use
            row = ctx.writer.add_field(
                "water_max_time_h", tmax / 3600.0, dims=["node"], units="h",
                role="scalar", grid="unstructured", stream=None,
                long_name="hours after coldstart when the peak occurred",
                cmap_hint="turbo", dtype="float32", source=source,
            )
            row["static"] = True
            rows.append(row)
        ds.close()

        # cross-check against the swath derived from the output snapshots
        derived = next(
            (f for f in ctx.writer.meta["fields"] if f["name"] == "water_max"), None
        )
        if derived is not None:
            native_max = float(np.nanmax(zmax))
            print(
                f"    cross-check: native peak {native_max:.3f} m vs "
                f"snapshot swath {derived['max']:.3f} m "
                f"(native ≥ snapshot expected — output interval misses sub-step peaks)",
                flush=True,
            )
            ctx.note(
                f"maxele peak {native_max:.3f} m vs snapshot-derived water_max "
                f"{derived['max']:.3f} m"
            )
        return rows
