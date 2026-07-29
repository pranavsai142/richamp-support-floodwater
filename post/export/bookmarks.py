"""Region bookmarks — the same extents the offline maps use (FR19).

Values mirror the `*_AXIS` constants at the top of `generateGraphs.py`, in the
offline order ``[lon_min, lon_max, lat_max, lat_min]``, converted here to the
web-standard bbox ``[west, south, east, north]``.

They are duplicated (not imported) on purpose: importing `generateGraphs`
would drag matplotlib, `GetRunup`, and the whole print stack into the exporter
— and runup is out of scope for this ladder.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

#: id -> offline axis [lon_min, lon_max, lat_max, lat_min]
OFFLINE_AXES: Dict[str, Sequence[float]] = {
    "RHODE_ISLAND": [-71.82698726277798, -71.00349734415707, 41.90734758914777, 41.29154575705807],
    "RHODE_ISLAND_CHAMP": [-71.9050164752, -71.1307245329, 42.000010143316864, 41.1192500979],
    "SOUTH_NEW_ENGLAND": [-71.905117442267496, -71.0339945492675, 42.200717972845119, 41.028319358056874],
    "BLOCK_ISLAND_SOUND": [-72.52397460937502, -70.87602539062502, 42.11417769664206, 40.87994188758605],
    "NARRAGANSETT_MOUTH": [-71.52799682617189, -71.32200317382814, 41.50218339933836, 41.34772474532908],
    "NEWPORT": [-71.55599363138899, -71.14424867207853, 41.65409629818921, 41.34571806834695],
    "PROVIDENCE": [-71.54599363138901, -71.1342486720785, 41.853618749387486, 41.54619474986597],
    "NAPATREE": [-71.88687460327148, -71.86112539672851, 41.31967002720852, 41.30032853828529],
    "LONG_ISLAND_SOUND_EAST": [-73.37397460937501, -71.72602539062501, 41.8170316891045, 40.577095781586486],
    "CAPE_COD_BAY": [-71.32397460937499, -69.67602539062499, 42.411307106237615, 41.18280523636922],
    "EAST_COAST": [-83.18359374999999, -56.816406249999986, 45.49399717614716, 24.090563202580892],
    "FLORIDA": [-85.7958984375, -79.2041015625, 30.383786045108156, 24.538640329845318],
    "GULF_YUCATAN": [-91.59179687500001, -78.40820312500001, 30.821121549266778, 18.889657344434774],
    "NORTH_ATLANTIC": [-76.59179620444773, -63.41595750651321, 46.70943547053439, 36.92061410517965],
    "ATLANTIC": [-89.47265625, -45.52734375, 49.402995871752374, 23.351173294924422],
}

LABELS: Dict[str, str] = {
    "RHODE_ISLAND": "Rhode Island",
    "RHODE_ISLAND_CHAMP": "Rhode Island (CHAMP)",
    "SOUTH_NEW_ENGLAND": "South New England",
    "BLOCK_ISLAND_SOUND": "Block Island Sound",
    "NARRAGANSETT_MOUTH": "Narragansett Mouth",
    "NEWPORT": "Newport",
    "PROVIDENCE": "Providence",
    "NAPATREE": "Napatree",
    "LONG_ISLAND_SOUND_EAST": "Long Island Sound (east)",
    "CAPE_COD_BAY": "Cape Cod Bay",
    "EAST_COAST": "East Coast",
    "FLORIDA": "Florida",
    "GULF_YUCATAN": "Gulf / Yucatan",
    "NORTH_ATLANTIC": "North Atlantic",
    "ATLANTIC": "Atlantic Basin",
}


def to_bbox(axis: Sequence[float]) -> List[float]:
    """Offline `[lon_min, lon_max, lat_max, lat_min]` -> `[w, s, e, n]`."""
    lon_min, lon_max, lat_max, lat_min = axis
    return [float(lon_min), float(lat_min), float(lon_max), float(lat_max)]


def _overlaps(bbox: Sequence[float], domain: Sequence[float]) -> bool:
    w, s, e, n = bbox
    dw, ds, de, dn = domain
    return not (e < dw or w > de or n < ds or s > dn)


def bookmarks_for_domain(
    lon_range: Sequence[float], lat_range: Sequence[float]
) -> List[Dict[str, Any]]:
    """Bookmarks that actually intersect this mesh, plus a full-domain entry."""
    domain = [
        float(lon_range[0]), float(lat_range[0]),
        float(lon_range[1]), float(lat_range[1]),
    ]
    out: List[Dict[str, Any]] = [
        {"id": "FULL_DOMAIN", "label": "Full mesh domain", "bbox": domain, "source": "mesh"}
    ]
    for key, axis in OFFLINE_AXES.items():
        bbox = to_bbox(axis)
        if _overlaps(bbox, domain):
            out.append(
                {
                    "id": key,
                    "label": LABELS.get(key, key),
                    "bbox": bbox,
                    "source": "generateGraphs *_AXIS",
                }
            )
    return out
