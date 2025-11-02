# Smart Delivery Allocator 🚚

AI-powered catering order allocation system that intelligently assigns delivery orders to drivers based on constraints, priorities, and logistics.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file in the project root (a template is provided in `.env.example`):

```bash
cp .env.example .env
```

Then edit `.env` and add your API key:

**Option A: Anthropic Claude (Recommended)**
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

### 3. Run the Allocator

```bash
python allocator.py
```

This will:
- Load orders from `orders.json` and drivers from `drivers.json`
- Run the AI allocation engine
- Display results in the terminal
- Save results to `allocation_output.json`

## What It Does

The system intelligently allocates 60 catering orders to 70 delivery specialists while handling:

- **Capability matching**: Only drivers with "wedding" capabilities can handle wedding orders
- **Capacity constraints**: Each driver has a max orders/day limit (4-8 orders)
- **Time conflicts**: Ensures drivers don't have overlapping order windows
- **Geographic efficiency**: Prefers assigning orders in drivers' preferred regions
- **Priority handling**: VIP and wedding orders get highest priority

## Project Structure

```
├── allocator.py          # Main allocation engine
├── config.py            # LLM settings and prompts
├── utils.py             # Helper functions (distance calc, validation)
├── output_formatter.py  # Output formatting and visualization
├── orders.json          # 60 catering orders (provided)
├── drivers.json         # 70 drivers (provided)
└── requirements.txt     # Python dependencies
```

## Key Design Decisions

### Multi-Stage Allocation
We use a multi-stage approach instead of single-pass:
1. **Priority Tier Assignment**: VIP+wedding orders first
2. **Capability Matching**: Match wedding orders to capable drivers
3. **Geographic Clustering**: Group nearby orders
4. **Conflict Resolution**: Handle unallocated orders

**Why?** With 26 wedding orders competing for only 14 wedding-capable drivers, a single-pass would create impossible allocations.

### AI vs Deterministic Logic
- **AI handles**: Prioritization decisions, regional clustering, trade-offs
- **Code handles**: Time conflict detection, distance calculations, hard constraint validation

**Why?** LLMs are great at reasoning about trade-offs, but we validate their outputs to prevent hallucinations.

### Assumptions Made
- **Travel time**: 30 minutes between any two orders
- **Minimum buffer**: 15 minutes between order teardown and next pickup
- **TBD addresses** (postal code "000000"): Treated as lower priority, flagged as incomplete data

## Output Format

The system generates:
1. **Terminal output**: Human-readable allocation summary
2. **JSON file**: Structured allocation data (`allocation_output.json`)
3. **Text file**: Detailed report (`allocation_output.txt`)
4. **Map visualization** (optional): HTML map showing allocations

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

- ✅ Phase 1: Core infrastructure (COMPLETE)
- 🚧 Phase 2: Data preprocessing (IN PROGRESS)
- ⏳ Phase 3: AI allocation engine (PENDING)
- ⏳ Phase 4: Visualization (PENDING)

---

Built for Grain AI Solutions Engineer Technical Interview