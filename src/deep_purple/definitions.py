import os
from pathlib import Path

import dagster as dg

DEFAULT_DEEP_PURPLE_MULTI_PROCESS_NUM_WORKERS = 4


@dg.definitions
def defs():
    loaded = dg.load_from_defs_folder(path_within_project=Path(__file__).parent.parent.parent)

    # Set default executor for all jobs
    return dg.Definitions(
        assets=loaded.assets,
        sensors=loaded.sensors,
        executor=dg.multiprocess_executor.configured(
            {
                # default is 16 which is too high for deep purple
                "max_concurrent": int(
                    os.getenv(
                        "DEEP_PURPLE_MULTI_PROCESS_NUM_WORKERS",
                        DEFAULT_DEEP_PURPLE_MULTI_PROCESS_NUM_WORKERS,
                    )
                )
            }
        ),
    )
