"""D-TRACK — driving-track products for the pack (browser-native JSON).

For a parametric-forced scenario the driving track is the scientific overlay,
not chrome. This exports the **same track files that fed PWM**:

  * ``lee_best_track.trk``-style ATCF (BEST) → ``tracks/drive_track.json``
  * ``track.richamp`` (PWM geometry/time)   → ``tracks/pwm_track.json``

plus ``tracks/catalog.json``. No NHC shapefiles are required — the Lee golden
has none (GIS zip optional); when a case has them a converter can add GeoJSON
entries to the same catalog later.

Coordinates come from the track files verbatim. Sentinels (−999) and blanks
become ``null`` in JSON — never 0, never invented.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_latlon_token(tok: str, lat: bool) -> Optional[float]:
    """ATCF-style token: '122N' → 12.2 · '0396W' → −39.6 (tenths of a degree)."""
    tok = tok.strip()
    if not tok or len(tok) < 2:
        return None
    hemi = tok[-1].upper()
    try:
        val = float(tok[:-1]) / 10.0
    except ValueError:
        return None
    if lat:
        if hemi == "N":
            return val
        if hemi == "S":
            return -val
        return None
    if hemi == "E":
        return val
    if hemi == "W":
        return -val
    return None


def _num(tok: str) -> Optional[float]:
    """Numeric field with −999-style sentinels mapped to None (JSON null)."""
    tok = tok.strip()
    if not tok:
        return None
    try:
        v = float(tok)
    except ValueError:
        return None
    if v <= -998.0:
        return None
    return v


def parse_atcf_track(path: Path) -> Dict[str, List[Any]]:
    """ATCF best/advisory deck → one row per timestamp.

    ATCF repeats a timestamp once per wind radius (34/50/64 kt). The first row
    of each timestamp carries the position / vmax / mslp / RMW used here; the
    radii rows are deliberately not flattened into the track geometry.
    """
    times: List[str] = []
    lon: List[Optional[float]] = []
    lat: List[Optional[float]] = []
    vmax_kt: List[Optional[float]] = []
    mslp_mb: List[Optional[float]] = []
    rmw_nm: List[Optional[float]] = []
    storm_type: List[Optional[str]] = []
    seen: set = set()

    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        cols = [c.strip() for c in line.split(",")]
        if len(cols) < 11:
            continue
        stamp = cols[2]
        if len(stamp) != 10 or not stamp.isdigit() or stamp in seen:
            continue
        la = _parse_latlon_token(cols[6], lat=True)
        lo = _parse_latlon_token(cols[7], lat=False)
        if la is None or lo is None:
            continue
        seen.add(stamp)
        dt = datetime(int(stamp[0:4]), int(stamp[4:6]), int(stamp[6:8]),
                      int(stamp[8:10]), tzinfo=timezone.utc)
        times.append(_iso(dt))
        lat.append(la)
        lon.append(lo)
        vmax_kt.append(_num(cols[8]) if len(cols) > 8 else None)
        mslp_mb.append(_num(cols[9]) if len(cols) > 9 else None)
        storm_type.append(cols[10] or None if len(cols) > 10 else None)
        rmw_nm.append(_num(cols[19]) if len(cols) > 19 else None)

    return {
        "times_utc": times, "lon": lon, "lat": lat,
        "vmax_kt": vmax_kt, "mslp_mb": mslp_mb, "rmw_nm": rmw_nm,
        "storm_type": storm_type,
    }


def parse_richamp_track(path: Path) -> Dict[str, List[Any]]:
    """``track.richamp`` (PWM input) → per-snapshot geometry + intensity.

    Whitespace columns (observed on the Lee golden):
      [3] YYYYMMDD · [4] HHMM · [5] lat '122N' · [6] lon '0396W' ·
      [7] heading° · [8] min pressure mb · [10] env pressure mb ·
      [12] max wind m/s · [13] RMW km
    """
    times: List[str] = []
    lon: List[Optional[float]] = []
    lat: List[Optional[float]] = []
    heading_deg: List[Optional[float]] = []
    mslp_mb: List[Optional[float]] = []
    penv_mb: List[Optional[float]] = []
    vmax_ms: List[Optional[float]] = []
    rmw_km: List[Optional[float]] = []

    for line in path.read_text().splitlines():
        cols = line.split()
        if len(cols) < 13:
            continue
        d, hm = cols[3], cols[4]
        if len(d) != 8 or not d.isdigit() or len(hm) != 4 or not hm.isdigit():
            continue
        la = _parse_latlon_token(cols[5], lat=True)
        lo = _parse_latlon_token(cols[6], lat=False)
        if la is None or lo is None:
            continue
        dt = datetime(int(d[0:4]), int(d[4:6]), int(d[6:8]),
                      int(hm[0:2]), int(hm[2:4]), tzinfo=timezone.utc)
        times.append(_iso(dt))
        lat.append(la)
        lon.append(lo)
        heading_deg.append(_num(cols[7]))
        mslp_mb.append(_num(cols[8]))
        penv_mb.append(_num(cols[10]))
        vmax_ms.append(_num(cols[12]))
        rmw_km.append(_num(cols[13]) if len(cols) > 13 else None)

    return {
        "times_utc": times, "lon": lon, "lat": lat,
        "heading_deg": heading_deg, "mslp_mb": mslp_mb, "penv_mb": penv_mb,
        "vmax_ms": vmax_ms, "rmw_km": rmw_km,
    }


def _sane(track: Dict[str, List[Any]]) -> bool:
    if not track["times_utc"]:
        return False
    for lo, la in zip(track["lon"], track["lat"]):
        if lo is None or la is None:
            return False
        if not (-180.0 <= lo <= 180.0 and -90.0 <= la <= 90.0):
            return False
    return True


def export_track(ctx) -> None:
    """Resolve track sources for the case and write ``tracks/`` into the pack."""
    case = ctx.case_dir or ctx.rundir.parent
    manifest_products = ctx.manifest.get("products") or {}

    trk_candidates: List[Path] = []
    manifest_trk = manifest_products.get("track_source")
    if manifest_trk:
        p = Path(manifest_trk)
        trk_candidates.append(p if p.is_absolute() else case / p)
    for sub in ("met_pwm", "properties"):
        d = case / sub
        if d.is_dir():
            trk_candidates.extend(sorted(d.glob("*best*track*.trk")))
            trk_candidates.extend(sorted(d.glob("*.trk")))
    trk_path = ctx.resolve("track_source", *trk_candidates)

    richamp_path = ctx.resolve(
        "track_richamp",
        case / "met_pwm" / "track.richamp",
        case / "properties" / "track.richamp",
    )

    if trk_path is None and richamp_path is None:
        ctx.note("track requested but no .trk / track.richamp found — skipped")
        return

    storm = ctx.manifest.get("storm") or {}
    storm_label = " ".join(
        str(x) for x in (storm.get("name"), storm.get("basin"),
                         storm.get("number"), storm.get("year")) if x
    ) or ctx.run_id

    items: Dict[str, Any] = {}
    catalog_rows: List[Dict[str, Any]] = []

    if trk_path is not None:
        track = parse_atcf_track(trk_path)
        if _sane(track):
            payload = {
                "id": "drive_track",
                "role": "forcing",
                "crs": "EPSG:4326",
                "source": ctx.rel_source(trk_path),
                "label": f"{storm_label} BEST track (PWM drive)",
                **track,
            }
            items["drive_track"] = payload
            catalog_rows.append({
                "id": "drive_track", "label": payload["label"],
                "path": "tracks/drive_track.json", "role": "forcing",
                "source": payload["source"], "n": len(track["times_utc"]),
            })
            print(f"  track: {trk_path.name} → drive_track "
                  f"({len(track['times_utc'])} fixes "
                  f"{track['times_utc'][0]} … {track['times_utc'][-1]})", flush=True)
        else:
            ctx.note(f"track file {trk_path} parsed empty/insane — not exported")

    if richamp_path is not None:
        track = parse_richamp_track(richamp_path)
        if _sane(track):
            payload = {
                "id": "pwm_track",
                "role": "forcing_geometry",
                "crs": "EPSG:4326",
                "source": ctx.rel_source(richamp_path),
                "label": f"{storm_label} track.richamp (PWM geometry)",
                **track,
            }
            items["pwm_track"] = payload
            catalog_rows.append({
                "id": "pwm_track", "label": payload["label"],
                "path": "tracks/pwm_track.json", "role": "forcing_geometry",
                "source": payload["source"], "n": len(track["times_utc"]),
            })
            print(f"  track: {richamp_path.name} → pwm_track "
                  f"({len(track['times_utc'])} fixes)", flush=True)
        else:
            ctx.note(f"track.richamp {richamp_path} parsed empty/insane — not exported")

    if not items:
        ctx.note("no sane track parsed — tracks/ not written")
        return

    if "drive_track" in items and "pwm_track" in items:
        n_d = len(items["drive_track"]["times_utc"])
        n_p = len(items["pwm_track"]["times_utc"])
        ctx.note(f"track cross-check: BEST {n_d} fixes vs track.richamp {n_p} fixes")

    catalog = {
        "tracks": catalog_rows,
        "note": (
            "Driving track parsed from the same files that fed PWM "
            "(generateParametricInput / windgfdl). Sentinel −999 → null; "
            "coordinates verbatim from the track file."
        ),
    }
    ctx.writer.add_tracks(catalog, items)
    for src in (trk_path, richamp_path):
        if src is not None:
            ctx.writer._add_source(ctx.rel_source(src))
