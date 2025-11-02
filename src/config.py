"""
Configuration settings for the Smart Delivery Allocator
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for LLM and application settings"""

    def __init__(self):
        # LLM Provider - can be "anthropic" or "openai"
        self.llm_provider = os.getenv("LLM_PROVIDER", "anthropic")

        # API Keys (loaded from environment variables)
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Model selection
        self.anthropic_model = "claude-3-5-sonnet-20241022"
        self.openai_model = "gpt-4o"

        # LLM parameters
        self.temperature = 0.1  # Low temperature for more deterministic outputs
        self.max_tokens = 4000

        # Allocation parameters
        self.assumed_travel_time_minutes = 30  # Assumed travel time between orders
        self.min_buffer_time_minutes = 15  # Minimum buffer between orders

        # Feature flags
        self.enable_visualization = True
        self.verbose_logging = True

    def get_api_key(self) -> str:
        """Get the appropriate API key based on provider"""
        if self.llm_provider == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not found in environment variables.\n"
                    "Please set it with: export ANTHROPIC_API_KEY='your-key-here'\n"
                    "Get a free API key at: https://console.anthropic.com/"
                )
            return self.anthropic_api_key
        elif self.llm_provider == "openai":
            if not self.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY not found in environment variables.\n"
                    "Please set it with: export OPENAI_API_KEY='your-key-here'\n"
                    "Get an API key at: https://platform.openai.com/api-keys"
                )
            return self.openai_api_key
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")

    def get_model(self) -> str:
        """Get the model name based on provider"""
        if self.llm_provider == "anthropic":
            return self.anthropic_model
        elif self.llm_provider == "openai":
            return self.openai_model
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")


# System prompts for different allocation stages
ALLOCATION_SYSTEM_PROMPT = """You are an expert logistics coordinator for a catering company in Singapore.
Your task is to intelligently assign catering orders to delivery specialists based on multiple constraints.

Key constraints to consider:
1. Driver capabilities: Only drivers with "wedding" capability can handle wedding-tagged orders
2. Driver capacity: Each driver has a max_orders_per_day limit (typically 4-8 orders)
3. Time windows: Orders have pickup, setup, and teardown times. Drivers cannot have overlapping orders.
4. Geographic efficiency: Prefer assigning orders to drivers in their preferred region
5. Priority: VIP and wedding orders are highest priority

Your decisions should:
- Prioritize VIP+wedding orders first (assign to capable drivers)
- Cluster orders by region and time to maximize efficiency
- Explain your reasoning for each assignment
- Flag any conflicts, capacity issues, or questionable assignments
- Be practical and realistic for an operations team

Output your allocations in structured JSON format."""


CONFLICT_RESOLUTION_PROMPT = """You are analyzing unallocated orders and allocation conflicts.

Your task:
1. Identify why orders couldn't be allocated (over-capacity, missing capabilities, time conflicts)
2. Suggest alternatives (reassignment, splitting orders, flagging for manual review)
3. Provide clear explanations for the operations team

Be honest about limitations - if something truly cannot be allocated given the constraints, say so clearly."""
