"""
Validation module for allocation results
Ensures LLM outputs meet hard constraints
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from utils import check_time_conflict, has_required_capabilities, parse_datetime


class AllocationValidator:
    """Validates allocation results against constraints"""

    def __init__(self, config):
        self.config = config
        self.validation_errors = []
        self.validation_warnings = []

    def validate_allocation(self, allocation_result: Dict[str, Any]) -> bool:
        """
        Validate an entire allocation result

        Args:
            allocation_result: Dictionary containing allocations

        Returns:
            True if valid, False otherwise
        """
        self.validation_errors = []
        self.validation_warnings = []

        allocations = allocation_result.get("allocations", [])

        print("\n🔍 Validating allocations...")

        # Validate each driver's assignments
        for allocation in allocations:
            self._validate_driver_allocation(allocation)

        # Cross-validation: check for duplicate order assignments
        self._check_duplicate_assignments(allocations)

        # Print validation results
        if self.validation_errors:
            print(f"\n❌ VALIDATION FAILED: {len(self.validation_errors)} errors found")
            for error in self.validation_errors:
                print(f"  • {error}")
            return False
        elif self.validation_warnings:
            print(f"\n⚠️  VALIDATION PASSED with {len(self.validation_warnings)} warnings:")
            for warning in self.validation_warnings:
                print(f"  • {warning}")
            return True
        else:
            print("\n✅ VALIDATION PASSED: No errors found")
            return True

    def _validate_driver_allocation(self, allocation: Dict):
        """Validate a single driver's allocation"""
        driver = allocation.get("driver", {})
        orders = allocation.get("orders", [])

        driver_id = driver.get("driver_id", "Unknown")

        # Check capacity constraint
        max_orders = driver.get("max_orders_per_day", 0)
        if len(orders) > max_orders:
            self.validation_errors.append(
                f"Driver {driver_id} assigned {len(orders)} orders, "
                f"exceeds capacity of {max_orders}"
            )

        # Check capability constraints
        for order in orders:
            if not has_required_capabilities(driver, order):
                order_id = order.get("order_id", "Unknown")
                order_tags = order.get("tags", [])
                driver_capabilities = driver.get("capabilities", [])

                self.validation_errors.append(
                    f"Driver {driver_id} lacks required capabilities for order {order_id}. "
                    f"Order tags: {order_tags}, Driver capabilities: {driver_capabilities}"
                )

        # Check time conflicts
        if len(orders) > 1:
            conflicts = self._find_time_conflicts_in_orders(orders)
            for order1, order2 in conflicts:
                self.validation_errors.append(
                    f"Driver {driver_id} has time conflict between "
                    f"orders {order1.get('order_id')} and {order2.get('order_id')}"
                )

        # Check regional efficiency (warning only)
        self._check_regional_efficiency(driver, orders)

    def _find_time_conflicts_in_orders(self, orders: List[Dict]) -> List[tuple]:
        """Find time conflicts within a list of orders"""
        conflicts = []

        for i, order1 in enumerate(orders):
            for order2 in orders[i+1:]:
                if check_time_conflict(order1, order2):
                    conflicts.append((order1, order2))

        return conflicts

    def _check_regional_efficiency(self, driver: Dict, orders: List[Dict]):
        """Check if orders match driver's preferred region (warning only)"""
        preferred_region = driver.get("preferred_region")
        driver_id = driver.get("driver_id", "Unknown")

        mismatched_orders = []
        for order in orders:
            order_region = order.get("region")
            if order_region != preferred_region:
                mismatched_orders.append(order.get("order_id"))

        if mismatched_orders:
            mismatch_ratio = len(mismatched_orders) / len(orders)
            if mismatch_ratio > 0.5:
                self.validation_warnings.append(
                    f"Driver {driver_id} (prefers {preferred_region}) has {len(mismatched_orders)}/{len(orders)} "
                    f"orders outside preferred region: {mismatched_orders[:3]}{'...' if len(mismatched_orders) > 3 else ''}"
                )

    def _check_duplicate_assignments(self, allocations: List[Dict]):
        """Check if any order is assigned to multiple drivers"""
        assigned_orders = {}

        for allocation in allocations:
            driver_id = allocation.get("driver", {}).get("driver_id", "Unknown")
            orders = allocation.get("orders", [])

            for order in orders:
                order_id = order.get("order_id", "Unknown")

                if order_id in assigned_orders:
                    self.validation_errors.append(
                        f"Order {order_id} assigned to multiple drivers: "
                        f"{assigned_orders[order_id]} and {driver_id}"
                    )
                else:
                    assigned_orders[order_id] = driver_id

    def get_errors(self) -> List[str]:
        """Get validation errors"""
        return self.validation_errors

    def get_warnings(self) -> List[str]:
        """Get validation warnings"""
        return self.validation_warnings


def validate_order_feasibility(order: Dict, driver: Dict,
                               assigned_orders: List[Dict],
                               config) -> tuple[bool, str]:
    """
    Check if an order can feasibly be assigned to a driver

    Args:
        order: Order to check
        driver: Driver to assign to
        assigned_orders: Orders already assigned to this driver
        config: Configuration object

    Returns:
        Tuple of (is_feasible, reason)
    """
    # Check capacity
    max_capacity = driver.get("max_orders_per_day", 0)
    if len(assigned_orders) >= max_capacity:
        return False, f"Driver at capacity ({len(assigned_orders)}/{max_capacity})"

    # Check capabilities
    if not has_required_capabilities(driver, order):
        order_tags = order.get("tags", [])
        driver_caps = driver.get("capabilities", [])
        return False, f"Missing required capabilities. Order needs: {order_tags}, Driver has: {driver_caps}"

    # Check time conflicts
    for assigned_order in assigned_orders:
        if check_time_conflict(order, assigned_order):
            return False, f"Time conflict with order {assigned_order.get('order_id')}"

    # Check if enough buffer time exists
    for assigned_order in assigned_orders:
        if not has_sufficient_buffer(order, assigned_order, config):
            return False, f"Insufficient buffer time with order {assigned_order.get('order_id')}"

    return True, "Feasible"


def has_sufficient_buffer(order1: Dict, order2: Dict, config) -> bool:
    """
    Check if there's sufficient buffer time between two orders

    Args:
        order1, order2: Orders to check
        config: Configuration object with min_buffer_time_minutes

    Returns:
        True if sufficient buffer exists
    """
    min_buffer = config.min_buffer_time_minutes

    teardown1 = parse_datetime(order1["teardown_time"])
    pickup2 = parse_datetime(order2["pickup_time"])
    teardown2 = parse_datetime(order2["teardown_time"])
    pickup1 = parse_datetime(order1["pickup_time"])

    # Check both directions
    if teardown1 <= pickup2:
        buffer_minutes = (pickup2 - teardown1).total_seconds() / 60
        return buffer_minutes >= min_buffer
    elif teardown2 <= pickup1:
        buffer_minutes = (pickup1 - teardown2).total_seconds() / 60
        return buffer_minutes >= min_buffer

    return False
