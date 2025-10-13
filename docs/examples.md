# Examples

Usage examples and tutorials for Filling Scheduler.

## Basic Examples

### Example 1: Simple Schedule

**Using CLI (Recommended)**:

```bash
# Basic usage
fillscheduler schedule --data examples/lots.csv

# With specific strategy
fillscheduler schedule --data examples/lots.csv --strategy smart-pack

# With start time
fillscheduler schedule \
    --data examples/lots.csv \
    --strategy smart-pack \
    --start-time "2025-01-01 08:00"

# Custom output directory
fillscheduler schedule \
    --data examples/lots.csv \
    --output results/
```

Output:
```
⠋ Loading lots from examples/lots.csv...
✓ Loaded 15 lots
⠋ Validating lots...
✓ Lots validated successfully
⠋ Planning schedule with smart-pack strategy...
✓ Schedule completed

╭─────────────────────── Schedule KPIs ────────────────────────╮
│ Makespan           │ 156.75 hours                            │
│ Lots Scheduled     │ 15                                      │
│ Utilization        │ 87.3%                                   │
│ Changeovers        │ 3                                       │
│ Window Violations  │ 0                                       │
╰──────────────────────────────────────────────────────────────╯

✓ Summary written to output/summary.txt
✓ HTML report written to output/report.html
```

**Using Python API**:

```python
from fillscheduler.config_loader import load_config_from_file
from fillscheduler.scheduler import plan_schedule
from fillscheduler.io_utils import read_lots_with_pandas
from datetime import datetime

# Load configuration from file (recommended)
cfg = load_config_from_file("config.yaml")

# Or use programmatic configuration
from fillscheduler.config import AppConfig
from pathlib import Path
cfg = AppConfig(
    DATA_PATH=Path("examples/lots.csv"),
    STRATEGY="smart-pack"
)

# Load lots
lots = read_lots_with_pandas(cfg.DATA_PATH, cfg)

# Generate schedule
activities, makespan, kpis = plan_schedule(
    lots=lots,
    start_time=datetime(2025, 1, 1, 8, 0),
    cfg=cfg
)

# Print results
print(f"Makespan: {makespan:.2f} hours")
print(f"Lots scheduled: {kpis['Lots Scheduled']}")
```

### Example 2: Compare Strategies

**Using CLI (Recommended)**:

```bash
# Compare specific strategies
fillscheduler compare \
    --data examples/lots.csv \
    --strategies smart-pack spt-pack lpt-pack

# Compare all strategies
fillscheduler compare --data examples/lots.csv --all-strategies

# Sort by utilization instead of makespan
fillscheduler compare \
    --data examples/lots.csv \
    --all-strategies \
    --sort-by utilization

# Custom output directory
fillscheduler compare \
    --data examples/lots.csv \
    --all-strategies \
    --output results/comparison/
```

Output:
```
⠋ Comparing 6 strategies on 15 lots...
✓ All strategies completed

╭─────────────────────── Strategy Comparison ────────────────────────╮
│ Strategy    │ Makespan (h) │ Utilization │ Changeovers │ Violations │
├─────────────┼──────────────┼─────────────┼─────────────┼────────────┤
│ smart-pack  │ 156.75       │ 87.3%       │ 3           │ 0          │
│ hybrid-pack │ 158.20       │ 86.8%       │ 3           │ 0          │
│ lpt-pack    │ 160.50       │ 85.5%       │ 4           │ 0          │
│ spt-pack    │ 162.00       │ 84.7%       │ 5           │ 0          │
│ cfs-pack    │ 159.10       │ 86.2%       │ 2           │ 0          │
│ milp-opt    │ 156.50       │ 87.5%       │ 3           │ 0          │
╰────────────────────────────────────────────────────────────────────╯

✓ Comparison written to results/comparison/comparison.txt
```

**Using Python API**:

```python
from fillscheduler.compare_sequences import compare_strategies

# Compare multiple strategies
results = compare_strategies(
    lots=lots,
    strategy_names=["smart-pack", "spt-pack", "lpt-pack"],
    cfg=cfg
)

# Print comparison
for result in results:
    print(f"{result['strategy']}: {result['makespan']:.2f}h, {result['utilization']:.1%}")
```

### Example 3: Custom Configuration

