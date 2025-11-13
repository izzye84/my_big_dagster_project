import dagster as dg

"""
Custom eager condition:
- Without latest time window restriction
"""
eager_all_partitions: dg.AutomationCondition = (
    dg.AutomationCondition.eager().without(dg.AutomationCondition.in_latest_time_window())
).with_label("eager_all_partitions")
