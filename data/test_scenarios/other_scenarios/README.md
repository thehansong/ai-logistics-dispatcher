# Other Scenario Test Dataset

## Overview
This test dataset is designed to achieve **100% allocation success** with optimal conditions.

## Dataset Composition

### Orders (30 total)
- **6 VIP Weddings** - Highest priority orders
- **6 Regular Weddings** - Wedding capability required
- **6 VIP Corporate** - High priority corporate events
- **6 Regular Corporate** - Standard corporate events
- **6 Standard Orders** - No special requirements

### Drivers (50 total)
- **10 Wedding-capable with VIP** (DRV-001 to DRV-010)
  - Max capacity: 6 orders/day each
  - Capabilities: vip, wedding, large_events
  - Coverage: 2 per region

- **5 Wedding-capable** (DRV-011 to DRV-015)
  - Max capacity: 5 orders/day each
  - Capabilities: wedding, large_events
  - Coverage: 1 per region

- **10 Corporate-capable with VIP** (DRV-016 to DRV-025)
  - Max capacity: 6 orders/day each
  - Capabilities: vip, corporate, early_setup
  - Coverage: 2 per region

- **5 Corporate-capable** (DRV-026 to DRV-030)
  - Max capacity: 5 orders/day each
  - Capabilities: corporate
  - Coverage: 1 per region

- **20 General drivers** (DRV-031 to DRV-050)
  - Max capacity: 4 orders/day each
  - Capabilities: none (can handle standard orders)
  - Coverage: 4 per region

## Key Features

### ✅ Adequate Capacity
- **Wedding orders**: 12 total vs 15 wedding-capable drivers (1.25:1 ratio)
- **Corporate orders**: 12 total vs 15 corporate-capable drivers (1.25:1 ratio)
- **Total capacity**: 240 order slots vs 30 orders needed (8:1 ratio)

### ✅ No Time Conflicts
Orders are spread across the day:
- **Morning (6am-12pm)**: 12 orders
- **Afternoon (12pm-4pm)**: 12 orders
- **Evening (4pm-8pm)**: 6 orders

All orders have 4-hour windows with no overlaps.

### ✅ Regional Balance
Each region (north, south, east, west, central) has:
- 6 orders
- 10 drivers (2 wedding-VIP, 1 wedding, 2 corporate-VIP, 1 corporate, 4 general)

### ✅ Realistic Venues
All venues use real Singapore locations with valid postal codes.

## Expected Results

**Target Metrics:**
- ✅ **100% allocation rate** (30/30 orders assigned)
- ✅ **0 unallocated orders**
- ✅ **0 time conflicts**
- ✅ **0 capability mismatches**
- ✅ **High regional efficiency** (most drivers assigned to their home region)
- ✅ **Low driver utilization** (12-20% average - sustainable workload)

## How to Test

### Option 1: Run with test data directly
```bash
source venv/bin/activate
python run_allocation.py --orders data/test_scenarios/other_scenarios/orders.json --drivers data/test_scenarios/other_scenarios/drivers.json
```

### Option 2: Copy to main data folder
```bash
cp data/test_scenarios/other_scenarios/orders.json data/orders.json
cp data/test_scenarios/other_scenarios/drivers.json data/drivers.json
python run_allocation.py
```

## Validation Checklist

After running the test, verify:
- [ ] All 30 orders are allocated
- [ ] No validation errors or warnings
- [ ] VIP weddings allocated to wedding-capable drivers with VIP capability
- [ ] Regular weddings allocated to wedding-capable drivers
- [ ] Corporate orders allocated to corporate-capable drivers
- [ ] Standard orders allocated to any available driver
- [ ] No time conflicts in driver schedules
- [ ] Map shows all orders with driver-specific colors (no red unallocated markers)
- [ ] Regional distribution is balanced

## What This Tests

✅ **AI Allocation Logic**: Confirms the 5-stage pipeline works correctly
✅ **Capability Matching**: Validates wedding/VIP/corporate filtering
✅ **Time Conflict Detection**: Ensures no overlapping assignments
✅ **Regional Optimization**: Tests geographic efficiency logic
✅ **Constraint Validation**: Verifies all hard constraints are enforced
✅ **Map Visualization**: Confirms all features render correctly