**Using CLI with configuration file (recommended)**:

Step 1: Export a default configuration template:

```bash
fillscheduler config export --output config.yaml
```

Step 2: Edit the configuration file:

```yaml
# config.yaml
schedule:
  strategy: "smart-pack"

constraints:
  clean_hours: 18.0
  window_hours: 96.0

smart_pack:
  beam_width: 5
```

Step 3: Use the configuration file:

```bash
fillscheduler --config config.yaml schedule --data examples/lots.csv
```

You can also validate the configuration:

```bash
fillscheduler config validate --file config.yaml
```

**Using CLI with environment variables**:

```bash
export FILLSCHEDULER_STRATEGY="smart-pack"
export FILLSCHEDULER_CLEAN_HOURS="18.0"
export FILLSCHEDULER_WINDOW_HOURS="96.0"
export FILLSCHEDULER_BEAM_WIDTH="5"

fillscheduler schedule --data examples/lots.csv
```

**Using CLI with inline options** (overrides configuration file):

```bash
fillscheduler --config config.yaml schedule \
    --data examples/lots.csv \
    --strategy lpt-pack  # Overrides config file
```

**Using Python API**:

```python
from fillscheduler.config_loader import load_config_from_file

# Load from file
cfg = load_config_from_file("config.yaml")
```

Or programmatically:

```python
from fillscheduler.config import AppConfig

cfg = AppConfig(
    STRATEGY="smart-pack",
    CLEAN_HOURS=18.0,      # Shorter cleaning
    WINDOW_HOURS=96.0,     # Tighter window
    BEAM_WIDTH=5,          # More exploration
)
```

### Example 4: Working with Configuration

**Export configuration in different formats**:

```bash
# YAML format (default, includes comments)
fillscheduler config export --output config.yaml

# JSON format (no comments)
fillscheduler config export --output config.json --format json
```

**Validate configuration files**:

```bash
# Validate a configuration file
fillscheduler config validate --file config.yaml

# Output on success:
✓ Configuration is valid

# Output on error:
✗ Validation failed:
  - STRATEGY must be one of: smart-pack, spt-pack, lpt-pack, cfs-pack, hybrid-pack, milp-opt
  - BEAM_WIDTH must be >= 1
```

**View current configuration**:

```bash
# Show default configuration
fillscheduler config show

# Show configuration from file
fillscheduler config show --file config.yaml

# Show configuration from file with environment overrides
export FILLSCHEDULER_STRATEGY="lpt-pack"
fillscheduler config show --file config.yaml
```

**Python API for configuration**:

```python
from fillscheduler.config_loader import export_default_config

# Export template config with comments
export_default_config("my_config.yaml", format="yaml", include_comments=True)
```

Edit the exported file, then use it:

```python
from fillscheduler.config_loader import load_config_with_overrides

# Load from file, with environment variable overrides
cfg = load_config_with_overrides("my_config.yaml")

# Or add runtime overrides (highest priority)
cfg = load_config_with_overrides(
    "my_config.yaml",
    STRATEGY="lpt-pack",  # Override file setting
    BEAM_WIDTH=5          # Override file setting
)
```

## Included Example Datasets

### Small Dataset (`examples/lots.csv`)
- 15 lots
- Mix of VialE and VialH types
- Good for testing and learning

### Large Dataset (`examples/lots_large.csv`)
- 500 lots
- 4 vial types
- Performance testing

### Generate Custom Data

```python
cd examples
python gen_lots.py  # Generates lots_large.csv
```

Customize the generator:

```python
generate_dataset(
    out_path=Path("my_lots.csv"),
    n_lots=100,
    vial_types=["TypeA", "TypeB", "TypeC"],
    min_vials=50000,
    max_vials=1000000,
    seed=42
)
```

## Real-World Scenarios

### Scenario 1: Urgent Production

You have urgent lots that must be scheduled first.

**Using CLI**:

```bash
# Sort your CSV so urgent lots appear first
# Then run the scheduler
fillscheduler schedule --data urgent_lots.csv --strategy smart-pack
```

**Using Python API**:

