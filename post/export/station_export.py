"""Station catalog + model / obs series for the pack (D-STN, O-NOS, O-NDBC, O-USGS).

Nothing about the station stencil is reimplemented here. The model series come
from the offline Readers themselves — `Fort63Reader`, `WaveReader`,
`GFSWindReader`, `PostWindReader`, `Fort74Reader` — which run
`Reader.initializeClosestNodes` (closest-node + threshold stencil) and
`generateDataFilesWithInterpolation` (LinearND with nearest fill outside the
hull). That is exactly the path behind the offline `*_station_water.png`, so a
web series and a print series are the same numbers.

The intermediate JSON those Readers write is **export-internal**. Only the
fieldpack is public.

Observations come from the same `GetBuoy*` adapters the offline stack uses:
CO-OPS product API for water (the ERDDAP `.mat` endpoint is dead), NDBC for
waves, NWIS for rain.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from .context import FULL_DOMAIN_AXIS, iso_utc

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

#: which OBS_STATIONS group each model product is compared against
GROUP_FOR = {
    "water": "NOS",
    "wind": "NOS",
    "swh": "NDBC",
    "mwd": "NDBC",
    "mwp": "NDBC",
    "pwp": "NDBC",
    "rad": "NDBC",
    "rain": "USGS",
}

#: pack series key -> (Reader dataType, value field in the Reader's temp json, units)
SERIES_SPEC = {
    "water": ("water", "water", "m"),
    "wave_swh": ("swh", "swh", "m"),
    "wave_mwd": ("mwd", "mwd", "deg"),
    "wave_mwp": ("mwp", "mwp", "s"),
    "wave_pwp": ("pwp", "pwp", "s"),
}


def _load_stations(path: Path) -> Dict[str, Any]:
    with open(path) as fh:
        return json.load(fh)


def _series_from_reader_json(
    data_file: Path, value_key: str, units: str, source: str, kind: str = "model"
) -> Dict[str, Any]:
    """Convert one Reader temp JSON into pack series rows."""
    with open(data_file) as fh:
        raw = json.load(fh)
    out: Dict[str, Any] = {}
    for station_key, rec in raw.items():
        values = rec.get(value_key)
        if values is None:
            continue
        vals = np.asarray(values, dtype=float).ravel()
        times = [iso_utc(t) for t in rec.get("times", [])]
        if len(times) != vals.size:
            # a Reader that interpolated a single point returns a 1×T row;
            # anything else is a shape mismatch worth surfacing, not hiding
            if vals.size % max(1, len(times)) == 0 and len(times):
                vals = vals[: len(times)]
            else:
                print(
                    f"  warn: station {station_key} {value_key}: "
                    f"{vals.size} values vs {len(times)} times — skipped",
                    flush=True,
                )
                continue
        out[station_key] = {
            "times": times,
            "values": [None if not np.isfinite(v) else float(v) for v in vals],
            "units": units,
            "kind": kind,
            "node_index": rec.get("nodeIndex"),
            "node_lon": rec.get("longitude"),
            "node_lat": rec.get("latitude"),
            "source": source,
        }
    return out


def _closest_node_series(
    nc_file: Path, var_name: str, nodes_file: Path, units: str, source: str
) -> Dict[str, Any]:
    """Each station's **own closest node**, straight out of the netCDF.

    Why this exists alongside the interpolated series: on a coarse mesh the
    offline `generateDataFilesWithInterpolation` builds one *shared* support
    cloud from every station's stencil, so a station whose stencil is empty is
    interpolated from other stations' nodes — potentially hundreds of km away.
    That is the offline behaviour and it is preserved verbatim in the `water`
    series, but the pack also carries the local value so the discrepancy is
    visible rather than silently baked in. Both are real model output; the UI
    labels which is which, and `node_distance_km` says how far the node is.
    """
    import netCDF4 as nc

    if not nodes_file.exists():
        return {}
    try:
        nodes = json.load(open(nodes_file)).get("NOS", {})
    except (OSError, json.JSONDecodeError):
        return {}
    ds = nc.Dataset(str(nc_file))
    if var_name not in ds.variables:
        ds.close()
        return {}
    var = ds.variables[var_name]
    reader_times = None
    out: Dict[str, Any] = {}
    from .context import open_with_times  # local import: keeps module import cheap

    try:
        base = ds.variables["time"]
        from Reader import Reader as _R

        cold = _R()._parseColdStartDate(base.units)
        secs = np.asarray(base[:], dtype=float)
        unit = base.units.lower()
        scale = 60.0 if unit.strip().startswith("minutes") else 1.0
        reader_times = [
            iso_utc((cold.timestamp() + t * scale)) for t in secs
        ]
    except Exception:  # noqa: BLE001 — fall back to no times rather than wrong times
        reader_times = None

    for key, rec in nodes.items():
        node_index = rec.get("nodeIndex")
        if node_index is None:
            continue
        try:
            col = np.ma.asarray(var[:, int(node_index)]).astype(float).filled(np.nan)
        except (ValueError, IndexError):
            continue
        out[key] = {
            "times": reader_times or [],
            "values": [None if not np.isfinite(v) else float(v) for v in col],
            "units": units,
            "kind": "model_node",
            "node_index": node_index,
            "node_lon": rec.get("longitude"),
            "node_lat": rec.get("latitude"),
            "source": source,
            "note": "closest mesh node, no interpolation",
        }
    ds.close()
    return out


def _obs_series(obs_file: Path, value_key: str, time_key: str, units: str,
                source: str) -> Dict[str, Any]:
    with open(obs_file) as fh:
        raw = json.load(fh)
    out: Dict[str, Any] = {}
    for key, rec in raw.items():
        times = rec.get(time_key) or []
        vals = rec.get(value_key) or []
        if not len(times) or not len(vals):
            continue
        n = min(len(times), len(vals))
        out[key] = {
            "times": [iso_utc(t) for t in times[:n]],
            "values": [None if v is None or not np.isfinite(float(v)) else float(v)
                       for v in vals[:n]],
            "units": units,
            "kind": "obs",
            "source": source,
        }
    return out


def _catalog(
    stations: Dict[str, Any],
    nodes_files: Dict[str, Path],
    distance_files: Dict[str, Path],
) -> Dict[str, Any]:
    """Station catalog with the stencil the model series actually used."""
    groups: Dict[str, Dict[str, Any]] = {}
    for group in ("NOS", "NDBC", "USGS"):
        if group not in stations:
            continue
        entries: Dict[str, Any] = {}
        stencil = {}
        dist = {}
        nf = nodes_files.get(group)
        if nf and nf.exists():
            try:
                stencil = json.load(open(nf)).get("NOS", {})
            except (OSError, json.JSONDecodeError):
                stencil = {}
        df = distance_files.get(group)
        if df and df.exists():
            try:
                dist = json.load(open(df))
            except (OSError, json.JSONDecodeError):
                dist = {}
        for key, s in stations[group].items():
            rec = {
                "id": s.get("id"),
                "name": s.get("name"),
                "lon": float(s["longitude"]),
                "lat": float(s["latitude"]),
                "obs_source": s.get("source"),
            }
            st = stencil.get(key)
            if st:
                rec["node_index"] = st.get("nodeIndex")
                rec["node_lon"] = st.get("longitude")
                rec["node_lat"] = st.get("latitude")
                rec["stencil_n"] = len(st.get("closestNodes") or [])
            d = dist.get(key)
            if isinstance(d, dict) and d.get("distance") is not None:
                rec["node_distance_km"] = float(d["distance"])
            if group == "NOS":
                rec["datum"] = "MSL (CO-OPS product API)"
            entries[key] = rec
        groups[group] = entries
    return {
        "groups": groups,
        "note": (
            "Model series use Reader.initializeClosestNodes + "
            "generateDataFilesWithInterpolation — the same stencil as the offline "
            "station graphs. Obs datum may differ from the model's vertical datum; "
            "both are labelled, neither is silently shifted."
        ),
    }


def export_stations(ctx) -> None:
    """Run the offline Readers for station series, then fold them into the pack."""
    from Reader import Fort63Reader, WaveReader

    stations_file = Path(ctx.stations_file)
    if not stations_file.exists():
        ctx.note(f"no stations file at {stations_file}; skipping stations")
        return
    stations = _load_stations(stations_file)
    temp = ctx.temp()
    series: Dict[str, Any] = {}
    nodes_files: Dict[str, Path] = {}
    distance_files: Dict[str, Path] = {}
    window: List[datetime] = []

    # ---------------------------------------------------------------- water
    water_nc = ctx.resolve("water", ctx.rundir / "fort.63.nc")
    if water_nc is not None and (ctx.wants("stations") or ctx.wants("obs_water")):
        print(f"  stations: water via Fort63Reader ({water_nc.name})", flush=True)
        data_file = temp / "water_data_file.json"
        reader = Fort63Reader(
            ADCIRC_WATER_FILE=str(water_nc),
            STATIONS_FILE=str(stations_file),
            ADCIRC_WATER_DATA_FILE=str(data_file),
            BACKGROUND_AXIS=list(FULL_DOMAIN_AXIS),
        )
        start, end = reader.generateWindDataForStations()
        window = [start, end]
        series["water"] = _series_from_reader_json(
            data_file, "water", "m", ctx.rel_source(water_nc)
        )
        nodes_files["NOS"] = temp / "ADCIRC_Nodes.json"
        distance_files["NOS"] = temp / "ADCIRC_Station_To_Node_Distances.json"
        node_series = _closest_node_series(
            water_nc, "zeta", nodes_files["NOS"], "m", ctx.rel_source(water_nc)
        )
        if node_series:
            series["water_node"] = node_series
        print(
            f"    model water series: {len(series['water'])} stations "
            f"(+{len(node_series)} closest-node)",
            flush=True,
        )

    # ---------------------------------------------------------------- waves
    swh_nc = ctx.resolve("wave_swh", ctx.rundir / "swan_HS.63.nc")
    if swh_nc is not None and ctx.wants("stations"):
        print(f"  stations: waves via WaveReader ({swh_nc.name})", flush=True)
        wave_files = {
            "WAVE_SWH_FILE": swh_nc,
            "WAVE_MWD_FILE": ctx.resolve("wave_mwd", ctx.rundir / "swan_DIR.63.nc"),
            "WAVE_MWP_FILE": ctx.resolve("wave_mwp", ctx.rundir / "swan_TMM10.63.nc"),
            "WAVE_PWP_FILE": ctx.resolve("wave_pwp", ctx.rundir / "swan_TPS.63.nc"),
            "WAVE_RAD_FILE": ctx.resolve("wave_rad", ctx.rundir / "rads.64.nc"),
        }
        kwargs = {k: (str(v) if v else "") for k, v in wave_files.items()}
        reader = WaveReader(
            STATIONS_FILE=str(stations_file),
            WAVE_SWH_DATA_FILE=str(temp / "wave_swh_data_file.json"),
            WAVE_MWD_DATA_FILE=str(temp / "wave_mwd_data_file.json"),
            WAVE_MWP_DATA_FILE=str(temp / "wave_mwp_data_file.json"),
            WAVE_PWP_DATA_FILE=str(temp / "wave_pwp_data_file.json"),
            WAVE_RAD_DATA_FILE=str(temp / "wave_rad_data_file.json"),
            BACKGROUND_AXIS=list(FULL_DOMAIN_AXIS),
            **kwargs,
        )
        start, end = reader.generateWaveDataForStations()
        if not window:
            window = [start, end]
        for key, (_dt, value_key, units) in SERIES_SPEC.items():
            if not key.startswith("wave_"):
                continue
            f = temp / f"{key}_data_file.json"
            if f.exists():
                series[key] = _series_from_reader_json(
                    f, value_key, units, ctx.rel_source(swh_nc)
                )
        nodes_files["NDBC"] = temp / "Wave_Nodes.json"
        distance_files["NDBC"] = temp / "Wave_Station_To_Node_Distances.json"

    # ------------------------------------------------------------- wave obs
    if ctx.wants("obs_waves") and window:
        try:
            from GetBuoyWaves import GetBuoyWaves

            obs_file = temp / "obs_wave_data_file.json"
            GetBuoyWaves(
                STATIONS_FILE=str(stations_file),
                OBS_WAVE_DATA_FILE=str(obs_file),
                startDateObject=window[0],
                endDateObject=window[1],
            )
            if obs_file.exists():
                series["obs_wave_swh"] = _obs_series(
                    obs_file, "waveHeights", "times", "m", "NDBC"
                )
                print(f"    obs waves: {len(series['obs_wave_swh'])} stations", flush=True)
        except Exception as e:  # noqa: BLE001 — obs are best-effort, never fatal
            ctx.note(f"NDBC wave obs unavailable: {e}")

    # ------------------------------------------------------------ water obs
    if ctx.wants("obs_water") and window:
        try:
            from GetBuoyWater import GetBuoyWater

            obs_file = temp / "obs_water_data_file.json"
            GetBuoyWater(
                STATIONS_FILE=str(stations_file),
                OBS_WATER_DATA_FILE=str(obs_file),
                startDateObject=window[0],
                endDateObject=window[1],
            )
            if obs_file.exists():
                series["obs_water"] = _obs_series(
                    obs_file, "water", "times", "m", "CO-OPS product API (MSL)"
                )
                pred = _obs_series(
                    obs_file, "prediction_water", "prediction_times", "m",
                    "CO-OPS predictions (MSL)"
                )
                if pred:
                    series["obs_water_prediction"] = pred
                print(f"    obs water: {len(series['obs_water'])} stations", flush=True)
        except Exception as e:  # noqa: BLE001
            ctx.note(f"CO-OPS water obs unavailable: {e}")

    if not series:
        ctx.note("no station series produced")
        return

    catalog = _catalog(stations, nodes_files, distance_files)
    if window:
        catalog["window_utc"] = [window[0].isoformat(), window[1].isoformat()]
    ctx.writer.add_stations(catalog, series)
    print(f"  stations: {', '.join(series.keys())}", flush=True)
