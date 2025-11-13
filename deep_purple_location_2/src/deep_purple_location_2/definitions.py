"""
Dagster definitions for code location 2.
Contains approximately 1/5 of all assets (hash-based distribution) and sensors 10-19.
"""

import dagster as dg

from deep_purple_location_2.defs.assets import location_2_assets
from deep_purple_location_2.defs.sensors import location_2_sensors


@dg.definitions
def defs():
    return dg.Definitions(
        assets=location_2_assets,
        sensors=location_2_sensors,
    )