```python
# Prioritize specific lots
urgent_lots = [lot for lot in lots if lot.lot_id in ["URGENT1", "URGENT2"]]
normal_lots = [lot for lot in lots if lot not in urgent_lots]

# Schedule urgent first
all_lots = urgent_lots + normal_lots
activities, _, kpis = plan_schedule(all_lots, start_time, cfg)
```

### Scenario 2: Type Segregation

Minimize type changes by clustering similar lots.

**Using CLI**:

```bash
# Export default config
fillscheduler config export --output config.yaml

# Edit config.yaml to set:
# schedule:
#   strategy: "cfs-pack"
# constraints:
#   chg_diff_hours: 12.0

# Run with config
fillscheduler --config config.yaml schedule --data lots.csv
```

Or use environment variables:

```bash
export FILLSCHEDULER_STRATEGY="cfs-pack"
export FILLSCHEDULER_CHG_DIFF_HOURS="12.0"
fillscheduler schedule --data lots.csv
```

**Using Python API**:

```python
cfg = AppConfig(
    STRATEGY="cfs-pack",  # Cluster by type
    CHG_DIFF_HOURS=12.0,  # Make type changes expensive
)
```

### Scenario 3: Maximize Throughput

Focus on filling as much as possible with longer windows.

**Using CLI**:

```bash
# Use command-line options
fillscheduler schedule \
    --data lots.csv \
    --strategy lpt-pack

# With custom configuration
fillscheduler config export --output config.yaml
# Edit: window_hours: 144.0
fillscheduler --config config.yaml schedule --data lots.csv
```

**Using Python API**:

```python
cfg = AppConfig(
    STRATEGY="lpt-pack",  # Large lots first
    WINDOW_HOURS=144.0,   # Longer windows
)
```

## Integration Examples

### Example: Export to Excel

```python
import pandas as pd
from fillscheduler.io_utils import activities_to_dataframe

# Generate schedule
activities, _, kpis = plan_schedule(lots, start_time, cfg)

# Convert to DataFrame and export
df = activities_to_dataframe(activities, cfg)
df.to_excel("schedule.xlsx", index=False)
```

### Example: JSON API

```python
import json

# Convert activities to dict
schedule_json = []
for activity in activities:
    schedule_json.append({
        "start": activity.start.isoformat(),
        "end": activity.end.isoformat(),
        "type": activity.kind,
        "lot_id": activity.lot_id,
        "lot_type": activity.lot_type,
    })

# Export as JSON
with open("schedule.json", "w") as f:
    json.dump(schedule_json, f, indent=2)
```

## Troubleshooting

### Issue: Schedule takes too long

**Solution**: Use a faster strategy

CLI:
```bash
fillscheduler schedule --data lots.csv --strategy spt-pack
# or
fillscheduler schedule --data lots.csv --strategy lpt-pack
```

Python API:
```python
cfg.STRATEGY = "spt-pack"  # or "lpt-pack"
```

### Issue: Too many changeovers

**Solution**: Use clustering strategy

CLI:
```bash
export FILLSCHEDULER_STRATEGY="cfs-pack"
export FILLSCHEDULER_CFS_CLUSTER_ORDER="by_count"
fillscheduler schedule --data lots.csv
```

Python API:
```python
cfg.STRATEGY = "cfs-pack"
cfg.CFS_CLUSTER_ORDER = "by_count"
```

### Issue: Low utilization

**Solution**: Tune smart-pack parameters

CLI:
```bash
fillscheduler config export --output config.yaml
# Edit config.yaml:
# smart_pack:
#   slack_waste_weight: 5.0
#   beam_width: 5
fillscheduler --config config.yaml schedule --data lots.csv
```

Python API:
```python
cfg.SLACK_WASTE_WEIGHT = 5.0  # Penalize wasted space more
cfg.BEAM_WIDTH = 5            # More exploration
```

### Issue: Validation errors

**Check your configuration**:

```bash
fillscheduler config validate --file config.yaml
```

**Enable verbose mode for debugging**:

```bash
fillscheduler --verbose schedule --data lots.csv
```

### Issue: Command not found

**Solution**: Ensure package is installed in development mode

```bash
pip install -e .
fillscheduler --version
```

## Next Steps

- [Strategy Guide](strategies.md) - Learn about each strategy
- [Configuration](configuration.md) - Tune parameters
- [API Reference](api_reference.md) - Programmatic usage
