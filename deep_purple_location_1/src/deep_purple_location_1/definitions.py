"""
Dagster definitions for code location 1.
Contains approximately 1/5 of all assets (hash-based distribution) and sensors 0-9.
"""

import dagster as dg

from deep_purple_location_1.defs.assets import location_1_assets
from deep_purple_location_1.defs.sensors import location_1_sensors


@dg.definitions
def defs():
    return dg.Definitions(
        assets=location_1_assets,
        sensors=location_1_sensors,
    )
