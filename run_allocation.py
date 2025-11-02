#!/usr/bin/env python3
"""
Main runner script that executes both data analysis and allocation in one command.
Creates a timestamped output folder for each run.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from allocator import DeliveryAllocator
from config import Config
from utils import load_json_file
from output_formatter import format_allocation_output
import json
from io import StringIO
from collections import defaultdict


def run_data_analysis(output_dir: Path):
    """Run data analysis and save to output directory"""
    print("=" * 80)
    print("STEP 1: DATA ANALYSIS")
    print("=" * 80 + "\n")

    # Load data
    data_dir = Path(__file__).parent / 'data'
    with open(data_dir / 'orders.json', 'r') as f:
        orders = json.load(f)
    with open(data_dir / 'drivers.json', 'r') as f:
        drivers = json.load(f)

    # Capture output
    output_buffer = StringIO()

    def print_dual(text=""):
        """Print to both console and buffer"""
        print(text)
        output_buffer.write(text + "\n")

    print_dual("=" * 80)
    print_dual("DATA ANALYSIS REPORT")
    print_dual("=" * 80)

    # Orders analysis
    print_dual("\n📦 ORDERS ANALYSIS")
    print_dual(f"Total orders: {len(orders)}")

    # Count by tags
    tags_count = defaultdict(int)
    for order in orders:
        for tag in order.get('tags', []):
            tags_count[tag] += 1

    print_dual("\nOrders by tag:")
    for tag, count in sorted(tags_count.items(), key=lambda x: x[1], reverse=True):
        print_dual(f"  {tag}: {count}")

    # Count wedding orders
    wedding_orders = [o for o in orders if 'wedding' in o.get('tags', [])]
    vip_wedding_orders = [o for o in orders if 'wedding' in o.get('tags', []) and 'vip' in o.get('tags', [])]
    print_dual(f"\nTotal wedding orders: {len(wedding_orders)}")
    print_dual(f"VIP wedding orders: {len(vip_wedding_orders)}")

    # Count by region
    region_count = defaultdict(int)
    for order in orders:
        region_count[order.get('region')] += 1

    print_dual("\nOrders by region:")
    for region, count in sorted(region_count.items(), key=lambda x: x[1], reverse=True):
        print_dual(f"  {region}: {count}")

    # Time distribution
    print_dual("\nTime distribution:")
    time_slots = defaultdict(int)
    for order in orders:
        setup_time = datetime.fromisoformat(order['setup_time'])
        hour = setup_time.hour
        if hour < 12:
            time_slots['morning (before 12pm)'] += 1
        elif hour < 18:
            time_slots['afternoon (12pm-6pm)'] += 1
        else:
            time_slots['evening (after 6pm)'] += 1

    for slot, count in time_slots.items():
        print_dual(f"  {slot}: {count}")

    # TBD addresses
    tbd_orders = [o for o in orders if o.get('postal_code') == '000000']
    print_dual(f"\nOrders with TBD address: {len(tbd_orders)}")

    print_dual("\n" + "-" * 80)
    print_dual("\n🚚 DRIVERS ANALYSIS")
    print_dual(f"Total drivers: {len(drivers)}")

    # Count by capabilities
    cap_count = defaultdict(int)
    for driver in drivers:
        for cap in driver.get('capabilities', []):
            cap_count[cap] += 1

    print_dual("\nDrivers by capability:")
    for cap, count in sorted(cap_count.items(), key=lambda x: x[1], reverse=True):
        print_dual(f"  {cap}: {count}")

    # Wedding-capable drivers
    wedding_drivers = [d for d in drivers if 'wedding' in d.get('capabilities', [])]
    print_dual(f"\nWedding-capable drivers: {len(wedding_drivers)}")

    # Count by preferred region
    driver_region_count = defaultdict(int)
    for driver in drivers:
        driver_region_count[driver.get('preferred_region')] += 1

    print_dual("\nDrivers by preferred region:")
    for region, count in sorted(driver_region_count.items(), key=lambda x: x[1], reverse=True):
        print_dual(f"  {region}: {count}")

    # Capacity analysis
    total_capacity = sum(d.get('max_orders_per_day', 0) for d in drivers)
    avg_capacity = total_capacity / len(drivers)
    print_dual(f"\nTotal driver capacity: {total_capacity} orders/day")
    print_dual(f"Average capacity per driver: {avg_capacity:.1f} orders/day")

    print_dual("\n" + "-" * 80)
    print_dual("\n⚠️  KEY CONSTRAINTS")
    print_dual(f"  • Wedding orders: {len(wedding_orders)}")
    print_dual(f"  • Wedding-capable drivers: {len(wedding_drivers)}")
    print_dual(f"  • Ratio: {len(wedding_orders)/len(wedding_drivers):.1f} orders per wedding driver")
    print_dual(f"\n  • Total orders: {len(orders)}")
    print_dual(f"  • Total capacity: {total_capacity}")
    print_dual(f"  • Utilization needed: {len(orders)/total_capacity*100:.1f}%")

    # Regional balance
    print_dual("\nRegional balance issues:")
    for region in set(region_count.keys()) | set(driver_region_count.keys()):
        order_count = region_count.get(region, 0)
        driver_count = driver_region_count.get(region, 0)
        if driver_count > 0:
            ratio = order_count / driver_count
            status = "⚠️ IMBALANCED" if ratio > 6 or ratio < 2 else "✓ OK"
            print_dual(f"  {region}: {order_count} orders / {driver_count} drivers = {ratio:.1f} orders/driver {status}")
        else:
            print_dual(f"  {region}: {order_count} orders / NO DRIVERS ⚠️ CRITICAL")

    print_dual("\n" + "=" * 80)

    # Save to file
    analysis_file = output_dir / "01_data_analysis.txt"
    with open(analysis_file, 'w') as f:
        f.write(output_buffer.getvalue())

    print(f"\n✅ Analysis saved to: {analysis_file}\n")


def run_allocation(output_dir: Path):
    """Run allocation and save to output directory"""
    print("\n" + "=" * 80)
    print("STEP 2: AI ALLOCATION")
    print("=" * 80 + "\n")

    # Default file paths
    orders_file = "data/orders.json"
    drivers_file = "data/drivers.json"

    try:
        # Initialize allocator
        allocator = DeliveryAllocator(orders_file, drivers_file)

        # Run allocation
        results = allocator.allocate()

        # Format and display output
        format_allocation_output(results)

        # Save JSON results
        json_file = output_dir / "02_allocation_results.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Results saved to: {json_file}")

        return results

    except Exception as e:
        print(f"❌ Error during allocation: {e}")
        raise


def create_summary(output_dir: Path, results: dict):
    """Create a summary file with key metrics"""
    summary_file = output_dir / "00_SUMMARY.txt"

    metrics = results.get("metrics", {})
    allocations = results.get("allocations", [])
    unallocated = results.get("unallocated_orders", [])
    warnings = results.get("warnings", [])

    total_orders = metrics.get("total_orders", 0)
    allocated = metrics.get("total_allocated", 0)
    allocation_rate = metrics.get("allocation_rate", 0)

    with open(summary_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("ALLOCATION RUN SUMMARY\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Output Directory: {output_dir.name}\n\n")

        f.write("=" * 80 + "\n")
        f.write("KEY METRICS\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"📊 ALLOCATION SUCCESS\n")
        f.write(f"  Total Orders: {total_orders}\n")
        f.write(f"  Allocated: {allocated} ({allocation_rate:.1f}%)\n")
        f.write(f"  Unallocated: {len(unallocated)}\n")
        f.write(f"  Drivers Used: {len(allocations)}\n\n")

        if allocations:
            avg_util = metrics.get("average_utilization", 0)
            f.write(f"🚚 DRIVER UTILIZATION\n")
            f.write(f"  Average: {avg_util:.1f}%\n")
            f.write(f"  Top 5 Drivers:\n")
            sorted_drivers = sorted(allocations, key=lambda x: x["utilization"], reverse=True)[:5]
            for i, alloc in enumerate(sorted_drivers, 1):
                driver_name = alloc["driver"].get("name", "Unknown")
                driver_id = alloc["driver"].get("driver_id", "Unknown")
                util = alloc["utilization"]
                order_count = len(alloc["orders"])
                f.write(f"    {i}. {driver_name} ({driver_id}): {util:.0f}% - {order_count} orders\n")
            f.write("\n")

        regional_dist = metrics.get("regional_distribution", {})
        if regional_dist:
            f.write(f"🗺️  REGIONAL DISTRIBUTION\n")
            for region, count in sorted(regional_dist.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {region}: {count} orders\n")
            f.write("\n")

        if warnings:
            f.write(f"⚠️  WARNINGS ({len(warnings)})\n")
            for warning in warnings[:5]:  # Show first 5
                f.write(f"  • {warning}\n")
            if len(warnings) > 5:
                f.write(f"  ... and {len(warnings) - 5} more\n")
            f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("FILES GENERATED\n")
        f.write("=" * 80 + "\n\n")
        f.write("  00_SUMMARY.txt             - This summary file\n")
        f.write("  01_data_analysis.txt       - Data statistics and constraints\n")
        f.write("  02_allocation_results.json - Complete allocation results (JSON)\n\n")

        f.write("=" * 80 + "\n")

    print(f"\n✅ Summary saved to: {summary_file}")


def main():
    """Main entry point"""
    print("\n🚀 SMART DELIVERY ALLOCATOR - FULL RUN\n")

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path("output") / f"run_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📁 Output directory: {output_dir}\n")

    try:
        # Step 1: Data Analysis
        run_data_analysis(output_dir)

        # Step 2: Allocation
        results = run_allocation(output_dir)

        # Step 3: Create Summary
        create_summary(output_dir, results)

        # Also update "latest" symlink/copy
        latest_dir = Path("output") / "latest"
        if latest_dir.exists():
            if latest_dir.is_symlink() or latest_dir.is_dir():
                if latest_dir.is_symlink():
                    latest_dir.unlink()
                else:
                    shutil.rmtree(latest_dir)

        # Copy to latest
        shutil.copytree(output_dir, latest_dir)

        print("\n" + "=" * 80)
        print("✅ COMPLETE!")
        print("=" * 80)
        print(f"\n📂 All outputs saved to: {output_dir}")
        print(f"📂 Latest run also available at: output/latest/")
        print("\nFiles generated:")
        print("  - 00_SUMMARY.txt           (Quick overview)")
        print("  - 01_data_analysis.txt     (Data insights)")
        print("  - 02_allocation_results.json (Full results)")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()