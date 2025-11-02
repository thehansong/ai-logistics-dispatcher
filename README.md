# Smart Delivery Allocator 🚚

AI-powered catering order allocation system that intelligently assigns delivery orders to drivers based on constraints, priorities, and logistics.

# Test with default data
python run_allocation.py

# Test with my own other scenario data
python run_allocation.py --orders data/test_scenarios/other_scenarios/orders.json --drivers data/test_scenarios/other_scenarios/drivers.json

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

Create a `.env` file in the project root (a template is provided in `.env.example`):

```bash
cp .env.example .env
```

Then edit `.env` and add your API key:

**Option A: Anthropic Claude (Recommended - Free Tier Available)**
```bash
# In .env file:
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```
Get a free API key at: https://console.anthropic.com/

**Option B: OpenAI GPT**
```bash
# In .env file:
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```
Get an API key at: https://platform.openai.com/api-keys

**Option C: Azure OpenAI**
```bash
# In .env file:
LLM_PROVIDER=azure_openai
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 3. Run the System

**Recommended: Run Full Pipeline (Single Command)**
```bash
source venv/bin/activate
python run_allocation.py
```

This single command will:
1. Run data analysis with statistics
2. Execute AI allocation through 5 stages
3. Generate interactive map visualization
4. Create comprehensive summary
5. Save all outputs to timestamped folder: `output/run_YYYY-MM-DD_HH-MM-SS/`
   - `00_SUMMARY.txt` - Quick overview with key metrics
   - `01_data_analysis.txt` - Data statistics and constraints
   - `02_allocation_results.json` - Complete allocation results
   - `03_allocation_map.html` - Interactive map visualization
6. Copy to `output/latest/` for easy access

**Alternative: Run Components Individually**

*Data Analysis Only:*
```bash
python scripts/analyze_data.py
```
Output: `output/data_analysis_YYYY-MM-DD_HH-MM-SS.txt`

*Allocation Only:*
```bash
python main.py
```
Output: `output/allocation_output_YYYY-MM-DD_HH-MM-SS.json`

## What It Does

The system intelligently allocates 60 catering orders to 70 delivery specialists while handling:

- **Capability matching**: Only drivers with "wedding" capabilities can handle wedding orders
- **Capacity constraints**: Each driver has a max orders/day limit (4-8 orders)
- **Time conflicts**: Ensures drivers don't have overlapping order windows
- **Geographic efficiency**: Prefers assigning orders in drivers' preferred regions
- **Priority handling**: VIP and wedding orders get highest priority

## Project Structure

```
ai-logistics-dispatcher/
├── run_allocation.py                # 🎯 MAIN RUNNER (use this!)
├── main.py                          # Allocation only (standalone)
├── src/                             # Source code
│   ├── allocator.py                 # Main orchestration engine
│   ├── ai_allocator.py              # AI-powered allocation logic
│   ├── llm_client.py                # LLM wrapper (OpenAI/Anthropic/Azure)
│   ├── config.py                    # LLM settings and prompts
│   ├── utils.py                     # Helper functions (distance, time, validation)
│   ├── preprocessor.py              # Data preprocessing and categorization
│   ├── validator.py                 # Allocation validation
│   └── output_formatter.py          # Output formatting
├── data/                            # Data files
│   ├── orders.json                  # 60 catering orders
│   └── drivers.json                 # 70 drivers
├── scripts/                         # Utility scripts
│   └── analyze_data.py              # Data analysis (standalone)
├── output/                          # Generated outputs
│   ├── run_YYYY-MM-DD_HH-MM-SS/     # Timestamped run folders
│   │   ├── 00_SUMMARY.txt           # Quick overview
│   │   ├── 01_data_analysis.txt     # Data insights
│   │   ├── 02_allocation_results.json # Full results
│   │   └── 03_allocation_map.html   # Interactive map
│   └── latest/                      # Latest run (always available)
│       ├── 00_SUMMARY.txt
│       ├── 01_data_analysis.txt
│       ├── 02_allocation_results.json
│       └── 03_allocation_map.html
├── venv/                            # Virtual environment
├── .env                             # API keys (create from .env.example)
├── .env.example                     # API key template
└── requirements.txt                 # Python dependencies
```

## How It Works

### Multi-Stage AI Allocation Pipeline

The system processes orders through 5 intelligent stages:

**Stage 1: VIP + Wedding Orders**
- Allocates highest priority orders (VIP weddings) first
- Matches to wedding-capable drivers only
- Critical constraint: 19 VIP wedding orders → 14 capable drivers

**Stage 2: Remaining VIP Orders**
- Allocates VIP-only orders to available wedding-capable drivers
- Ensures VIP service quality

**Stage 3: Remaining Wedding Orders**
- Allocates wedding-only orders (no VIP tag)
- 17 additional wedding orders compete for remaining capacity

**Stage 4: Corporate Orders**
- Allocates corporate/seminar events
- Matches to corporate-experienced or general drivers
- Handles early_setup requirements

**Stage 5: Regular Orders**
- Allocates standard catering orders
- Uses all available drivers
- Maximizes regional efficiency

### AI vs Deterministic Logic

**AI Handles:**
- Prioritization decisions within each stage
- Regional clustering and geographic efficiency
- Trade-off reasoning (e.g., region match vs time efficiency)
- Explaining allocation decisions

**Code Validates:**
- Time conflict detection (pickup/setup/teardown overlaps)
- Driver capacity constraints (max_orders_per_day)
- Required capabilities (wedding/VIP/corporate)
- Distance calculations (haversine formula)
- Buffer time between orders (15 min minimum)

**Why this split?** LLMs excel at nuanced trade-offs but can hallucinate. We validate every AI decision with hard constraints.

### Key Assumptions

- **Travel time**: 30 minutes between any two orders (Singapore is compact)
- **Minimum buffer**: 15 minutes between order teardown and next pickup
- **TBD addresses** (postal code "000000"): Lower priority, flagged as incomplete
- **Capability requirements**: Wedding/VIP tags require matching driver capabilities

## Output Format

The system generates 4 files per run in a timestamped folder:
1. **00_SUMMARY.txt**: Quick overview with key metrics and top drivers
2. **01_data_analysis.txt**: Detailed data statistics and constraint analysis
3. **02_allocation_results.json**: Complete allocation results with driver assignments and reasoning
4. **03_allocation_map.html**: Interactive map visualization with color-coded markers

## Example Output

```
🚚 DRIVER: DRV-008 - Lakshmi Naidu
   Region: east | Capacity: 3/5 orders | Utilization: 60%
   Capabilities: vip, wedding, large_events

   Assigned Orders (3):
   1. Q3958 - Sacred Heart Hall, Church of Saint Ignatius
      Setup: 19:45 | Region: north | Pax: 200 [wedding, vip]
      → VIP wedding capability required, no time conflict

   2. P4436 - Grace Baptist Church
      Setup: 20:15 | Region: east | Pax: 150 [wedding, vip]
      → Same region preference, sequential timing works
