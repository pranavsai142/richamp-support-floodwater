"""Coastal fieldpack export CLI.

    export PYTHONPATH=~/projects/richamp-support-floodwater
    python -m post.export.cli \
      --rundir  ~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/forecast \
      --mesh    ~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/forecast/fort.14 \
      --case    ~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512 \
      --products mesh,water \
      --outdir  ~/projects/adcirc-local-smoke/ec95d_gfs_5d_2026072512/products/fieldpack

Exit codes mirror the atmospheric twin: 0 ok · 2 missing inputs · 3 write failure.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Dict, List

from . import bookmarks as bookmarks_mod
from .context import ExportContext
from .field_adapters import REGISTRY, adapters_for, all_products
from .mesh_adapter import export_mesh
from .pack_writer import PackWriteError, PackWriter

EXIT_OK = 0
EXIT_MISSING = 2
EXIT_WRITE = 3

#: products handled outside the FieldAdapter registry
CORE_PRODUCTS = ("mesh", "stations", "obs_water", "obs_waves", "track")

#: compare-role → candidate field names, first present wins (meta.roles)
ROLE_CANDIDATES = (
    ("water_surface", ("water_zeta",)),
    ("water_max", ("water_max", "water_max_native")),
    ("wind_10m_u", ("wind_u", "param_wind_u")),
    ("wind_10m_v", ("wind_v", "param_wind_v")),
    ("wind_10m_speed", ("wind_speed", "param_wind_speed")),
    ("pressure_surface", ("pressure_surface",)),
)


def met_family(wind_mode) -> str | None:
    """Honest met family from a run_manifest ``modes.wind`` string."""
    s = str(wind_mode or "").lower()
    if s.startswith("parametric"):
        return "parametric"
    if "gfs" in s:
        return "gfs"
    if "shield" in s or "fv3" in s:
        return "shield"
    return None


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="post.export.cli",
        description="Export an ADCIRC(+SWAN) run as adcirc-fieldpack/v0",
    )
    p.add_argument("--rundir", required=True, help="ADCIRC output dir (holds fort.63.nc …)")
    p.add_argument("--outdir", required=True, help="fieldpack output directory")
    p.add_argument("--mesh", help="fort.14 (defaults to <rundir>/fort.14)")
    p.add_argument("--case", help="case root (for run_manifest.json + provenance paths)")
    p.add_argument("--run-id", help="override run id (defaults to case/rundir name)")
    p.add_argument(
        "--products",
        default="mesh,water",
        help=f"comma list; core={','.join(CORE_PRODUCTS)} adapters={','.join(all_products())}",
    )
    p.add_argument("--stations", help="stations json (default: repo OBS_STATIONS.json)")
    p.add_argument("--temp-dir", help="scratch dir for Reader stencil json")
    p.add_argument(
        "--path",
        action="append",
        default=[],
        metavar="KEY=PATH",
        help="explicit product path override, e.g. --path wind_gfs=/…/gfs_wind.nc",
    )
    p.add_argument(
        "--post-stride",
        type=int,
        default=0,
        help="spatial stride for the RICHAMP post wind product (0 = do not export; "
             "any value is recorded in meta.fidelity.decimation — never silent)",
    )
    p.add_argument(
        "--wind-stride",
        type=int,
        default=0,
        help="spatial stride for basin-scale gridded wind (parametric PWM); "
             "0/1 = full grid; recorded on field rows + meta.fidelity — never silent",
    )
    p.add_argument(
        "--default-utc",
        help="scenario hint: ISO time the shell should open on (nearest snap), "
             "written to meta.scenario.default_utc",
    )
    p.add_argument("--list-products", action="store_true", help="print registry and exit")
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    if args.list_products:
        print("core:     " + ", ".join(CORE_PRODUCTS))
        for a in REGISTRY:
            print(f"adapter:  {a.name:<16} products={','.join(a.products)}")
        return EXIT_OK

    rundir = Path(args.rundir).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()
    if not rundir.is_dir():
        print(f"FAIL: rundir not a directory: {rundir}", file=sys.stderr)
        return EXIT_MISSING

    case_dir = Path(args.case).expanduser().resolve() if args.case else rundir.parent
    mesh_file = Path(args.mesh).expanduser().resolve() if args.mesh else (rundir / "fort.14")
    if not mesh_file.exists():
        mesh_file = None  # mesh_adapter falls back to the netCDF-embedded mesh

    repo_root = Path(__file__).resolve().parents[2]
    stations_file = (
        Path(args.stations).expanduser().resolve()
        if args.stations
        else repo_root / "OBS_STATIONS.json"
    )

    manifest: Dict = {}
    manifest_path = case_dir / "run_manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
        except (OSError, json.JSONDecodeError) as e:
            print(f"  warn: could not read {manifest_path}: {e}", flush=True)

    run_id = (
        args.run_id
        or manifest.get("run_id")
        or (case_dir.name if case_dir.name else rundir.name)
    )

    products = [s.strip() for s in args.products.split(",") if s.strip()]
    overrides: Dict[str, Path] = {}
    for spec in args.path:
        if "=" not in spec:
            print(f"FAIL: --path needs KEY=PATH, got {spec!r}", file=sys.stderr)
            return EXIT_MISSING
        k, v = spec.split("=", 1)
        overrides[k.strip()] = Path(v).expanduser().resolve()

    print(f"adcirc-fieldpack export → {outdir}")
    print(f"  run_id   : {run_id}")
    print(f"  rundir   : {rundir}")
    print(f"  mesh     : {mesh_file if mesh_file else '(from netCDF)'}")
    print(f"  products : {','.join(products)}")

    writer = PackWriter(outdir, run_id=run_id)
    ctx = ExportContext(
        rundir=rundir,
        outdir=outdir,
        writer=writer,
        run_id=run_id,
        mesh_file=mesh_file,
        case_dir=case_dir,
        stations_file=stations_file,
        temp_dir=Path(args.temp_dir).expanduser().resolve() if args.temp_dir else None,
        products=products,
        paths=overrides,
        manifest=manifest,
    )
    ctx.manifest["_post_stride"] = args.post_stride
    ctx.manifest["_wind_stride"] = args.wind_stride

    phase = rundir.name if rundir.name in ("analysis", "forecast") else None
    if phase:
        writer.meta["phase"] = phase

    try:
        if "mesh" in products:
            export_mesh(ctx)
        else:
            print("  warn: mesh not requested — unstructured fields will have no geometry")

        ran: List[str] = []
        for adapter in adapters_for(products):
            if not adapter.available(ctx):
                print(f"  skip {adapter.name}: inputs not present")
                continue
            rows = adapter.export(ctx)
            ran.append(adapter.name)
            for r in rows:
                if r.get("role") == "vector":
                    print(
                        f"    + {r['name']:<16} vector{'':<20} "
                        f"{r.get('units','')}  ← {', '.join(r.get('components', []))}"
                    )
                else:
                    print(
                        f"    + {r['name']:<16} {str(r.get('dims')):<26} "
                        f"{r.get('units','')}  [{r.get('min')}, {r.get('max')}]"
                    )

        if "stations" in products or "obs_water" in products or "obs_waves" in products:
            from .station_export import export_stations

            export_stations(ctx)

        if "track" in products:
            from .track_export import export_track

            export_track(ctx)

        mesh_meta = writer.meta.get("mesh")
        if mesh_meta:
            writer.set_bookmarks(
                bookmarks_mod.bookmarks_for_domain(
                    mesh_meta["lon_range"], mesh_meta["lat_range"]
                )
            )

        # modes.wind keeps the manifest's honest string (parametric_nws6 /
        # gfs_nws6_fort22) when wind fields shipped — a bare bool loses the
        # met family the compare UI keys on
        has_wind = any(n.startswith("wind_") for n in writer.field_names())
        wind_mode = (manifest.get("modes") or {}).get("wind")
        writer.set_modes(
            water="water_zeta" in writer.field_names(),
            mesh=bool(mesh_meta),
            waves=any(n.startswith("wave_") for n in writer.field_names()),
            wind=(wind_mode if (has_wind and isinstance(wind_mode, str)) else has_wind),
            rain=any(n.startswith("rain_") for n in writer.field_names()),
            track=bool(writer.meta.get("tracks")),
            runup=False,
        )

        # meta.scenario — storm + honest met family from the run manifest;
        # the catalog card may mirror this but the pack wins on conflict
        scenario: Dict = {}
        if manifest.get("storm"):
            scenario["storm"] = manifest["storm"]
        met: Dict = {}
        family = met_family(wind_mode)
        if family and has_wind:
            met["family"] = family
        if isinstance(wind_mode, str):
            met["wind_mode"] = wind_mode
        wind_src = next(
            (f.get("source") for f in writer.meta["fields"]
             if f.get("name") == "wind_u" and f.get("source")), None,
        )
        if wind_src:
            met["source"] = wind_src
        if met:
            scenario["met"] = met
        if args.default_utc:
            scenario["default_utc"] = args.default_utc
        if scenario:
            writer.meta["scenario"] = scenario

        # meta.roles — compare binds by role, never by hardcoded field name
        roles = {}
        have = set(writer.field_names())
        for role, candidates in ROLE_CANDIDATES:
            for cand in candidates:
                if cand in have:
                    roles[role] = cand
                    break
        if roles:
            writer.meta["roles"] = roles
        writer.set_fidelity(
            horizontal="full mesh (no node subsample)",
            temporal="all model output times",
            adapters=ran,
            notes=ctx.notes,
        )
        if args.wind_stride and args.wind_stride > 1 and "wind_parametric" in ran:
            writer.set_fidelity(decimation=(
                f"gridded parametric wind spatial stride {args.wind_stride} "
                "(explicit --wind-stride, recorded per field row); "
                "mesh, water and time axes full"
            ))
        if manifest:
            writer.meta["provenance"]["run_manifest"] = str(manifest_path)
            cold = manifest.get("coldstart", {}).get("base_date_iso")
            if cold:
                writer.meta["coldstart_utc"] = cold

        meta_path = writer.write()
    except FileNotFoundError as e:
        print(f"FAIL (missing input): {e}", file=sys.stderr)
        return EXIT_MISSING
    except PackWriteError as e:
        print(f"FAIL (pack): {e}", file=sys.stderr)
        return EXIT_WRITE
    except Exception:  # noqa: BLE001 — report, do not paper over
        traceback.print_exc()
        return EXIT_WRITE

    print(f"wrote {meta_path}")
    print(f"  fields: {', '.join(writer.field_names()) or '(none)'}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
