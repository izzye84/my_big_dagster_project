"""
Sensor definitions for code location 3.
This location manages sensors 20-29 (10 sensors total).
"""

from dagster import AssetSelection, AutomationConditionSensorDefinition

from deep_purple_shared.utils.performance_config import PERF_CONFIG

# This location handles sensors 20-29
SENSOR_START_INDEX = 20
SENSOR_END_INDEX = 29


def generate_location_sensors():
    """Generate automation condition sensors for this location's assets."""
    _sensors = []
    for i in range(SENSOR_START_INDEX, SENSOR_END_INDEX + 1):
        _sensor = AutomationConditionSensorDefinition(
            f"deep_purple_eval_automation_sensor_{i}",
            target=AssetSelection.tag("evaluation_trigger_sensor_index", str(i)),
            default_status=PERF_CONFIG.sensor_default_status,
        )
        _sensors.append(_sensor)

    return _sensors


location_3_sensors = generate_location_sensors()
