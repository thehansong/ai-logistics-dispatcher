# Original Scenario

## Overview
This is the **default order dataset** for the AI Logistics Dispatcher project. It represents a realistic delivery scenario with various constraints, edge cases, and allocation challenges.

## Usage

### Run with default settings
```bash
python run_allocation.py
```

This scenario is automatically used when no arguments are provided.

### Run with explicit path
```bash
python run_allocation.py --orders data/test_scenarios/original_scenario/orders.json
```

## Dataset Characteristics

This scenario includes:
- **Real-world complexity**: Mix of order types with varying priorities
- **Wedding orders**: Requiring specialized wedding-capable drivers
- **VIP orders**: High-priority deliveries with strict requirements
- **Corporate events**: Business deliveries with specific time windows
- **Regional distribution**: Orders spread across different regions
- **Time constraints**: Various setup times and event windows
- **Capacity challenges**: Tests driver allocation under realistic load

## Testing Purpose

This scenario is designed to:
- ✅ Test the algorithm under realistic conditions
- ✅ Identify allocation challenges and edge cases
- ✅ Evaluate capability matching (wedding, VIP, corporate)
- ✅ Assess regional distribution efficiency
- ✅ Measure time conflict handling
- ✅ Benchmark allocation rate with real-world constraints

## Expected Results

Unlike the `other_scenarios` test which aims for 100% allocation, this scenario:
- May have **unallocated orders** due to realistic constraints
- Tests how well the algorithm **prioritizes** orders
- Evaluates **trade-offs** between different allocation strategies
- Demonstrates **real-world performance** metrics

## Comparing with Other Scenarios

- **original_scenario** (this): Realistic, challenging scenario with potential unallocated orders
- **other_scenarios**: Idealized scenario designed for 100% allocation success

Use both to understand algorithm behavior in different conditions.
