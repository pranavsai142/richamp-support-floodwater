"""adcirc-fieldpack/v0 export — coastal member of the suite fieldpack family.

    python -m post.export.cli --rundir <run> --mesh <fort.14> \
        --products mesh,water --outdir <case>/products/fieldpack

Contract: `ADCIRC_FIELDPACK_V0.md` (this directory).
Loader / verifier: `~/projects/CloudVision/threejs-shield-live-viz/`.
"""

from .pack_writer import SCHEMA, PackWriteError, PackWriter  # noqa: F401
