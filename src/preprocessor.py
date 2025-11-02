"""
Data preprocessing module for Smart Delivery Allocator
Handles data analysis, categorization, and constraint preparation
"""

from typing import Dict, List, Any, Tuple
from collections import defaultdict
from datetime import datetime
from utils import (
    get_order_priority,
    categorize_orders_by_priority,
    has_required_capabilities,
    check_time_conflict,
    parse_datetime
)


class DataPreprocessor:
    """Preprocesses order and driver data for allocation"""

    def __init__(self, orders: List[Dict], drivers: List[Dict]):
        self.orders = orders
        self.drivers = drivers
        self.stats = None

    def preprocess(self) -> Dict[str, Any]:
        """
        Main preprocessing function

        Returns:
            Dictionary containing categorized data and statistics
        """
        print("\n🔍 Preprocessing data...")

        # Categorize orders by priority
        categorized_orders = categorize_orders_by_priority(self.orders)

        # Sort orders within each category by priority score
        for category in categorized_orders:
            categorized_orders[category].sort(
                key=lambda x: get_order_priority(x),
                reverse=True
            )

        # Categorize drivers by capabilities
        categorized_drivers = self._categorize_drivers()

        # Generate statistics
        stats = self._generate_statistics(categorized_orders, categorized_drivers)
        self.stats = stats

        # Identify critical constraints
        constraints = self._identify_constraints(categorized_orders, categorized_drivers)

        # Print summary
        self._print_preprocessing_summary(stats, constraints)

        return {
            "categorized_orders": categorized_orders,
            "categorized_drivers": categorized_drivers,
            "stats": stats,
            "constraints": constraints,
            "all_orders": self.orders,
            "all_drivers": self.drivers
        }

    def _categorize_drivers(self) -> Dict[str, List[Dict]]:
        """Categorize drivers by their capabilities"""
        categorized = {
            "wedding_capable": [],
            "corporate_capable": [],
            "general": []
        }

        for driver in self.drivers:
            capabilities = driver.get("capabilities", [])

            if "wedding" in capabilities or "vip" in capabilities:
                categorized["wedding_capable"].append(driver)
            elif "corporate" in capabilities or "seminars" in capabilities:
                categorized["corporate_capable"].append(driver)
            else:
                categorized["general"].append(driver)

        return categorized

    def _generate_statistics(
        self,
        categorized_orders: Dict[str, List],
        categorized_drivers: Dict[str, List]
    ) -> Dict[str, Any]:
        """Generate comprehensive statistics about the data"""

        # Order statistics
        total_orders = len(self.orders)
        wedding_orders = len(categorized_orders["vip_wedding"]) + \
                        len(categorized_orders["vip"]) + \
                        len(categorized_orders["wedding"])

        # Driver statistics
        total_drivers = len(self.drivers)
        wedding_drivers = len(categorized_drivers["wedding_capable"])
        total_capacity = sum(d.get("max_orders_per_day", 0) for d in self.drivers)

        # Regional statistics
        orders_by_region = defaultdict(int)
        for order in self.orders:
            orders_by_region[order.get("region")] += 1

        drivers_by_region = defaultdict(int)
        for driver in self.drivers:
            drivers_by_region[driver.get("preferred_region")] += 1

        # Time distribution
        time_distribution = self._analyze_time_distribution()

        return {
            "total_orders": total_orders,
            "total_drivers": total_drivers,
            "wedding_orders": wedding_orders,
            "wedding_drivers": wedding_drivers,
            "total_capacity": total_capacity,
            "utilization_rate": (total_orders / total_capacity * 100) if total_capacity > 0 else 0,
            "orders_by_region": dict(orders_by_region),
            "drivers_by_region": dict(drivers_by_region),
            "time_distribution": time_distribution,
            "priority_distribution": {
                "vip_wedding": len(categorized_orders["vip_wedding"]),
                "vip": len(categorized_orders["vip"]),
                "wedding": len(categorized_orders["wedding"]),
                "corporate": len(categorized_orders["corporate"]),
                "regular": len(categorized_orders["regular"])
            }
        }

    def _analyze_time_distribution(self) -> Dict[str, int]:
        """Analyze time distribution of orders"""
        distribution = defaultdict(int)

        for order in self.orders:
            try:
                setup_time = parse_datetime(order["setup_time"])
                hour = setup_time.hour

                if hour < 12:
                    distribution["morning"] += 1
                elif hour < 18:
                    distribution["afternoon"] += 1
                else:
                    distribution["evening"] += 1
            except:
                distribution["unknown"] += 1

        return dict(distribution)

    def _identify_constraints(
        self,
        categorized_orders: Dict[str, List],
        categorized_drivers: Dict[str, List]
    ) -> Dict[str, Any]:
        """Identify critical constraints and potential issues"""

        constraints = {
            "critical": [],
            "warnings": [],
            "info": []
        }

        # Check wedding capacity constraint
        wedding_orders_count = (
            len(categorized_orders["vip_wedding"]) +
            len(categorized_orders["vip"]) +
            len(categorized_orders["wedding"])
        )
        wedding_drivers_count = len(categorized_drivers["wedding_capable"])

        if wedding_orders_count > 0:
            wedding_capacity = sum(
                d.get("max_orders_per_day", 0)
                for d in categorized_drivers["wedding_capable"]
            )

            if wedding_orders_count > wedding_capacity:
                constraints["critical"].append(
                    f"Wedding orders ({wedding_orders_count}) exceed wedding driver capacity ({wedding_capacity})"
                )
            elif wedding_orders_count > wedding_drivers_count * 2:
                constraints["warnings"].append(
                    f"High wedding order load: {wedding_orders_count} orders for {wedding_drivers_count} drivers"
                )

        # Check regional imbalances
        for region in set(self.stats["orders_by_region"].keys()) | set(self.stats["drivers_by_region"].keys()):
            order_count = self.stats["orders_by_region"].get(region, 0)
            driver_count = self.stats["drivers_by_region"].get(region, 0)

            if order_count > 0 and driver_count == 0:
                constraints["warnings"].append(
                    f"Region '{region}' has {order_count} orders but no preferred drivers"
                )
            elif driver_count > 0:
                ratio = order_count / driver_count
                if ratio > 6:
                    constraints["warnings"].append(
                        f"Region '{region}' overloaded: {ratio:.1f} orders per driver"
                    )

        # Check time conflicts potential
        evening_orders = self.stats["time_distribution"].get("evening", 0)
        if evening_orders > len(self.drivers) * 0.7:
            constraints["info"].append(
                f"Many orders concentrated in evening ({evening_orders}), may cause time conflicts"
            )

        # Check TBD addresses
        tbd_count = sum(1 for o in self.orders if o.get("postal_code") == "000000")
        if tbd_count > 0:
            constraints["info"].append(
                f"{tbd_count} orders have TBD addresses (postal code 000000)"
            )

        return constraints

    def _print_preprocessing_summary(self, stats: Dict, constraints: Dict):
        """Print preprocessing summary"""
        print("\n📊 PREPROCESSING SUMMARY")
        print(f"  Orders: {stats['total_orders']}")
        print(f"  Drivers: {stats['total_drivers']}")
        print(f"  Total Capacity: {stats['total_capacity']} orders/day")
        print(f"  Required Utilization: {stats['utilization_rate']:.1f}%")

        print(f"\n  Priority Distribution:")
        for priority, count in stats["priority_distribution"].items():
            if count > 0:
                print(f"    {priority}: {count}")

        print(f"\n  Time Distribution:")
        for time_slot, count in stats["time_distribution"].items():
            print(f"    {time_slot}: {count}")

        # Print constraints
        if constraints["critical"]:
            print(f"\n  🚨 CRITICAL CONSTRAINTS:")
            for c in constraints["critical"]:
                print(f"    • {c}")

        if constraints["warnings"]:
            print(f"\n  ⚠️  WARNINGS:")
            for w in constraints["warnings"]:
                print(f"    • {w}")

        if constraints["info"]:
            print(f"\n  ℹ️  INFO:")
            for i in constraints["info"]:
                print(f"    • {i}")

        print()

    def get_compatible_drivers(self, order: Dict) -> List[Dict]:
        """
        Get list of drivers compatible with a specific order

        Args:
            order: Order dictionary

        Returns:
            List of compatible driver dictionaries
        """
        compatible = []

        for driver in self.drivers:
            if has_required_capabilities(driver, order):
                compatible.append(driver)

        return compatible

    def find_time_conflicts(self, orders: List[Dict]) -> List[Tuple[Dict, Dict]]:
        """
        Find all pairs of orders that have time conflicts

        Args:
            orders: List of order dictionaries

        Returns:
            List of tuples containing conflicting order pairs
        """
        conflicts = []

        for i, order1 in enumerate(orders):
            for order2 in orders[i+1:]:
                if check_time_conflict(order1, order2):
                    conflicts.append((order1, order2))

        return conflicts