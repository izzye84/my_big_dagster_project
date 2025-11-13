"""
Utility functions for distributing assets across multiple code locations.
"""
import hashlib


def get_asset_location(asset_name: str, num_locations: int = 5) -> int:
    """
    Determine which code location an asset belongs to based on hash.

    Uses a deterministic hash function (MD5) to ensure consistent assignment
    across different Python processes.

    :param asset_name: The name of the asset (e.g., "managed_abc123" or "source_xyz789")
    :param num_locations: Total number of code locations (default 5)
    :return: Location number (1-5)
    """
    # Use MD5 for deterministic hashing across Python processes
    hash_value = int(hashlib.md5(asset_name.encode()).hexdigest(), 16)
    return (hash_value % num_locations) + 1


def should_create_asset_in_location(asset_name: str, current_location: int, num_locations: int = 5) -> bool:
    """
    Check if an asset should be created in the current code location.

    :param asset_name: The name of the asset
    :param current_location: The current code location number (1-5)
    :param num_locations: Total number of code locations (default 5)
    :return: True if asset should be created in this location
    """
    return get_asset_location(asset_name, num_locations) == current_location
