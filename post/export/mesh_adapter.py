"""fort.14 mesh -> pack mesh bins (D-MESH).

Geometry is sacred: the exported triangles are the run's own fort.14
connectivity and the exported lon/lat are the run's own node coordinates.
Nothing here regrids, decimates, or invents a coordinate.

`elev_m = -depth` matches the offline convention (`Fort14Reader.readMeshElevations`),
so the web bathy/topo layer and the offline `map_elevation.png` speak the same
sign.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..export.context import FULL_DOMAIN_AXIS  # noqa: F401  (re-export convenience)


def read_fort14(mesh_file: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
    """Parse fort.14 via the proven offline reader.

    Returns ``(lon, lat, elev_m, triangles0, mesh_name)``.
    """
    import sys

    repo_root = Path(__file__).resolve().parents[1].parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from Reader import Fort14Reader

    reader = Fort14Reader(
        ADCIRC_MESH_FILE=str(mesh_file),
        ADCIRC_MESH_DATA_FILE=str(mesh_file.parent / "_pack_mesh_scratch.json"),
        BACKGROUND_AXIS=list(FULL_DOMAIN_AXIS),
    )
    points, elevations, triangles, _masked = reader.readMeshElevations()
    lon = np.asarray(points[0], dtype=np.float64)
    lat = np.asarray(points[1], dtype=np.float64)
    elev = np.asarray(elevations, dtype=np.float64)
    tris = np.asarray(triangles, dtype=np.int64)

    mesh_name = ""
    with open(mesh_file, "r") as fh:
        mesh_name = fh.readline().strip()
    return lon, lat, elev, tris, mesh_name


def read_mesh_from_netcdf(nc_file: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
    """Fallback: the mesh embedded in an ADCIRC netCDF (x/y/depth/element).

    Same geometry as fort.14 for the same run; used only when no fort.14 was
    supplied. `element` is 1-based in the file, so it is shifted here exactly
    like `Reader.getTriangles` does.
    """
    import netCDF4 as nc

    ds = nc.Dataset(str(nc_file))
    lon = np.asarray(ds.variables["x"][:], dtype=np.float64)
    lat = np.asarray(ds.variables["y"][:], dtype=np.float64)
    depth = np.asarray(ds.variables["depth"][:], dtype=np.float64)
    tris = np.asarray(ds.variables["element"][:], dtype=np.int64) - 1
    mesh_name = str(ds.__dict__.get("agrid", "") or ds.__dict__.get("rundes", ""))
    ds.close()
    return lon, lat, -depth, tris, mesh_name


def export_mesh(ctx: Any) -> List[Dict[str, Any]]:
    """Write mesh bins + the static bathymetry node field."""
    mesh_file: Optional[Path] = ctx.mesh_file
    if mesh_file is not None and Path(mesh_file).exists():
        lon, lat, elev, tris, mesh_name = read_fort14(Path(mesh_file))
        source = ctx.rel_source(mesh_file)
    else:
        fallback = ctx.resolve(
            "water", ctx.rundir / "fort.63.nc", ctx.rundir / "maxele.63.nc"
        )
        if fallback is None:
            raise FileNotFoundError(
                "no fort.14 and no ADCIRC netCDF to take mesh geometry from"
            )
        lon, lat, elev, tris, mesh_name = read_mesh_from_netcdf(fallback)
        source = ctx.rel_source(fallback)
        ctx.note(f"mesh geometry taken from {source} (no fort.14 given)")

    print(
        f"  mesh: {lon.size} nodes / {tris.shape[0]} triangles  [{mesh_name}]",
        flush=True,
    )
    ctx.writer.set_mesh(
        lon=lon, lat=lat, elev_m=elev, triangles=tris, source=source, mesh_name=mesh_name
    )
    ctx.mesh_points = (lon, lat)

    # float32, not float16: abyssal depths reach ~8000 m where float16 ulp is 4 m,
    # and mesh/nodes.f32.bin already carries this column at full precision —
    # a lower-fidelity duplicate would be a silent downgrade.
    row = ctx.writer.add_field(
        name="bathymetry",
        data=elev,
        dims=["node"],
        units="m",
        role="scalar",
        grid="unstructured",
        stream=None,
        long_name="mesh elevation (−depth, positive up)",
        dtype="float32",
        cmap_hint="terrain",
        range_hint=[-15.0, 10.0],
        source=source,
    )
    row["static"] = True
    return [row]
