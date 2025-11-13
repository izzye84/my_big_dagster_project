"""
Dagster definitions for code location 4.
Contains approximately 1/5 of all assets (hash-based distribution) and sensors 30-39.
"""

import dagster as dg

from deep_purple_location_4.defs.assets import location_4_assets
from deep_purple_location_4.defs.sensors import location_4_sensors


@dg.definitions
def defs():
    return dg.Definitions(
        assets=location_4_assets,
        sensors=location_4_sensors,
    )
