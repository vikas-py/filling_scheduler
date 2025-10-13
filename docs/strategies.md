# Scheduling Strategies

Filling Scheduler provides 6 different scheduling strategies, each with different trade-offs between speed, solution quality, and use cases.

> **Note**: All configuration examples in this guide show programmatic configuration using `AppConfig`. You can also use [configuration files](configuration.md) (YAML/JSON) or environment variables for all settings shown.

## Strategy Comparison

| Strategy | Speed | Quality | Memory | Best For |
|----------|-------|---------|--------|----------|
| **smart-pack** | Fast (< 1s for 100 lots) | Excellent | Low | **Default, recommended** |
| **spt-pack** | Very Fast | Good | Very Low | Many small lots |
| **lpt-pack** | Very Fast | Good | Very Low | Datasets with large lots |
| **cfs-pack** | Fast | Good | Low | Type-heavy scenarios |
| **hybrid-pack** | Fast | Good-Excellent | Low | Balanced datasets |
| **milp-opt** | Slow (minutes) | **Optimal** | High | Small datasets (≤30 lots), benchmarking |

## Detailed Strategy Guide

### 1. Smart-Pack (Recommended)

**Algorithm**: Advanced greedy heuristic with look-ahead and slack optimization

**How it works**:
1. Scores each lot based on multiple factors:
   - Changeover penalties (type-dependent)
   - Window slack waste prediction
   - Type consistency bonuses
   - Dynamic penalties based on utilization
2. Uses beam search for limited look-ahead
3. Adaptively selects lots considering downstream effects

**Advantages**:
- Excellent balance of speed and quality
- Minimizes changeovers while maximizing utilization
- Avoids wasting window capacity
- Adapts to different dataset characteristics

**Configuration**:
```python
cfg = AppConfig(
    STRATEGY="smart-pack",
    BEAM_WIDTH=3,              # Look-ahead depth (1-5)
    SLACK_WASTE_WEIGHT=3.0,    # Penalty for wasted capacity
    STREAK_BONUS=1.0,          # Bonus for type consistency
)
```

**When to use**:
- ✅ Default choice for most datasets
- ✅ Mixed lot sizes and types
- ✅ Need good quality without long computation

**When to avoid**:
- ❌ Need provably optimal solution (use MILP)
- ❌ Dataset is extremely simple (SPT/LPT may be simpler)

---

### 2. SPT-Pack (Shortest Processing Time)

**Algorithm**: Sort lots by processing time (ascending), pack greedily

**How it works**:
1. Sort all lots from shortest to longest fill time
2. Group by type for efficient packing
3. Pack lots into windows greedily

**Advantages**:
- Very fast (microseconds for large datasets)
- Simple and predictable
- Good for many small lots

**Configuration**:
```python
cfg = AppConfig(STRATEGY="spt-pack")
```

**When to use**:
- ✅ Many small lots
- ✅ Speed is critical
- ✅ Quick scheduling needed

**When to avoid**:
- ❌ Mix of very large and very small lots
- ❌ Need to minimize changeovers specifically

---

### 3. LPT-Pack (Longest Processing Time)

**Algorithm**: Sort lots by processing time (descending), pack greedily

**How it works**:
1. Sort all lots from longest to shortest fill time
2. Pack large lots first, fill gaps with smaller lots
3. Aims to maximize window utilization

**Advantages**:
- Very fast
- Good utilization with large lots
- Simple bin-packing approach

**Configuration**:
```python
cfg = AppConfig(STRATEGY="lpt-pack")
```

**When to use**:
- ✅ Datasets dominated by large lots
- ✅ Want to schedule big jobs first
- ✅ Speed is important

**When to avoid**:
- ❌ Many small lots (SPT may be better)
- ❌ Complex type mixing patterns

---

### 4. CFS-Pack (Cluster-First, Schedule-Second)

**Algorithm**: Cluster by type, then schedule each cluster

**How it works**:
1. Group lots by vial type
2. Schedule each type cluster (using LPT or SPT within cluster)
3. Order clusters by various criteria (count, total volume)

**Advantages**:
- Minimizes type changeovers
- Predictable type-based scheduling
- Good for type-segregated production

**Configuration**:
```python
cfg = AppConfig(
    STRATEGY="cfs-pack",
    CFS_CLUSTER_ORDER="by_count",  # or "by_volume"
    CFS_WITHIN="LPT",              # or "SPT"
)
```

**When to use**:
- ✅ Type changeovers are very expensive
- ✅ Dataset has few types, many lots per type
- ✅ Type segregation preferred

**When to avoid**:
- ❌ Many types with few lots each
- ❌ Type mixing is acceptable/beneficial

---

### 5. Hybrid-Pack

**Algorithm**: Combination of heuristics with adaptive selection

**How it works**:
1. Combines elements of SPT, LPT, and type clustering
2. Dynamically weights strategies based on remaining lots
3. Emphasizes type streaks when beneficial

