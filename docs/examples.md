# Examples

Usage examples and tutorials for Filling Scheduler.

## Basic Examples

### Example 1: Simple Schedule

```python
from fillscheduler.config import AppConfig
from fillscheduler.scheduler import plan_schedule
from fillscheduler.io_utils import read_lots_with_pandas
from datetime import datetime

# Configuration
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

```bash
# Use the comparison tool
python compare_runs.py \
    --data examples/lots.csv \
    --strategies smart-pack spt-pack lpt-pack \
    --out output/comparison
```

### Example 3: Custom Configuration

```python
cfg = AppConfig(
    STRATEGY="smart-pack",
    CLEAN_HOURS=18.0,      # Shorter cleaning
    WINDOW_HOURS=96.0,     # Tighter window
    BEAM_WIDTH=5,          # More exploration
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

You have urgent lots that must be scheduled first:

```python
# Prioritize specific lots
urgent_lots = [lot for lot in lots if lot.lot_id in ["URGENT1", "URGENT2"]]
normal_lots = [lot for lot in lots if lot not in urgent_lots]

# Schedule urgent first
all_lots = urgent_lots + normal_lots
activities, _, kpis = plan_schedule(all_lots, start_time, cfg)
```

### Scenario 2: Type Segregation

Minimize type changes:

```python
cfg = AppConfig(
    STRATEGY="cfs-pack",  # Cluster by type
    CHG_DIFF_HOURS=12.0,  # Make type changes expensive
)
```

### Scenario 3: Maximize Throughput

Focus on filling as much as possible:

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
```python
cfg.STRATEGY = "spt-pack"  # or "lpt-pack"
```

### Issue: Too many changeovers

**Solution**: Use clustering strategy
```python
cfg.STRATEGY = "cfs-pack"
cfg.CFS_CLUSTER_ORDER = "by_count"
```

### Issue: Low utilization

**Solution**: Tune smart-pack
```python
cfg.SLACK_WASTE_WEIGHT = 5.0  # Penalize wasted space more
cfg.BEAM_WIDTH = 5            # More exploration
```

## Next Steps

- [Strategy Guide](strategies.md) - Learn about each strategy
- [Configuration](configuration.md) - Tune parameters
- [API Reference](api_reference.md) - Programmatic usage
