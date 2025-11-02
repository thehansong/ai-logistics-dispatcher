"""
AI-powered allocation engine using LLMs
"""

import json
from typing import Dict, List, Any, Tuple
from llm_client import LLMClient
from config import Config
from validator import AllocationValidator, validate_order_feasibility


class AIAllocator:
    """AI-powered order allocation using LLMs"""

    def __init__(self, config: Config):
        self.config = config
        self.llm = LLMClient(config)
        self.validator = AllocationValidator(config)

    def allocate_orders(
        self,
        orders: List[Dict],
        drivers: List[Dict],
        categorized_orders: Dict[str, List[Dict]],
        categorized_drivers: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """
        Main allocation method using multi-stage AI allocation

        Args:
            orders: All orders
            drivers: All drivers
            categorized_orders: Orders categorized by priority
            categorized_drivers: Drivers categorized by capability

        Returns:
            Allocation results dictionary
        """
        print("\n🤖 Starting AI allocation engine...\n")

        allocations = []
        allocated_order_ids = set()
        driver_assignments = {d["driver_id"]: [] for d in drivers}

        # Stage 1: Allocate VIP + Wedding orders (highest priority)
        print("Stage 1: Allocating VIP + Wedding orders...")
        vip_wedding_orders = categorized_orders.get("vip_wedding", [])
        if vip_wedding_orders:
            stage1_result = self._allocate_priority_orders(
                vip_wedding_orders,
                categorized_drivers["wedding_capable"],
                driver_assignments,
                stage_name="VIP Wedding Orders"
            )
            allocations.extend(stage1_result["allocations"])
            allocated_order_ids.update(stage1_result["allocated_order_ids"])
            print(f"  ✓ Allocated {len(stage1_result['allocated_order_ids'])}/{len(vip_wedding_orders)} VIP wedding orders\n")

        # Stage 2: Allocate VIP + Corporate orders
        print("Stage 2: Allocating VIP + Corporate orders...")
        vip_corporate_orders = categorized_orders.get("vip_corporate", [])
        if vip_corporate_orders:
            stage2_result = self._allocate_priority_orders(
                vip_corporate_orders,
                categorized_drivers["corporate_capable"],
                driver_assignments,
                stage_name="VIP Corporate Orders"
            )
            allocations.extend(stage2_result["allocations"])
            allocated_order_ids.update(stage2_result["allocated_order_ids"])
            print(f"  ✓ Allocated {len(stage2_result['allocated_order_ids'])}/{len(vip_corporate_orders)} VIP corporate orders\n")

        # Stage 3: Allocate remaining VIP orders
        print("Stage 3: Allocating remaining VIP orders...")
        vip_orders = categorized_orders.get("vip", [])
        if vip_orders:
            stage3_result = self._allocate_priority_orders(
                vip_orders,
                categorized_drivers["wedding_capable"],
                driver_assignments,
                stage_name="VIP Orders"
            )
            allocations.extend(stage3_result["allocations"])
            allocated_order_ids.update(stage3_result["allocated_order_ids"])
            print(f"  ✓ Allocated {len(stage3_result['allocated_order_ids'])}/{len(vip_orders)} VIP orders\n")

        # Stage 4: Allocate remaining wedding orders
        print("Stage 4: Allocating remaining wedding orders...")
        wedding_orders = categorized_orders.get("wedding", [])
        if wedding_orders:
            stage4_result = self._allocate_priority_orders(
                wedding_orders,
                categorized_drivers["wedding_capable"],
                driver_assignments,
                stage_name="Wedding Orders"
            )
            allocations.extend(stage4_result["allocations"])
            allocated_order_ids.update(stage4_result["allocated_order_ids"])
            print(f"  ✓ Allocated {len(stage4_result['allocated_order_ids'])}/{len(wedding_orders)} wedding orders\n")

        # Stage 5: Allocate corporate orders
        print("Stage 5: Allocating corporate orders...")
        corporate_orders = categorized_orders.get("corporate", [])
        if corporate_orders:
            stage5_result = self._allocate_batch_orders(
                corporate_orders,
                categorized_drivers["corporate_capable"] + categorized_drivers["general"],
                driver_assignments,
                stage_name="Corporate Orders"
            )
            allocations.extend(stage5_result["allocations"])
            allocated_order_ids.update(stage5_result["allocated_order_ids"])
            print(f"  ✓ Allocated {len(stage5_result['allocated_order_ids'])}/{len(corporate_orders)} corporate orders\n")

        # Stage 6: Allocate regular orders
        print("Stage 6: Allocating regular orders...")
        regular_orders = categorized_orders.get("regular", [])
        if regular_orders:
            stage6_result = self._allocate_batch_orders(
                regular_orders,
                drivers,  # All drivers available
                driver_assignments,
                stage_name="Regular Orders"
            )
            allocations.extend(stage6_result["allocations"])
            allocated_order_ids.update(stage6_result["allocated_order_ids"])
            print(f"  ✓ Allocated {len(stage6_result['allocated_order_ids'])}/{len(regular_orders)} regular orders\n")

        # Merge allocations by driver
        final_allocations = self._merge_allocations(allocations, drivers)

        # Find unallocated orders
        unallocated_orders = [
            o for o in orders if o["order_id"] not in allocated_order_ids
        ]

        # Add reasoning for unallocated orders
        for order in unallocated_orders:
            order["unallocation_reason"] = self._get_unallocation_reason(
                order, drivers, driver_assignments
            )

        return {
            "allocations": final_allocations,
            "allocated_order_ids": allocated_order_ids,
            "unallocated_orders": unallocated_orders
        }

    def _allocate_priority_orders(
        self,
        orders: List[Dict],
        available_drivers: List[Dict],
        driver_assignments: Dict[str, List[Dict]],
        stage_name: str
    ) -> Dict[str, Any]:
        """Allocate high-priority orders using AI"""

        if not orders:
            return {"allocations": [], "allocated_order_ids": set()}

        # Filter drivers who still have capacity
        drivers_with_capacity = [
            d for d in available_drivers
            if len(driver_assignments[d["driver_id"]]) < d.get("max_orders_per_day", 0)
        ]

        if not drivers_with_capacity:
            print(f"  ⚠️  No drivers with capacity available for {stage_name}")
            return {"allocations": [], "allocated_order_ids": set()}

        # Build prompt for AI
        prompt = self._build_allocation_prompt(
            orders, drivers_with_capacity, driver_assignments, stage_name
        )

        # Get AI allocation
        try:
            # Use the configured prompt strategy (conservative or aggressive)
            system_prompt = self.config.get_allocation_prompt()

            response = self.llm.generate(
                system_prompt=system_prompt,
                user_prompt=prompt,
                response_format="json"
            )

            allocation_result = self.llm.parse_json_response(response)

            # Parse and validate allocations
            allocations, allocated_ids = self._parse_ai_allocations(
                allocation_result, orders, drivers_with_capacity, driver_assignments
            )

            return {
                "allocations": allocations,
                "allocated_order_ids": allocated_ids
            }

        except Exception as e:
            print(f"  ❌ Error in AI allocation: {e}")
            return {"allocations": [], "allocated_order_ids": set()}

    def _allocate_batch_orders(
        self,
        orders: List[Dict],
        available_drivers: List[Dict],
        driver_assignments: Dict[str, List[Dict]],
        stage_name: str
    ) -> Dict[str, Any]:
        """Allocate regular/corporate orders in batch"""
        return self._allocate_priority_orders(
            orders, available_drivers, driver_assignments, stage_name
        )

    def _build_allocation_prompt(
        self,
        orders: List[Dict],
        drivers: List[Dict],
        driver_assignments: Dict[str, List[Dict]],
        stage_name: str
    ) -> str:
        """Build the allocation prompt for the LLM"""

        # Prepare order data
        order_summary = []
        for order in orders[:20]:  # Limit to avoid token overflow
            order_summary.append({
                "order_id": order["order_id"],
                "region": order.get("region"),
                "setup_time": order.get("setup_time"),
                "teardown_time": order.get("teardown_time"),
                "tags": order.get("tags", []),
                "address": order.get("address", "")[:50]
            })

        # Prepare driver data with current load
        driver_summary = []
        for driver in drivers[:30]:  # Limit drivers
            current_orders = len(driver_assignments[driver["driver_id"]])
            max_orders = driver.get("max_orders_per_day", 0)
            driver_summary.append({
                "driver_id": driver["driver_id"],
                "name": driver.get("name"),
                "preferred_region": driver.get("preferred_region"),
                "capabilities": driver.get("capabilities", []),
                "capacity": f"{current_orders}/{max_orders}"
            })

        prompt = f"""
You are allocating {stage_name} for a catering company.

## Orders to Allocate ({len(orders)} total, showing first {len(order_summary)}):
{json.dumps(order_summary, indent=2)}

## Available Drivers ({len(drivers)} total, showing first {len(driver_summary)}):
{json.dumps(driver_summary, indent=2)}

## Allocation Rules:
1. MUST match driver capabilities to order tags (wedding/vip orders need wedding-capable drivers)
2. MUST respect driver capacity limits
3. MUST avoid time conflicts (check setup_time and teardown_time)
4. PREFER drivers in their preferred region
5. PREFER clustering orders by region and time

## Required Output Format (JSON):
{{
  "allocations": [
    {{
      "driver_id": "DRV-XXX",
      "order_ids": ["Q1234", "Q5678"],
      "reasoning": "Brief explanation of why this driver got these orders"
    }}
  ]
}}

Allocate as many orders as possible while respecting all constraints.
"""

        return prompt

    def _parse_ai_allocations(
        self,
        ai_result: Dict,
        orders: List[Dict],
        drivers: List[Dict],
        driver_assignments: Dict[str, List[Dict]]
    ) -> Tuple[List[Dict], set]:
        """Parse and validate AI allocation results"""

        allocations = []
        allocated_order_ids = set()

        # Create lookup maps
        order_map = {o["order_id"]: o for o in orders}
        driver_map = {d["driver_id"]: d for d in drivers}

        ai_allocations = ai_result.get("allocations", [])

        for allocation in ai_allocations:
            driver_id = allocation.get("driver_id")
            order_ids = allocation.get("order_ids", [])
            reasoning = allocation.get("reasoning", "")

            if not driver_id or driver_id not in driver_map:
                continue

            driver = driver_map[driver_id]
            assigned_orders = []

            # Validate each order assignment
            for order_id in order_ids:
                if order_id not in order_map:
                    continue

                order = order_map[order_id]
                current_assignments = driver_assignments[driver_id]

                # Check feasibility
                is_feasible, reason = validate_order_feasibility(
                    order, driver, current_assignments, self.config
                )

                if is_feasible:
                    assigned_orders.append(order)
                    driver_assignments[driver_id].append(order)
                    allocated_order_ids.add(order_id)
                else:
                    if self.config.verbose_logging:
                        print(f"    ⚠️  Skipped {order_id} for {driver_id}: {reason}")

            if assigned_orders:
                allocations.append({
                    "driver": driver,
                    "orders": assigned_orders,
                    "reasoning": reasoning
                })

        return allocations, allocated_order_ids

    def _merge_allocations(
        self,
        allocations: List[Dict],
        all_drivers: List[Dict]
    ) -> List[Dict]:
        """Merge allocations by driver"""

        driver_map = {}

        for allocation in allocations:
            driver_id = allocation["driver"]["driver_id"]

            if driver_id not in driver_map:
                driver_map[driver_id] = {
                    "driver": allocation["driver"],
                    "orders": [],
                    "reasoning": allocation.get("reasoning", "")
                }

            driver_map[driver_id]["orders"].extend(allocation["orders"])

        # Calculate utilization
        final_allocations = []
        for driver_id, data in driver_map.items():
            max_orders = data["driver"].get("max_orders_per_day", 1)
            utilization = (len(data["orders"]) / max_orders) * 100

            final_allocations.append({
                "driver": data["driver"],
                "orders": data["orders"],
                "reasoning": data["reasoning"],
                "utilization": utilization
            })

        # Sort by utilization (descending)
        final_allocations.sort(key=lambda x: x["utilization"], reverse=True)

        return final_allocations

    def _get_unallocation_reason(
        self,
        order: Dict,
        drivers: List[Dict],
        driver_assignments: Dict[str, List[Dict]]
    ) -> str:
        """Determine why an order couldn't be allocated"""

        order_tags = order.get("tags", [])

        # Check if wedding order but no capable drivers
        if "wedding" in order_tags or "vip" in order_tags:
            capable_drivers = [
                d for d in drivers
                if "wedding" in d.get("capabilities", []) or "vip" in d.get("capabilities", [])
            ]
            if not capable_drivers:
                return "No drivers with wedding/VIP capabilities available"

            # Check if all capable drivers at capacity
            available = [
                d for d in capable_drivers
                if len(driver_assignments[d["driver_id"]]) < d.get("max_orders_per_day", 0)
            ]
            if not available:
                return "All wedding-capable drivers at full capacity"

        # General capacity issue
        drivers_with_space = [
            d for d in drivers
            if len(driver_assignments[d["driver_id"]]) < d.get("max_orders_per_day", 0)
        ]

        if not drivers_with_space:
            return "All drivers at full capacity"

        return "Time conflicts or regional constraints prevented allocation"