**Advantages**:
- Balanced approach
- Adapts to dataset characteristics
- Good for diverse datasets

**Configuration**:
```python
cfg = AppConfig(
    STRATEGY="hybrid-pack",
    HYBRID_SAME_TYPE_BONUS=2.0,
    HYBRID_SPT_WEIGHT=0.5,
    HYBRID_SWITCH_PENALTY_MULT=1.1,
)
```

**When to use**:
- ✅ Dataset characteristics are unknown
- ✅ Mix of small and large lots
- ✅ Want robustness across scenarios

**When to avoid**:
- ❌ Have specific constraints (use specialized strategy)
- ❌ Need provably optimal solution

---

### 6. MILP-Opt (Exact Optimization)

**Algorithm**: Mixed Integer Linear Programming (exact)

**How it works**:
1. Formulates scheduling as a mathematical optimization problem
2. Uses PuLP with CBC/GLPK solvers
3. Finds provably optimal solution (minimizes changeovers + clean blocks)
4. Enforces all constraints exactly

**Advantages**:
- **Provably optimal** solution
- Exact constraint satisfaction
- Useful for benchmarking heuristics

**Disadvantages**:
- Slow (minutes to hours for large instances)
- Limited to ≤30 lots (hard-coded safety limit)
- Requires PuLP library

**Configuration**:
```python
cfg = AppConfig(
    STRATEGY="milp-opt",
    MILP_MAX_LOTS=30,
    MILP_TIME_LIMIT=60,  # seconds
)
```

**When to use**:
- ✅ Small datasets (≤30 lots)
- ✅ Need provably optimal solution
- ✅ Benchmarking heuristic strategies
- ✅ Research/analysis

**When to avoid**:
- ❌ Large datasets (>30 lots)
- ❌ Need quick results
- ❌ Production scheduling (too slow)

---

## Performance Benchmarks

Based on typical datasets:

| Dataset Size | smart-pack | spt/lpt-pack | cfs/hybrid-pack | milp-opt |
|--------------|------------|--------------|-----------------|----------|
| 15 lots | < 0.1s | < 0.05s | < 0.1s | 1-10s |
| 50 lots | < 0.5s | < 0.1s | < 0.5s | ⚠️ Not recommended |
| 100 lots | < 1s | < 0.2s | < 1s | ❌ Too slow |
| 500 lots | < 5s | < 1s | < 5s | ❌ Not supported |

## Choosing the Right Strategy

### Decision Tree

```
Start
  ├─ Need provably optimal solution?
  │   └─ YES → Dataset ≤ 30 lots?
  │       ├─ YES → Use MILP-OPT ✓
  │       └─ NO → Use SMART-PACK (best heuristic) ✓
  │
  ├─ Need maximum speed?
  │   └─ YES → Many small lots?
  │       ├─ YES → Use SPT-PACK ✓
  │       └─ NO → Use LPT-PACK ✓
  │
  ├─ Type changeovers very expensive?
  │   └─ YES → Use CFS-PACK ✓
  │
  └─ General case → Use SMART-PACK ✓ (recommended)
```

### By Use Case

- **Production Scheduling**: `smart-pack` or `hybrid-pack`
- **Quick Estimates**: `spt-pack` or `lpt-pack`
- **Type-Segregated Production**: `cfs-pack`
- **Research/Optimization**: `milp-opt` (small datasets)
- **Benchmarking**: Run all, compare with `compare_runs.py`

## Tuning Strategies

### Smart-Pack Tuning

```python
# More exploration (slower, potentially better)
cfg.BEAM_WIDTH = 5
cfg.SLACK_WASTE_WEIGHT = 5.0

# Faster (less exploration)
cfg.BEAM_WIDTH = 1
cfg.SLACK_WASTE_WEIGHT = 1.0

# Emphasize type consistency
cfg.STREAK_BONUS = 3.0
cfg.DYNAMIC_SWITCH_MULT_MAX = 2.0
```

### CFS-Pack Tuning

```python
# Prioritize types with most lots
cfg.CFS_CLUSTER_ORDER = "by_count"

# Prioritize types with most volume
cfg.CFS_CLUSTER_ORDER = "by_volume"

# Within each type, use LPT or SPT
cfg.CFS_WITHIN = "LPT"  # or "SPT"
```

## Comparing Strategies

Use the comparison tool to evaluate all strategies:

```bash
python compare_runs.py --data examples/lots.csv --strategies smart-pack spt-pack lpt-pack cfs-pack hybrid-pack
```

This generates a comparative HTML report showing:
- KPIs for each strategy
- Side-by-side schedules
- Performance metrics
- Quality differences

## Next Steps

- [Configuration Guide](configuration.md) - Detailed tuning parameters
- [Examples](examples.md) - Real-world scenarios
- [API Reference](api_reference.md) - Programmatic usage
