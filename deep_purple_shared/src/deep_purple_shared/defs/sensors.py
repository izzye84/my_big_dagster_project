from dagster import AssetSelection, AutomationConditionSensorDefinition

from deep_purple_shared.utils.performance_config import PERF_CONFIG

DEEP_PURPLE_EVALUATION_SENSOR_COUNT = 50


def generate_sensors_for_deep_purple_trigger_evaluation():
    _sensors = []
    for i in range(DEEP_PURPLE_EVALUATION_SENSOR_COUNT):
        _sensor = AutomationConditionSensorDefinition(
            f"deep_purple_eval_automation_sensor_{i}",
            target=AssetSelection.tag("evaluation_trigger_sensor_index", str(i)),
            default_status=PERF_CONFIG.sensor_default_status,
        )
        _sensors.append(_sensor)

    return _sensors


# Everything but the Full Deep Purple DAG assets
deep_purple_eval_default_automation_sensor = AutomationConditionSensorDefinition(
    "deep_purple_eval_automation_sensor_default",
    target=AssetSelection.all()
    - AssetSelection.groups("full_deep_purple_dummy_dag", include_sources=True),
    default_status=PERF_CONFIG.sensor_default_status,
    minimum_interval_seconds=120,
)


deep_purple_eval_sensors = generate_sensors_for_deep_purple_trigger_evaluation()