```

## Known Limitations

1. **Route optimization**: Not implemented (NP-hard problem). Focus is on smart initial allocation.
2. **Real-time traffic**: Uses fixed 30-min travel time assumption
3. **Multi-stop sequencing**: Orders assigned to driver, but optimal route not calculated

## What I'd Build Next (Production)

1. **Real route optimization**: Integrate Google Maps Distance Matrix API
2. **Dynamic constraints**: Allow ops team to adjust priorities/constraints
3. **Interactive UI**: Web dashboard for viewing and tweaking allocations
4. **Database integration**: Store allocation history for learning
5. **A/B testing**: Compare AI allocations vs manual allocations over time

## Cost & Performance

- **API calls**: ~3-5 calls per run
- **Cost**: <$0.50 per allocation run
- **Runtime**: ~30-60 seconds for 60 orders

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
- Make sure you've exported the API key: `export ANTHROPIC_API_KEY='your-key'`
- Verify with: `echo $ANTHROPIC_API_KEY`

**Import errors**
- Install dependencies: `pip install -r requirements.txt`

**"No module named 'anthropic'"**
- Run: `pip install anthropic`

## Development Status

### ✅ Completed Phases

**Phase 1: Core Infrastructure**
- Project structure with organized folders (`src/`, `data/`, `scripts/`, `output/`)
- Configuration management with `.env` support
- LLM client wrapper supporting OpenAI, Anthropic, and Azure OpenAI
- Utility functions (haversine distance, time conflict detection, validation)
- Output formatting with timestamped files

**Phase 2: Data Preprocessing**
- Data analysis script with statistical insights
- Order categorization by priority (VIP+wedding, VIP, wedding, corporate, regular)
- Driver categorization by capabilities (wedding-capable, corporate-capable, general)
- Constraint identification (capacity bottlenecks, regional imbalances)
- Comprehensive statistics generation

**Phase 3: AI Allocation Engine**
- Multi-stage allocation pipeline (5 stages)
- AI-powered order assignment with reasoning
- Smart prompting for constraint satisfaction
- Allocation validation (time conflicts, capacity, capabilities)
- Metrics calculation (utilization, regional distribution)
- Unallocated order reasoning

**Phase 4: Visualization**
- Interactive HTML map using Folium
- Color-coded markers per driver (20 distinct colors)
- VIP orders marked with star icons, regular with cutlery icons
- Unallocated orders in red with warning icons
- Interactive popups showing order and driver details
- Layer control to toggle individual drivers
- Legend and statistics overlay
- Map output: `03_allocation_map.html`

### ✅ Current Status

**System is fully functional!** Just needs a valid API key to run.

- All 4 phases complete
- End-to-end testing completed
- Timestamped output files working
- Data analysis, allocation, and visualization integrated
- Single command execution via `run_allocation.py`

---

## Project Highlights

✨ **Key Features Implemented:**
- 5-stage intelligent allocation pipeline
- Multi-provider LLM support (OpenAI/Anthropic/Azure)
- Comprehensive validation with hard constraints
- Timestamped output for history tracking
- Interactive map visualization with Folium
- Clear separation of AI reasoning vs deterministic logic

📊 **Data Insights:**
- 60 orders across 5 regions
- 70 drivers with varying capabilities
- 36 wedding orders competing for 14 wedding-capable drivers (2.6:1 ratio)
- 14.5% driver utilization needed
- 42/60 orders in evening time slot (potential conflicts)

---

Built for Grain AI Solutions Engineer Technical Interview