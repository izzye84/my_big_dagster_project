import random

import dagster as dg
import pandas as pd

from deep_purple.defs.automation_conditions import eager_all_partitions
from deep_purple.defs.sensors import DEEP_PURPLE_EVALUATION_SENSOR_COUNT
from deep_purple.utils.constants import DATETIME_FORMAT, ASSET_TYPE, DAG_CSV_PATH
from deep_purple.utils.performance_config import PERF_CONFIG, PartitionMode


def create_partition_definition(
    timeslice_duration_seconds: int, start_date_str: str, end_date_str: str
) -> dg.PartitionsDefinition:
    """
    Create a partition definition based on timeslice duration using cron schedules.

    :param timeslice_duration_seconds: Duration of each partition in seconds.
    :param start_date: Start date for partitions.
    :param end_date: End date for partitions.
    :return: Appropriate partition definition.
    """
    # Actual values in TPS:
    # 300 (5 min): 18 datasets
    # 600 (10 min): 5 datasets
    # 900 (15 min): 6 datasets
    # 1200 (20 min): 1 dataset
    # 1800 (30 min): 7 datasets
    # 3600 (1 hour): 13,139 datasets
    # 10800 (3 hours): 3 datasets
    # 21600 (6 hours): 21 datasets
    # 86400 (1 day): 1,669 datasets

    cron_schedule_map = {
        300: "*/5 * * * *",  # Every 5 minutes
        600: "*/10 * * * *",  # Every 10 minutes
        900: "*/15 * * * *",  # Every 15 minutes
        1200: "*/20 * * * *",  # Every 20 minutes
        1800: "*/30 * * * *",  # Every 30 minutes
        3600: "0 * * * *",  # Every hour
        10800: "0 */3 * * *",  # Every 3 hours
        21600: "0 */6 * * *",  # Every 6 hours
        86400: "0 0 * * *",  # Daily
    }

    cron_schedule = cron_schedule_map.get(
        timeslice_duration_seconds, "0 0 * * *"
    )  # Default to daily

    return dg.TimeWindowPartitionsDefinition(
        cron_schedule=cron_schedule,
        start=start_date_str,
        end=end_date_str,
        fmt=DATETIME_FORMAT,
        timezone="UTC",
    )


def generate_full_deep_purple_dag(start_date: pd.Timestamp, end_date: pd.Timestamp):
    # Read gzip compressed CSV
    raw_data = pd.read_csv(DAG_CSV_PATH)
    formatted_start = pd.Timestamp(start_date).strftime(DATETIME_FORMAT)
    formatted_end = pd.Timestamp(end_date).strftime(DATETIME_FORMAT)

    tps_parents_by_dataset = (
        raw_data.groupby("DATASET_NAME")["PARENT_DATASET_NAME"].apply(list).to_dict()
    )
    tps_datasets = (
        raw_data[
            [
                "DATASET_NAME",
                "END_DATE",
                "START_DATE",
                "QUEUE_BINDING",
                "PARTITION_SECONDS",
                "MAX_CONTIGUOUS_SECONDS",
            ]
        ]
        .drop_duplicates(subset=["DATASET_NAME"])
        .reset_index(drop=True)
    )

    # Get set of all datasets that have their own rows (as children)
    valid_datasets = set(tps_datasets["DATASET_NAME"])

    _all_deep_purple_assets = []

    _deps_with_assets_already = []

    _total_number_of_assets = 0

    for _, row in tps_datasets.iterrows():
        dataset_name = row["DATASET_NAME"]
        queue_binding = row["QUEUE_BINDING"]
        partition_seconds = row["PARTITION_SECONDS"]
        max_contiguous_seconds = row["MAX_CONTIGUOUS_SECONDS"]
        parent_datasets = list(set(tps_parents_by_dataset.get(dataset_name, [])))

        # Calculate max_partitions_per_run for backfill policy
        # Handle None/NaN values by defaulting to 1 partition
        if pd.notna(max_contiguous_seconds) and partition_seconds > 0:
            max_partitions_per_run = max(
                1, int(max_contiguous_seconds / partition_seconds)
            )
        else:
            max_partitions_per_run = 1

        # Use dataset_name directly as asset_name (e.g., managed.{hash} or source.{hash})
        # Replace dots with underscores for valid Dagster asset names
        asset_name = dataset_name.replace(".", "_")

        if PERF_CONFIG.partition_mode == PartitionMode.TPS_ACTUAL:
            daily_partition = create_partition_definition(
                partition_seconds, formatted_start, formatted_end
            )
        else:
            daily_partition = dg.DailyPartitionsDefinition(start_date=formatted_start, end_date=formatted_end)

        dependency_assets = []
        for parent_dataset in parent_datasets:
            # Skip managed parents that don't have their own rows in the CSV (we don't have metadata for them)
            if parent_dataset.startswith("managed.") and parent_dataset not in valid_datasets:
                continue

            # Convert parent dataset name to asset name (replace . with _)
            parent_asset_name = parent_dataset.replace(".", "_")
            dependency_assets.append(parent_asset_name)

            # Create external assets for source dependencies (not managed assets)
            if parent_dataset not in _deps_with_assets_already and not parent_dataset.startswith("managed."):
                _total_number_of_assets += 1

                @dg.asset(
                    name=parent_asset_name,
                    tags={
                        ASSET_TYPE: "",
                        "is_dgp_asset": "false",
                        "evaluation_trigger_sensor_index": str(
                            _total_number_of_assets % DEEP_PURPLE_EVALUATION_SENSOR_COUNT
                        ),
                    },
                    group_name=ASSET_TYPE,
                    kinds={"SourceDGP"},
                    partitions_def=daily_partition,
                    backfill_policy=dg.BackfillPolicy.multi_run(max_partitions_per_run=1),
                )
                def _deep_purple_dgp_source_asset():
                    return dg.MaterializeResult(
                        metadata={"dagster/row_count": random.randint(500, 2000)}
                    )

                _all_deep_purple_assets.append(_deep_purple_dgp_source_asset)

                _deps_with_assets_already.append(parent_dataset)

        _total_number_of_assets += 1

        @dg.asset(
            name=asset_name,
            deps=dependency_assets,
            tags={
                ASSET_TYPE: "",
                "is_dgp_asset": "true",
                "evaluation_trigger_sensor_index": str(
                    _total_number_of_assets % DEEP_PURPLE_EVALUATION_SENSOR_COUNT
                ),
                "queue_binding": queue_binding,
            },
            group_name=ASSET_TYPE,
            kinds={"ManagedDGP"},
            partitions_def=daily_partition,
            backfill_policy=dg.BackfillPolicy.multi_run(
                max_partitions_per_run=max_partitions_per_run
            ),
            automation_condition=eager_all_partitions,
            metadata={
                "START_DATE": start_date,
                "END_DATE": end_date,
                "MAX_CONTIGUOUS_SECONDS": max_contiguous_seconds,
                "MAX_PARTITIONS_PER_RUN": max_partitions_per_run,
            },
        )
        def _deep_purple_dgp_asset():
            return dg.MaterializeResult(metadata={"dagster/row_count": random.randint(2000, 10000)})

        _all_deep_purple_assets.append(_deep_purple_dgp_asset)

    return _all_deep_purple_assets


# Use performance configuration for stress testing
start_date = PERF_CONFIG.start_date
end_date = PERF_CONFIG.end_date

all_deep_purple_assets = generate_full_deep_purple_dag(start_date=start_date, end_date=end_date)
