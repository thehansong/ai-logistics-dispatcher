"""
Output formatting for allocation results
Handles text-based output and optional visualization
"""

from typing import Dict, Any, List
from datetime import datetime


def format_allocation_output(results: Dict[str, Any]):
    """
    Format and print allocation results in a human-readable format

    Args:
        results: Dictionary containing allocation results
    """
    print("\n" + "=" * 80)
    print(" " * 20 + "SMART DELIVERY ALLOCATOR - RESULTS")
    print("=" * 80 + "\n")

    allocations = results.get("allocations", [])
    unallocated = results.get("unallocated_orders", [])
    metrics = results.get("metrics", {})
    warnings = results.get("warnings", [])

    # Print summary metrics
    _print_summary_metrics(metrics, len(allocations), len(unallocated))

    # Print driver allocations
    if allocations:
        print("\n" + "-" * 80)
        print("DRIVER ALLOCATIONS")
        print("-" * 80 + "\n")
        for allocation in allocations:
            _print_driver_allocation(allocation)

    # Print unallocated orders
    if unallocated:
        print("\n" + "-" * 80)
        print("UNALLOCATED ORDERS")
        print("-" * 80 + "\n")
        for order in unallocated:
            _print_unallocated_order(order)

    # Print warnings
    if warnings:
        print("\n" + "-" * 80)
        print("⚠️  WARNINGS & CONFLICTS")
        print("-" * 80 + "\n")
        for warning in warnings:
            print(f"  • {warning}")

    print("\n" + "=" * 80 + "\n")


def _print_summary_metrics(metrics: Dict, allocated_count: int, unallocated_count: int):
    """Print summary metrics"""
    total_orders = allocated_count + unallocated_count
    allocation_rate = (allocated_count / total_orders * 100) if total_orders > 0 else 0

    print(f"📊 SUMMARY METRICS")
    print(f"  Total Orders: {total_orders}")
    print(f"  Allocated: {allocated_count} ({allocation_rate:.1f}%)")
    print(f"  Unallocated: {unallocated_count}")

    if metrics:
        if "total_drivers_used" in metrics:
            print(f"  Drivers Used: {metrics['total_drivers_used']}")
        if "average_utilization" in metrics:
            print(f"  Avg Driver Utilization: {metrics['average_utilization']:.1f}%")
        if "regional_distribution" in metrics:
            print(f"\n  Regional Distribution:")
            for region, count in metrics["regional_distribution"].items():
                print(f"    {region}: {count} orders")


def _print_driver_allocation(allocation: Dict):
    """Print individual driver allocation"""
    driver = allocation.get("driver", {})
    orders = allocation.get("orders", [])
    reasoning = allocation.get("reasoning", "")
    utilization = allocation.get("utilization", 0)

    driver_id = driver.get("driver_id", "Unknown")
    driver_name = driver.get("name", "Unknown")
    preferred_region = driver.get("preferred_region", "Unknown")
    max_orders = driver.get("max_orders_per_day", 0)
    capabilities = driver.get("capabilities", [])

    print(f"🚚 DRIVER: {driver_id} - {driver_name}")
    print(f"   Region: {preferred_region} | Capacity: {len(orders)}/{max_orders} orders | "
          f"Utilization: {utilization:.0f}%")
    if capabilities:
        print(f"   Capabilities: {', '.join(capabilities)}")

    print(f"\n   Assigned Orders ({len(orders)}):")
    for i, order in enumerate(orders, 1):
        order_id = order.get("order_id", "Unknown")
        address = order.get("address", "Unknown")
        region = order.get("region", "Unknown")
        tags = order.get("tags", [])
        pax_count = order.get("pax_count", 0)
        setup_time = order.get("setup_time", "")

        # Format time
        if setup_time:
            try:
                dt = datetime.fromisoformat(setup_time)
                time_str = dt.strftime("%H:%M")
            except:
                time_str = setup_time
        else:
            time_str = "N/A"

        tags_str = f" [{', '.join(tags)}]" if tags else ""
        print(f"   {i}. {order_id} - {address[:50]}...")
        print(f"      Setup: {time_str} | Region: {region} | Pax: {pax_count}{tags_str}")

        # Print order reasoning if available
        order_reasoning = order.get("reasoning", "")
        if order_reasoning:
            print(f"      → {order_reasoning}")

    if reasoning:
        print(f"\n   Overall Reasoning: {reasoning}")

    print()


def _print_unallocated_order(order: Dict):
    """Print unallocated order details"""
    order_id = order.get("order_id", "Unknown")
    address = order.get("address", "Unknown")
    tags = order.get("tags", [])
    reason = order.get("unallocation_reason", "No reason provided")

    tags_str = f" [{', '.join(tags)}]" if tags else ""
    print(f"  ❌ {order_id} - {address[:60]}{tags_str}")
    print(f"     Reason: {reason}\n")


def save_text_output(results: Dict[str, Any], output_file: str = "allocation_output.txt"):
    """
    Save allocation results to a text file

    Args:
        results: Allocation results dictionary
        output_file: Output file path
    """
    import sys
    from io import StringIO

    # Capture print output
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    format_allocation_output(results)

    # Restore stdout
    sys.stdout = old_stdout

    # Write to file
    with open(output_file, 'w') as f:
        f.write(captured_output.getvalue())

    print(f"Text output saved to {output_file}")


def generate_map_visualization(results: Dict[str, Any], output_file: str = "allocation_map.html"):
    """
    Generate an HTML map visualization of allocations (optional)

    Args:
        results: Allocation results dictionary
        output_file: Output HTML file path
    """
    try:
        import folium
        from folium.plugins import MarkerCluster
    except ImportError:
        print("⚠️  Folium not installed. Skipping map visualization.")
        print("   Install with: pip install folium")
        return

    # TODO: Implement map visualization in Phase 4
    print(f"Map visualization will be implemented in Phase 4")
