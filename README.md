# Smart Delivery Allocator 🚚

AI-powered catering order allocation system that intelligently assigns delivery orders to drivers based on constraints, priorities, and logistics.

## Quick Start

### 1. Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your API key:

**Option A: Anthropic Claude (Recommended - Free Tier Available)**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Option B: OpenAI GPT**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

### 3. Run the System

**Basic Usage (Default Data)**
```bash
source venv/bin/activate
python run_allocation.py
```

**Test with Custom Data**
```bash
python run_allocation.py --orders data/test_scenarios/other_scenarios/orders.json --drivers data/test_scenarios/other_scenarios/drivers.json
```

**Choose Prompt Strategy**
```bash
# Conservative: Quality-focused, cautious allocations (default)
python run_allocation.py --prompt conservative

# Aggressive: Throughput-focused, maximizes allocation rate
python run_allocation.py --prompt aggressive
```

### 4. View Results

The system generates 4 files in `output/run_YYYY-MM-DD_HH-MM-SS/`:
- `00_SUMMARY.txt` - Quick overview with key metrics
- `01_data_analysis.txt` - Data statistics and constraints
- `02_allocation_results.json` - Complete allocation results
- `03_allocation_map.html` - Interactive map visualization

Results are also available at `output/latest/` for easy access.

## What It Does

The system intelligently allocates catering orders to delivery drivers while handling:

- **Capability matching**: Only drivers with "wedding" capabilities can handle wedding orders
- **Capacity constraints**: Each driver has a max orders/day limit
- **Time conflicts**: Ensures drivers don't have overlapping order windows
- **Geographic efficiency**: Prefers assigning orders in drivers' preferred regions
- **Priority handling**: VIP and wedding orders get highest priority

## Project Structure

```
ai-logistics-dispatcher/
├── run_allocation.py                # Main runner script
├── src/                             # Source code
│   ├── allocator.py                 # Main orchestration engine
│   ├── ai_allocator.py              # AI-powered allocation logic
│   ├── llm_client.py                # LLM wrapper (OpenAI/Anthropic/Azure)
│   ├── config.py                    # LLM settings and prompts
│   ├── utils.py                     # Helper functions
│   ├── preprocessor.py              # Data preprocessing
│   ├── validator.py                 # Allocation validation
│   ├── output_formatter.py          # Output formatting
│   └── map_visualizer.py            # Map visualization
├── data/                            # Data files
│   ├── orders.json                  # Catering orders
│   ├── drivers.json                 # Delivery drivers
│   └── test_scenarios/              # Test datasets
├── output/                          # Generated outputs
│   ├── run_YYYY-MM-DD_HH-MM-SS/     # Timestamped runs
│   └── latest/                      # Latest run
├── .env                             # API keys (create from .env.example)
└── requirements.txt                 # Python dependencies
```

## CLI Options

```bash
# Full help
python run_allocation.py --help

# Specify custom data files
python run_allocation.py --orders PATH --drivers PATH

# Choose prompt strategy (skip interactive selection)
python run_allocation.py --prompt [conservative|aggressive]
```

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
- Make sure you've created `.env` from `.env.example`
- Add your API key to the `.env` file

**Import errors**
- Install dependencies: `pip install -r requirements.txt`
- Activate virtual environment: `source venv/bin/activate`

**"No module named 'anthropic'"**
- Run: `pip install anthropic`