"""
Configuration module for Dagster performance testing.

Provides simple toggles to control asset definitions for performance testing scenarios.
"""

from enum import Enum

import pandas as pd
from dagster import DefaultSensorStatus
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PartitionMode(str, Enum):
    """Partition mode for performance testing."""

    DAILY = "daily"
    """Use simple daily partitions."""

    TPS_ACTUAL = "tps_actual"
    """Use actual partition definition from TPS (based on effective start/end dates)."""


class PerformanceConfig(BaseSettings):
    """
    Configuration for performance testing.

    Configure via environment variables:
    - DEEP_PURPLE_PARTITION_MODE: Partition mode (daily or tps_actual)
    - DEEP_PURPLE_N_DAYS: Number of days for partitions
    - DEEP_PURPLE_SENSOR_DEFAULT_STATUS: Default sensor status (RUNNING or STOPPED)
    """

    model_config = SettingsConfigDict(
        env_prefix="DEEP_PURPLE_",
        case_sensitive=False,
    )

    partition_mode: PartitionMode = Field(
        default=PartitionMode.TPS_ACTUAL,
        description="Partition mode for performance testing",
        validation_alias="DEEP_PURPLE_PARTITION_MODE",
    )

    n_days: int = Field(
        default=3,
        description="Number of days for partitions",
        ge=1,
        validation_alias="DEEP_PURPLE_N_DAYS",
    )

    sensor_default_status: DefaultSensorStatus = Field(
        default=DefaultSensorStatus.RUNNING,
        description="Default status for sensors (RUNNING or STOPPED)",
        validation_alias="DEEP_PURPLE_SENSOR_DEFAULT_STATUS",
    )

    @property
    def start_date(self) -> pd.Timestamp:
        """
        Compute the start date based on n_days.

        :return: The start date (n_days ago from today).
        """
        return pd.Timestamp.now().normalize() - pd.Timedelta(days=self.n_days)

    @property
    def end_date(self) -> pd.Timestamp:
        """
        Compute the end date.

        :return: Today's date.
        """
        return pd.Timestamp.now().normalize()


# Global configuration instance
PERF_CONFIG = PerformanceConfig()
