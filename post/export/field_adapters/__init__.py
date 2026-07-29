"""FieldAdapter registry — importing a module registers its adapter.

Add a product: write `my_thing.py` with `@register`, import it here. Nothing
else in the export or the web chrome changes (G-EXT).
"""

from .base import REGISTRY, FieldAdapter, adapters_for, all_products, register  # noqa: F401

# --- registration order = pack field order -------------------------------
from . import water_fort63  # noqa: F401,E402   D-WAT              (ORDER 2)
from . import wind_fort74  # noqa: F401,E402    D-WIND-F           (ORDER 7)
from . import wind_gfs  # noqa: F401,E402       D-WIND-G           (ORDER 7)
from . import wind_post  # noqa: F401,E402      D-WIND-P           (ORDER 7)
from . import rain_gfs  # noqa: F401,E402       D-RAIN             (ORDER 7)
from . import waves_swan  # noqa: F401,E402     D-SWH/MWD/MWP/PWP/RAD (ORDER 7)
from . import maxele  # noqa: F401,E402         D-MAX native       (ORDER 11, G-EXT)
from . import wind_parametric  # noqa: F401,E402 D-WIND-PWM        (Lee dual, G-LEE-PARAM)
