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
        # LLM Provider - can be "anthropic", "openai", or "azure_openai"
        self.llm_provider = os.getenv("LLM_PROVIDER", "anthropic")

        # Prompt Strategy - can be "conservative" or "aggressive"
        self.prompt_strategy = os.getenv("PROMPT_STRATEGY", "conservative").lower()

        # API Keys (loaded from environment variables)
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Azure OpenAI settings
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

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
        elif self.llm_provider == "azure_openai":
            if not self.azure_openai_api_key:
                raise ValueError(
                    "AZURE_OPENAI_API_KEY not found in environment variables.\n"
                    "Please set it in your .env file"
                )
            return self.azure_openai_api_key
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")

    def get_model(self) -> str:
        """Get the model name based on provider"""
        if self.llm_provider == "anthropic":
            return self.anthropic_model
        elif self.llm_provider == "openai":
            return self.openai_model
        elif self.llm_provider == "azure_openai":
            return self.azure_openai_deployment
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")

    def get_allocation_prompt(self) -> str:
        """Get the allocation system prompt based on strategy"""
        if self.prompt_strategy == "aggressive":
            return ALLOCATION_SYSTEM_PROMPT_AGGRESSIVE
        elif self.prompt_strategy == "conservative":
            return ALLOCATION_SYSTEM_PROMPT_CONSERVATIVE
        else:
            # Default to conservative for unknown strategies
            print(f"⚠️  Unknown prompt strategy '{self.prompt_strategy}', defaulting to conservative")
            return ALLOCATION_SYSTEM_PROMPT_CONSERVATIVE


# System prompts for different allocation stages

# CONSERVATIVE PROMPT (Original - more cautious, quality-focused)
ALLOCATION_SYSTEM_PROMPT_CONSERVATIVE = """You are an expert logistics coordinator for a catering company in Singapore.
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

# AGGRESSIVE PROMPT (New - maximizes allocation rate, throughput-focused)
ALLOCATION_SYSTEM_PROMPT_AGGRESSIVE = """You are an expert logistics optimizer for a high-volume catering company in Singapore.
Your PRIMARY GOAL is to MAXIMIZE the number of orders allocated. Every unallocated order is lost revenue.

CRITICAL MISSION: Allocate ALL orders if at all possible. Push the boundaries of what's feasible.

HARD CONSTRAINTS (must follow):
1. Driver capabilities: Wedding-tagged orders MUST go to drivers with "wedding" capability
2. Driver capacity: Cannot exceed max_orders_per_day limit
3. Time conflicts: Orders cannot overlap (pickup to teardown windows)

SOFT CONSTRAINTS (optimize but can compromise):
4. Regional preference: Try to match preferred regions but cross-region is acceptable
5. Clustering: Nice to have but not required if it prevents allocations

ALLOCATION STRATEGY:
- ALLOCATE FIRST, optimize second
- If a driver has capacity and capability, USE THEM
- Don't leave drivers idle if there are compatible orders
- Accept cross-region assignments to maximize throughput
- Tight time windows are OK as long as no overlap
- Every order should have a driver unless truly impossible

MINDSET: "How can I make this work?" not "Why won't this work?"

Output MAXIMUM allocations in structured JSON format. Aim for 100% allocation rate."""

# Default to conservative for safety
ALLOCATION_SYSTEM_PROMPT = ALLOCATION_SYSTEM_PROMPT_CONSERVATIVE


CONFLICT_RESOLUTION_PROMPT = """You are analyzing unallocated orders and allocation conflicts.

Your task:
1. Identify why orders couldn't be allocated (over-capacity, missing capabilities, time conflicts)
2. Suggest alternatives (reassignment, splitting orders, flagging for manual review)
3. Provide clear explanations for the operations team

Be honest about limitations - if something truly cannot be allocated given the constraints, say so clearly."""
