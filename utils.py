"""
Utility functions for data handling, validation, and calculations
"""

import json
import math
from datetime import datetime
from typing import List, Dict, Any, Tuple


def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """Load and parse JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")


def validate_data(orders: List[Dict], drivers: List[Dict]):
    """
    Validate that orders and drivers have required fields

    Args:
        orders: List of order dictionaries
        drivers: List of driver dictionaries

    Raises:
        ValueError: If required fields are missing
    """
    required_order_fields = ["order_id", "pickup_time", "setup_time", "teardown_time", "region"]
    required_driver_fields = ["driver_id", "name", "preferred_region", "max_orders_per_day"]

    # Check orders
    for i, order in enumerate(orders):
        for field in required_order_fields:
            if field not in order:
                raise ValueError(f"Order at index {i} missing required field: {field}")

    # Check drivers
    for i, driver in enumerate(drivers):
        for field in required_driver_fields:
            if field not in driver:
                raise ValueError(f"Driver at index {i} missing required field: {field}")

    print("✓ Data validation passed")


def parse_datetime(dt_string: str) -> datetime:
    """Parse ISO datetime string"""
    return datetime.fromisoformat(dt_string)


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate haversine distance between two points in kilometers

    Args:
        lat1, lng1: First point coordinates
        lat2, lng2: Second point coordinates

    Returns:
        Distance in kilometers
    """
    # Radius of Earth in kilometers
    R = 6371

    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)

    # Haversine formula
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * \
        math.sin(delta_lng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def check_time_conflict(order1: Dict, order2: Dict) -> bool:
    """
    Check if two orders have overlapping time windows

    Args:
        order1, order2: Order dictionaries with pickup_time and teardown_time

    Returns:
        True if orders conflict in time
    """
    pickup1 = parse_datetime(order1["pickup_time"])
    teardown1 = parse_datetime(order1["teardown_time"])
    pickup2 = parse_datetime(order2["pickup_time"])
    teardown2 = parse_datetime(order2["teardown_time"])

    # Orders conflict if they overlap
    return not (teardown1 <= pickup2 or teardown2 <= pickup1)


def has_required_capabilities(driver: Dict, order: Dict) -> bool:
    """
    Check if driver has capabilities required for order

    Args:
        driver: Driver dictionary
        order: Order dictionary with tags

    Returns:
        True if driver can handle the order
    """
    order_tags = order.get("tags", [])
    driver_capabilities = driver.get("capabilities", [])

    # Check for special requirements
    if "wedding" in order_tags or "vip" in order_tags:
        # Need wedding capability for wedding orders
        if "wedding" in order_tags and "wedding" not in driver_capabilities:
            return False
        # VIP orders should have VIP-capable drivers (preferred but not hard requirement)
        if "vip" in order_tags and "vip" not in driver_capabilities:
            return False

    if "corporate" in order_tags:
        # Corporate events prefer corporate-experienced drivers
        if "corporate" not in driver_capabilities:
            return False

    return True


def get_order_priority(order: Dict) -> int:
    """
    Calculate priority score for an order (higher = more important)

    Priority levels:
    1. VIP + Wedding (highest)
    2. VIP only
    3. Wedding only
    4. Corporate with early_setup
    5. Corporate
    6. Regular orders (lowest)

    Args:
        order: Order dictionary

    Returns:
        Priority score (0-100)
    """
    tags = order.get("tags", [])

    if "vip" in tags and "wedding" in tags:
        return 100
    elif "vip" in tags:
        return 90
    elif "wedding" in tags:
        return 80
    elif "corporate" in tags and "early_setup" in tags:
        return 60
    elif "corporate" in tags:
        return 50
    else:
        return 30


def categorize_orders_by_priority(orders: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Categorize orders into priority tiers

    Args:
        orders: List of order dictionaries

    Returns:
        Dictionary with priority tiers as keys
    """
    categories = {
        "vip_wedding": [],
        "vip": [],
        "wedding": [],
        "corporate": [],
        "regular": []
    }

    for order in orders:
        tags = order.get("tags", [])

        if "vip" in tags and "wedding" in tags:
            categories["vip_wedding"].append(order)
        elif "vip" in tags:
            categories["vip"].append(order)
        elif "wedding" in tags:
            categories["wedding"].append(order)
        elif "corporate" in tags:
            categories["corporate"].append(order)
        else:
            categories["regular"].append(order)

    return categories


def get_region_stats(orders: List[Dict], drivers: List[Dict]) -> Dict[str, Any]:
    """
    Calculate statistics by region

    Args:
        orders: List of orders
        drivers: List of drivers

    Returns:
        Dictionary with regional statistics
    """
    stats = {}

    # Count orders by region
    order_counts = {}
    for order in orders:
        region = order.get("region")
        order_counts[region] = order_counts.get(region, 0) + 1

    # Count drivers by preferred region
    driver_counts = {}
    for driver in drivers:
        region = driver.get("preferred_region")
        driver_counts[region] = driver_counts.get(region, 0) + 1

    # Combine stats
    all_regions = set(list(order_counts.keys()) + list(driver_counts.keys()))
    for region in all_regions:
        stats[region] = {
            "orders": order_counts.get(region, 0),
            "drivers": driver_counts.get(region, 0)
        }

    return stats
