"""D-WAT — water surface elevation ζ from fort.63.nc (+ swath).

Times come from `Reader.getNetcdfProperties` so the coldstart parse is
byte-for-byte the offline one. ζ is written time×node at full mesh resolution:
no spatial subsample, no time subsample.

Dry nodes stay NaN (ADCIRC `_FillValue = -99999`). The swath is `nanmax` over
time — the Grapher "max over time" semantic, not the last frame.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from ..context import open_with_times
from .base import register

#: read this many time steps at once (keeps a 5-day basin run inside a few hundred MB)
CHUNK = 24


@register
class WaterFort63Adapter:
    name = "water_fort63"
    products = ("water",)

    def _path(self, ctx) -> Path | None:
        return ctx.resolve(
            "water",
            ctx.rundir / "fort.63.nc",
        )

    def available(self, ctx) -> bool:
        return self._path(ctx) is not None

    def export(self, ctx) -> List[Dict[str, Any]]:
        path = self._path(ctx)
        if path is None:
            return []
        print(f"  water: {path}", flush=True)
        ds, times_unix, times_iso = open_with_times(path, "FORT", "water")
        source = ctx.rel_source(path)
        ctx.writer.add_time_stream("adcirc", times_iso, source=source, make_default=True)

        var = ds.variables["zeta"]
        n_t, n_node = int(var.shape[0]), int(var.shape[1])
        zeta = np.empty((n_t, n_node), dtype=np.float64)
        for start in range(0, n_t, CHUNK):
            stop = min(start + CHUNK, n_t)
            block = np.ma.asarray(var[start:stop, :])
            zeta[start:stop, :] = block.astype(np.float64).filled(np.nan)
            print(f"    zeta {stop}/{n_t}", flush=True)
        ds.close()

        rows = [
            ctx.writer.add_field(
                name="water_zeta",
                data=zeta,
                dims=["time", "node"],
                units=str(getattr(var, "units", "m")),
                role="scalar",
                grid="unstructured",
                stream="adcirc",
                long_name="water surface elevation above geoid",
                cmap_hint="balance",
                source=source,
            )
        ]

        with np.errstate(invalid="ignore"):
            swath = np.full(n_node, np.nan, dtype=np.float64)
            any_wet = np.isfinite(zeta).any(axis=0)
            swath[any_wet] = np.nanmax(zeta[:, any_wet], axis=0)
        row = ctx.writer.add_field(
            name="water_max",
            data=swath,
            dims=["node"],
            units=str(getattr(var, "units", "m")),
            role="scalar",
            grid="unstructured",
            stream=None,
            long_name="peak water surface elevation over the run (swath)",
            cmap_hint="balance",
            source=source,
        )
        row["static"] = True
        row["derivation"] = "max over time (Grapher swath semantic)"
        rows.append(row)
        return rows
