"""Export context — resolves run inputs and shares the Reader Lego.

Time parsing and the closest-node stencil are **not** reimplemented here. They
come from `Reader.py`, which is where two years of coldstart / stencil fidelity
already lives (`Reader._parseColdStartDate`, `Reader.getNetcdfProperties`,
`Reader.initializeClosestNodes`).
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# repo root on sys.path so `import Reader` works when run as `python -m post.export.cli`
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from Reader import Reader  # noqa: E402  (after sys.path fix)

#: full domain — the export never crops science; display bounds are a UI concern
FULL_DOMAIN_AXIS = [-999.0, 999.0, 999.0, -999.0]


def iso_utc(unix_seconds: float) -> str:
    """Unix seconds -> ISO-8601 Z, matching the twin's `times_utc` formatting."""
    return (
        datetime.fromtimestamp(float(unix_seconds), timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    )


def open_with_times(path: os.PathLike | str, fmt: str, data_type: str):
    """Open a product through `Reader.getNetcdfProperties`.

    Returns ``(dataset, times_unix, times_iso)``. ``fmt`` is the Reader format
    ("FORT" | "GFS" | "POST"); ``data_type`` is the Reader dataType token
    ("water" | "fort" | "gfs" | "post" | "rain" | "swh" | ...). Using the Reader
    keeps ADCIRC seconds-vs-GFS-minutes and the `base_date` quirks (e.g.
    "2018-02-23 0Z") identical to the offline graphs.
    """
    reader = Reader(BACKGROUND_AXIS=FULL_DOMAIN_AXIS, format=fmt)
    dataset, times = reader.getNetcdfProperties(str(path), data_type)
    return dataset, times, [iso_utc(t) for t in times]


@dataclass
class ExportContext:
    """Everything an adapter needs. Adapters must not reach outside this."""

    rundir: Path
    outdir: Path
    writer: Any  # PackWriter (avoids a circular import)
    run_id: str
    mesh_file: Optional[Path] = None
    case_dir: Optional[Path] = None
    stations_file: Optional[Path] = None
    temp_dir: Optional[Path] = None
    products: List[str] = field(default_factory=list)
    #: explicit product path overrides, e.g. {"wind_gfs": "/…/gfs_wind.nc"}
    paths: Dict[str, Path] = field(default_factory=dict)
    #: mesh node lon/lat cached by the mesh adapter for station/stencil reuse
    mesh_points: Optional[tuple] = None
    manifest: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def wants(self, product: str) -> bool:
        return product in self.products

    def resolve(self, key: str, *candidates: os.PathLike | str) -> Optional[Path]:
        """First existing path for ``key``: explicit override, then candidates."""
        override = self.paths.get(key)
        if override is not None:
            p = Path(override)
            return p if p.exists() else None
        for c in candidates:
            if c is None:
                continue
            p = Path(c)
            if p.exists():
                return p
        return None

    def rel_source(self, path: os.PathLike | str) -> str:
        """Path recorded in provenance — relative to the case dir when possible."""
        p = Path(path)
        base = self.case_dir or self.rundir
        try:
            return str(p.relative_to(base))
        except ValueError:
            return str(p)

    def note(self, msg: str) -> None:
        self.notes.append(msg)
        print(f"  note: {msg}", flush=True)

    def temp(self) -> Path:
        d = self.temp_dir or (self.outdir / "_export_temp")
        d.mkdir(parents=True, exist_ok=True)
        return d
