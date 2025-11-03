# Data Directory

This directory contains the core data files used by the AI Logistics Dispatcher.

## Structure

```
data/
├── README.md                    # This file
├── drivers/                     # Driver fleet data
│   └── drivers.json             # Single source of truth for driver information
└── test_scenarios/              # Test order datasets
    ├── original_scenario/       # Default/original scenario
    │   ├── orders.json          # Original order dataset (default)
    │   └── README.md            # Original scenario documentation
    └── other_scenarios/         # Alternative test scenario
        ├── orders.json          # Test orders (100% allocation scenario)
        └── README.md            # Test scenario documentation
```

## Files

### `drivers/drivers.json`
**Purpose**: Defines the available driver fleet with their capabilities, regions, and capacities.

**Location**: `data/drivers/drivers.json`

**Contents**:
- Driver profiles with unique IDs
- Capabilities (wedding, VIP, corporate, etc.)
- Regional assignments
- Maximum orders per day
- Working hours and availability

**Usage**: This file represents your consistent fleet of drivers and should remain relatively stable across test runs. Update this file when:
- Adding or removing drivers from your fleet
- Changing driver capabilities or certifications
- Modifying regional assignments
- Adjusting capacity limits

**Note**: This is the single source of truth for driver data. All test scenarios use this same driver file to ensure consistency.

---

## Test Scenarios

### `test_scenarios/original_scenario/`
**Purpose**: The original/default order dataset for the project.

**Location**: `data/test_scenarios/original_scenario/orders.json`

**Usage**: This is the default scenario used when running `python run_allocation.py` without arguments. It represents a realistic delivery scenario with various constraints and challenges.

---

### `test_scenarios/other_scenarios/`
**Purpose**: Alternative test dataset designed for 100% allocation success.

**Location**: `data/test_scenarios/other_scenarios/orders.json`

**Usage**: Test scenario with optimal conditions designed to achieve 100% allocation. See `test_scenarios/other_scenarios/README.md` for details.

---

## Testing Strategy

**Keep drivers constant, vary orders**: Maintain `drivers/drivers.json` as a stable baseline while testing different order scenarios to evaluate how the algorithm handles various patterns, volumes, and constraints with the same driver fleet.
