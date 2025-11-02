#!/usr/bin/env python3
"""
Quick data analysis script to understand constraints
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from io import StringIO

# Load data from data directory
data_dir = Path(__file__).parent.parent / 'data'
output_dir = Path(__file__).parent.parent / 'output'

with open(data_dir / 'orders.json', 'r') as f:
    orders = json.load(f)

with open(data_dir / 'drivers.json', 'r') as f:
    drivers = json.load(f)

# Capture output to both console and file
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

# Count wedding orders (with or without VIP)
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

# Count by event type
event_count = defaultdict(int)
for order in orders:
    event_type = order.get('event_type') or 'None'
    event_count[event_type] += 1

print_dual("\nOrders by event type:")
for event, count in sorted(event_count.items(), key=lambda x: x[1], reverse=True):
    print_dual(f"  {event}: {count}")

# Analyze time distribution
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

# Capacity distribution
capacity_dist = defaultdict(int)
for driver in drivers:
    capacity = driver.get('max_orders_per_day', 0)
    capacity_dist[capacity] += 1

print_dual("\nCapacity distribution:")
for cap, count in sorted(capacity_dist.items()):
    print_dual(f"  {cap} orders/day: {count} drivers")

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

# Save to file with timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file = output_dir / f"data_analysis_{timestamp}.txt"
with open(output_file, 'w') as f:
    f.write(output_buffer.getvalue())

print(f"\n✅ Analysis saved to: {output_file}")

# Also save as latest
latest_file = output_dir / "data_analysis_latest.txt"
with open(latest_file, 'w') as f:
    f.write(output_buffer.getvalue())

print(f"✅ Also saved as: {latest_file}")