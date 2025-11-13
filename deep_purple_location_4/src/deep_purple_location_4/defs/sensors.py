"""
Sensor definitions for code location 4.
This location manages sensors 30-39 (10 sensors total).
"""

from dagster import AssetSelection, AutomationConditionSensorDefinition

from deep_purple_shared.utils.performance_config import PERF_CONFIG

# This location handles sensors 30-39
SENSOR_START_INDEX = 30
SENSOR_END_INDEX = 39


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


location_4_sensors = generate_location_sensors()
