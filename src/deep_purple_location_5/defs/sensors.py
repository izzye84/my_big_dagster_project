"""
Sensor definitions for code location 5.
This location manages sensors 40-49 (10 sensors total).
"""

from dagster import AssetSelection, AutomationConditionSensorDefinition

from deep_purple.utils.performance_config import PERF_CONFIG

# This location handles sensors 40-49
SENSOR_START_INDEX = 40
SENSOR_END_INDEX = 49


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


location_5_sensors = generate_location_sensors()
