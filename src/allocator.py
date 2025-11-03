#!/usr/bin/env python3
"""
Smart Delivery Allocator - AI-powered catering order allocation system
"""

import json
import sys
from datetime import datetime
from typing import List, Dict, Any

from config import Config
from utils import load_json_file, validate_data
from output_formatter import format_allocation_output
from preprocessor import DataPreprocessor
from ai_allocator import AIAllocator
from validator import AllocationValidator


class DeliveryAllocator:
    """Main allocation engine that orchestrates the AI-powered allocation process"""

    def __init__(self, orders_file: str, drivers_file: str):
        """
        Initialize the allocator with order and driver data

        Args:
            orders_file: Path to orders.json
            drivers_file: Path to drivers.json
        """
        self.orders = load_json_file(orders_file)
        self.drivers = load_json_file(drivers_file)
        self.config = Config()

        # Validate data
        validate_data(self.orders, self.drivers)

        print(f"Loaded {len(self.orders)} orders and {len(self.drivers)} drivers")

        # Initialize preprocessor
        self.preprocessor = DataPreprocessor(self.orders, self.drivers)
        self.preprocessed_data = None

    def allocate(self) -> Dict[str, Any]:
        """
        Main allocation logic - orchestrates the multi-stage allocation process

        Returns:
            Dictionary containing allocation results, metrics, and warnings
        """
        print("\n=== Starting allocation process ===\n")

        # Step 1: Preprocess data
        self.preprocessed_data = self.preprocessor.preprocess()

        # Step 2: Run AI allocation
        ai_allocator = AIAllocator(self.config)
        ai_results = ai_allocator.allocate_orders(
            orders=self.orders,
            drivers=self.drivers,
            categorized_orders=self.preprocessed_data["categorized_orders"],
            categorized_drivers=self.preprocessed_data["categorized_drivers"]
        )

        # Step 3: Validate allocations
        validator = AllocationValidator(self.config)
        allocation_result = {
            "allocations": ai_results["allocations"],
            "unallocated_orders": ai_results["unallocated_orders"],
            "metrics": self.preprocessed_data["stats"],
            "warnings": []
        }

        # Validate
        is_valid = validator.validate_allocation(allocation_result)

        # Add validation warnings
        allocation_result["warnings"].extend(validator.get_warnings())

        # Add preprocessing constraint warnings
        for warning in self.preprocessed_data["constraints"]["warnings"]:
            allocation_result["warnings"].append(warning)

        # Update metrics with allocation stats
        allocation_result["metrics"]["total_allocated"] = len(ai_results["allocated_order_ids"])
        allocation_result["metrics"]["total_unallocated"] = len(ai_results["unallocated_orders"])
        allocation_result["metrics"]["allocation_rate"] = (
            len(ai_results["allocated_order_ids"]) / len(self.orders) * 100
            if len(self.orders) > 0 else 0
        )
        allocation_result["metrics"]["total_drivers_used"] = len(ai_results["allocations"])

        # Calculate average driver utilization
        if ai_results["allocations"]:
            avg_util = sum(a["utilization"] for a in ai_results["allocations"]) / len(ai_results["allocations"])
            allocation_result["metrics"]["average_utilization"] = avg_util

        # Regional distribution
        regional_dist = {}
        for allocation in ai_results["allocations"]:
            for order in allocation["orders"]:
                region = order.get("region", "unknown")
                regional_dist[region] = regional_dist.get(region, 0) + 1
        allocation_result["metrics"]["regional_distribution"] = regional_dist

        return allocation_result

    def save_results(self, results: Dict[str, Any], output_file: str = "allocation_output.json"):
        """Save allocation results to file"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_file}")


def main():
    """Main entry point"""
    # Default file paths (relative to project root)
    orders_file = "data/test_scenarios/original_scenario/orders.json"
    drivers_file = "data/drivers/drivers.json"

    # Allow command line overrides
    if len(sys.argv) > 2:
        orders_file = sys.argv[1]
        drivers_file = sys.argv[2]

    try:
        # Initialize allocator
        allocator = DeliveryAllocator(orders_file, drivers_file)

        # Run allocation
        results = allocator.allocate()

        # Format and display output
        format_allocation_output(results)

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"output/allocation_output_{timestamp}.json"

        # Save to file (in output directory with timestamp)
        allocator.save_results(results, output_file)

        # Also save as latest (for convenience)
        allocator.save_results(results, "output/allocation_output_latest.json")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
