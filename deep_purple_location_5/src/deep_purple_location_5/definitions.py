"""
Dagster definitions for code location 5.
Contains approximately 1/5 of all assets (hash-based distribution) and sensors 40-49.
"""

import dagster as dg

from deep_purple_location_5.defs.assets import location_5_assets
from deep_purple_location_5.defs.sensors import location_5_sensors


@dg.definitions
def defs():
    return dg.Definitions(
        assets=location_5_assets,
        sensors=location_5_sensors,
    )
