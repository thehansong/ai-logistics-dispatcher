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

        # Placeholder for Phase 3 - AI allocation will go here
        allocation_results = {
            "allocations": [],
            "unallocated_orders": self.orders,  # For now, all orders unallocated
            "metrics": self.preprocessed_data["stats"],
            "warnings": []
        }

        # Add constraints as warnings
        for warning in self.preprocessed_data["constraints"]["warnings"]:
            allocation_results["warnings"].append(warning)

        return allocation_results

    def save_results(self, results: Dict[str, Any], output_file: str = "allocation_output.json"):
        """Save allocation results to file"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_file}")


def main():
    """Main entry point"""
    # Default file paths (relative to project root)
    orders_file = "data/orders.json"
    drivers_file = "data/drivers.json"

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

        # Save to file (in output directory)
        allocator.save_results(results, "output/allocation_output.json")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
