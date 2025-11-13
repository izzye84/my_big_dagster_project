"""
Dagster definitions for code location 3.
Contains approximately 1/5 of all assets (hash-based distribution) and sensors 20-29.
"""

import dagster as dg

from deep_purple_location_3.defs.assets import location_3_assets
from deep_purple_location_3.defs.sensors import location_3_sensors


@dg.definitions
def defs():
    return dg.Definitions(
        assets=location_3_assets,
        sensors=location_3_sensors,
    )
