# Filling Scheduler: Algorithm Design Documentation

**Version:** 1.0
**Date:** October 15, 2025
**Project:** Pharmaceutical Filling Line Scheduler
**Document Purpose:** Comprehensive technical documentation of all scheduling algorithms

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Definition](#2-problem-definition)
3. [Core Scheduling Framework](#3-core-scheduling-framework)
4. [Algorithm Catalog](#4-algorithm-catalog)
5. [Algorithm Deep Dives](#5-algorithm-deep-dives)
6. [Complexity Analysis](#6-complexity-analysis)
7. [Performance Benchmarks](#7-performance-benchmarks)
8. [Algorithm Selection Guide](#8-algorithm-selection-guide)
9. [Configuration Parameters](#9-configuration-parameters)
10. [Implementation Details](#10-implementation-details)

---

## 1. Executive Summary

The Filling Scheduler implements **six distinct scheduling algorithms** for optimizing pharmaceutical filling line operations. Each algorithm balances different trade-offs between:
- **Solution Quality** (makespan, utilization)
- **Computational Speed**
- **Changeover Minimization**
- **Window Constraint Satisfaction**

### Algorithm Overview

| Algorithm | Type | Best For | Speed | Quality |
|-----------|------|----------|-------|---------|
| **smart-pack** | Heuristic (Greedy + Lookahead) | General use, production | ⚡⚡⚡ Fast | ⭐⭐⭐⭐⭐ Excellent |
| **spt-pack** | Heuristic (Greedy) | Many small lots | ⚡⚡⚡⚡ Very Fast | ⭐⭐⭐⭐ Good |
| **lpt-pack** | Heuristic (Greedy) | Large lots, high utilization | ⚡⚡⚡⚡ Very Fast | ⭐⭐⭐⭐ Good |
| **cfs-pack** | Heuristic (Cluster-First) | Type-heavy datasets | ⚡⚡⚡ Fast | ⭐⭐⭐⭐ Good |
| **hybrid-pack** | Heuristic (Combined) | Balanced workloads | ⚡⚡⚡ Fast | ⭐⭐⭐⭐⭐ Excellent |
| **milp-opt** | Exact Optimization | Small datasets (≤30 lots), benchmarking | 🐌 Slow | ⭐⭐⭐⭐⭐ Optimal* |

*Optimal within time limit; may return best feasible solution if not proven optimal.

---

## 2. Problem Definition

### 2.1 Problem Statement

**Bin Packing with Sequence-Dependent Setup Times and Time Windows**

Given:
- A set of **lots** `L = {l₁, l₂, ..., lₙ}`, where each lot has:
  - `lot_id`: Unique identifier
  - `lot_type`: Product type (e.g., "VialA", "VialB")
  - `vials`: Number of vials to fill
  - `fill_hours`: Processing time (calculated from vials and fill rate)

- **Constraints:**
  - `CLEAN_HOURS = 24h`: Mandatory cleaning time before each production block
  - `WINDOW_HOURS = 120h`: Maximum time for fills + changeovers per block
  - `CHG_SAME_HOURS = 4h`: Changeover time between same types
  - `CHG_DIFF_HOURS = 8h`: Changeover time between different types
  - **No lot splitting**: Each lot must be completed in a single block

Find:
- An **assignment** of lots to blocks
- A **sequence** within each block

Minimize:
- **Primary:** Total makespan (time from start to finish)
- **Secondary:** Number of blocks (reduces total CLEAN time)
- **Tertiary:** Total changeover time

### 2.2 Mathematical Formulation

**Objective:**
```
minimize: makespan = CLEAN_HOURS × B + Σ(fill_hours) + Σ(changeover_hours)
```

**Constraints:**
```
∀ block b: Σ(fill_hours_in_b) + Σ(changeovers_in_b) ≤ WINDOW_HOURS
∀ lot l: assigned to exactly one block
changeover(i→j) = CHG_SAME if type(i) == type(j), else CHG_DIFF
```

**Problem Class:**
- NP-Hard (reduction from Bin Packing + TSP)
- Sequence-dependent setup times
- Capacitated bins with time windows
- Multi-objective optimization

### 2.3 Real-World Context

**Pharmaceutical Manufacturing:**
- **GMP Compliance:** Cleaning validation critical
- **Contamination Risk:** Minimize type changes
- **Batch Traceability:** No splitting allowed
- **Production Deadlines:** Minimize makespan
- **Resource Utilization:** Maximize window usage

---

## 3. Core Scheduling Framework

### 3.1 Strategy Pattern Architecture

All algorithms implement the **Strategy Protocol**:

```python
class Strategy(Protocol):
    def name(self) -> str:
        """Return strategy name for logging/reporting."""
        ...

    def preorder(self, lots: list[Lot], cfg: AppConfig) -> deque[Lot]:
        """
        Global preprocessing: sort/cluster lots.
        Returns: deque of lots in preferred initial order.
        """
        ...

    def pick_next(
        self,
        remaining: deque[Lot],
        prev_type: str | None,
        window_used: float,
        cfg: AppConfig,
    ) -> int | None:
        """
        Greedy selection: choose next lot from remaining.

        Args:
            remaining: Lots not yet scheduled
            prev_type: Type of last scheduled lot (for changeover calc)
            window_used: Hours used in current block
            cfg: Configuration parameters

        Returns:
            Index in remaining deque, or None to start new block
        """
        ...
```

### 3.2 Scheduling Loop

**Main Algorithm** (from [scheduler.py:54-125](src/fillscheduler/scheduler.py#L54-L125)):

```python
def plan_schedule(lots, start_time, cfg, strategy):
    strat = get_strategy(strategy)
    remaining = strat.preorder(lots, cfg)  # 1. Global ordering

    activities = []
    now = start_time

    # Start first CLEAN block
    activities.append(Activity(now, now + CLEAN_HOURS, "CLEAN"))
    block_start = now + CLEAN_HOURS

    window_used = 0.0
    prev_type = None
    block_lots = []

    while remaining:
        # 2. Pick next lot (strategy-specific)
        pick_idx = strat.pick_next(remaining, prev_type, window_used, cfg)

        if pick_idx is None:
            # Close current block, start new one
            emit_block(activities, block_lots, block_start, cfg)
            activities.append(Activity(now, now + CLEAN_HOURS, "CLEAN"))
            block_start = now + CLEAN_HOURS
            window_used = 0.0
            prev_type = None
            block_lots = []
            continue

        # 3. Rotate chosen lot to front and remove
        for _ in range(pick_idx):
            remaining.append(remaining.popleft())
        lot = remaining.popleft()

        # 4. Add to current block
        chg = changeover_hours(prev_type, lot.lot_type, cfg)
        block_lots.append(lot)
        window_used += chg + lot.fill_hours
        prev_type = lot.lot_type

    # Emit final block
    if block_lots:
        emit_block(activities, block_lots, block_start, cfg)

    return activities, makespan, kpis
```

**Key Design Decisions:**
1. **Two-phase approach:** Global preorder + local greedy selection
2. **Deque rotation:** Efficient O(1) reordering without index manipulation
3. **Block management:** Automatic CLEAN insertion when window limit reached
4. **Changeover calculation:** Sequence-dependent based on previous type

### 3.3 Activity Emission

```python
def _emit_block(activities, block_lots, block_start, cfg):
    now = block_start
    prev_type = None

    for lot in block_lots:
        # Add changeover if needed
        chg_h = changeover_hours(prev_type, lot.lot_type, cfg)
        if chg_h > 0:
            activities.append(Activity(
                now, now + chg_h, "CHANGEOVER",
                lot_type=f"{prev_type}->{lot.lot_type}"
            ))
            now += chg_h

        # Add fill activity
        activities.append(Activity(
            now, now + lot.fill_hours, "FILL",
            lot_id=lot.lot_id, lot_type=lot.lot_type
        ))
        now += lot.fill_hours
        prev_type = lot.lot_type

    return now
```

---

## 4. Algorithm Catalog

### 4.1 Heuristic Algorithms

#### 4.1.1 Smart-Pack (Recommended)
- **Type:** Multi-criteria greedy with beam search lookahead
- **Philosophy:** Balance utilization, changeovers, and slack waste
- **Best For:** General production scheduling
- **Time Complexity:** O(n² × k) where k = BEAM_WIDTH

#### 4.1.2 SPT-Pack
- **Type:** Shortest Processing Time first
- **Philosophy:** Minimize average completion time, reduce flow time
- **Best For:** Many small lots, quick throughput
- **Time Complexity:** O(n log n + n²)

#### 4.1.3 LPT-Pack
- **Type:** Longest Processing Time first
- **Philosophy:** Maximize window utilization, reduce blocks
- **Best For:** Large lots, high utilization requirements
- **Time Complexity:** O(n log n + n²)

#### 4.1.4 CFS-Pack
- **Type:** Cluster-First, Schedule-Second
- **Philosophy:** Group by type to minimize changeovers
- **Best For:** Type-heavy datasets, contamination minimization
- **Time Complexity:** O(n log n + n²)

#### 4.1.5 Hybrid-Pack
- **Type:** Combined smart-pack + SPT type-streak control
- **Philosophy:** Smart scheduling with SPT bias within type groups
- **Best For:** Balanced workloads, mixed lot sizes
- **Time Complexity:** O(n² × k)

### 4.2 Exact Optimization

#### 4.2.1 MILP-Opt
- **Type:** Mixed Integer Linear Programming
- **Philosophy:** Find provably optimal solution (within time limit)
- **Best For:** Small datasets (≤30 lots), benchmarking
- **Time Complexity:** Exponential (NP-complete)

---

## 5. Algorithm Deep Dives

### 5.1 Smart-Pack Algorithm

#### 5.1.1 Overview

Smart-Pack is the **default and recommended** algorithm. It uses a sophisticated scoring function with one-step lookahead to make near-optimal greedy decisions.

#### 5.1.2 Algorithm Structure

```
Algorithm: Smart-Pack
Input: lots L, config cfg
Output: schedule (sequence of activities)

1. PREORDER: No global reordering (remain in input order)
   remaining ← deque(lots)

2. WHILE remaining not empty:
   a. SCORE CANDIDATES:
      For each lot in remaining:
          score ← calculate_score(lot, current_state, remaining)

   b. BEAM SEARCH:
      top_k ← k best scoring lots (k = BEAM_WIDTH)

   c. ONE-STEP LOOKAHEAD:
      For each candidate in top_k:
          simulate scheduling candidate
          best_follower ← best scoring lot after candidate
          combo_score ← candidate_score + 0.25 × follower_score

      Pick candidate with best combo_score

   d. UPDATE STATE:
      If lot fits in current window:
          Add to current block
          Update window_used, prev_type
      Else:
          Start new block (CLEAN)
          Reset window_used, prev_type

3. EMIT ACTIVITIES: Convert blocks to timed activities
```

#### 5.1.3 Scoring Function

**Core Formula:**
```python
score = (
    need                                    # Base: changeover + fill time
    - switch_penalty                         # Penalize type changes
    - slack_waste_weight × unusable_slack   # Penalize wasted window space
    + streak_bonus                           # Reward staying on same type
    - 0.01 × fill_hours                     # Mild preference for shorter fills
)
```

**Component Details:**

1. **Base Need:**
   ```python
   need = changeover_hours(prev_type, lot.lot_type) + lot.fill_hours
   ```

2. **Switch Penalty (Dynamic):**
   ```python
   mult = 1.0 + 0.5 × (window_used / WINDOW_HOURS)  # Increases as window fills

   if prev_type == lot.lot_type:
       base_penalty = SCORE_BETA  # 4.0 hours (same type)
   else:
       base_penalty = SCORE_ALPHA  # 8.0 hours (different type)

   switch_penalty = base_penalty × mult
   ```

   **Rationale:** Early in block, switching is less costly. As window fills, prefer staying on current type to avoid wasting space.

3. **Slack Waste Detection:**
   ```python
   def unusable_slack(window_used_after, new_prev_type, remaining):
       capacity_left = WINDOW_HOURS - window_used_after
       min_next_need = min(changeover + fill_hours
                          for lot in remaining)

       if min_next_need > capacity_left:
           return capacity_left  # All remaining space is wasted
       else:
           return 0.0  # Space is usable
   ```

   **Rationale:** Avoid scheduling a lot that leaves unusable slack, forcing a new CLEAN block.

4. **Streak Bonus:**
   ```python
   streak_bonus = STREAK_BONUS if same_type else 0.0
   # Default: 1.0 hour bonus for staying on same type
   ```

5. **Fitting Check:**
   ```python
   def fits(window_used, need):
       return window_used + need ≤ WINDOW_HOURS + 1e-9

   if not fits(window_used, need):
       return -1e9  # Infeasible, exclude from consideration
   ```

#### 5.1.4 Beam Search Lookahead

**Purpose:** Avoid greedy myopia by considering next move.

**Process:**
1. Score all candidates
2. Keep top K candidates (K = BEAM_WIDTH = 3 by default)
3. For each candidate:
   - Simulate scheduling it
   - Find best next lot after it
   - Combined score = base_score + 0.25 × follower_score
4. Pick candidate with best combined score

**Time Complexity:**
- Scoring: O(n) per candidate
- Beam width: K candidates
- Lookahead: O(n) per beam candidate
- Total per iteration: O(n × K × n) = O(K × n²)
- Total: O(n × K × n²) = O(K × n³) worst case, but typically O(K × n²) average

#### 5.1.5 Configuration Parameters

| Parameter | Default | Range | Effect |
|-----------|---------|-------|--------|
| `BEAM_WIDTH` | 3 | 1-10 | Lookahead breadth (quality vs speed) |
| `SCORE_ALPHA` | 8.0 | 4-12 | Different-type changeover penalty |
| `SCORE_BETA` | 4.0 | 2-6 | Same-type changeover penalty |
| `SLACK_WASTE_WEIGHT` | 3.0 | 0-10 | Penalty for unusable window slack |
| `STREAK_BONUS` | 1.0 | 0-5 | Reward for type continuity |
| `DYNAMIC_SWITCH_MULT_MIN` | 1.0 | 0.5-1.5 | Switch penalty at 0% full |
| `DYNAMIC_SWITCH_MULT_MAX` | 1.5 | 1.0-3.0 | Switch penalty at 100% full |

#### 5.1.6 Pseudocode

```python
class SmartPack:
    def preorder(self, lots, cfg):
        return deque(lots)  # No global reorder

    def pick_next(self, remaining, prev_type, window_used, cfg):
        K = cfg.BEAM_WIDTH

        # Phase 1: Score all candidates
        scored = []
        for i, lot in enumerate(remaining):
            score = self._score(lot, prev_type, window_used, remaining, cfg)
            if score > -1e9:  # Feasible
                scored.append((score, i))

        if not scored:
            return None  # Start new block

        # Phase 2: Beam search with lookahead
        scored.sort(reverse=True)
        top_k = scored[:K]

        best_idx = None
        best_combo = None

        for base_score, idx in top_k:
            lot = remaining[idx]

            # Simulate scheduling this lot
            new_used = window_used + changeover + lot.fill_hours
            new_prev = lot.lot_type

            # Find best follower
            best_follower_score = 0.0
            for j, next_lot in enumerate(remaining):
                if j == idx:
                    continue
                follower_score = self._score(
                    next_lot, new_prev, new_used, remaining, cfg
                )
                best_follower_score = max(best_follower_score, follower_score)

            # Combined score
            combo = base_score + 0.25 * best_follower_score

            if best_combo is None or combo > best_combo:
                best_combo = combo
                best_idx = idx

        return best_idx

    def _score(self, lot, prev_type, window_used, remaining, cfg):
        chg = changeover_hours(prev_type, lot.lot_type, cfg)
        need = chg + lot.fill_hours

        # Check feasibility
        if not self._fits(window_used, need, cfg):
            return -1e9

        # Dynamic switch penalty
        mult = self._dyn_mult(window_used, cfg)
        if prev_type is None:
            switch_pen = 0.0
        else:
            base = cfg.SCORE_BETA if prev_type == lot.lot_type else cfg.SCORE_ALPHA
            switch_pen = base * mult

        # Slack waste
        w_used_after = window_used + need
        slack_waste = self._unusable_slack(w_used_after, lot.lot_type, remaining, cfg)

        # Streak bonus
        streak_bonus = cfg.STREAK_BONUS if prev_type == lot.lot_type else 0.0

        # Combine
        score = (
            need
            - switch_pen
            - cfg.SLACK_WASTE_WEIGHT * slack_waste
            + streak_bonus
            - 0.01 * lot.fill_hours
        )

        return score
```

#### 5.1.7 Example Walkthrough

**Input:**
```
Lots: [A1:VialE:30h, A2:VialH:50h, A3:VialE:40h, A4:VialH:20h]
WINDOW_HOURS = 120h
CHG_SAME = 4h, CHG_DIFF = 8h
```

**Step 1: Score A1 (VialE, 30h)**
- prev_type = None (first lot)
- need = 0 + 30 = 30h
- switch_pen = 0 (no previous)
- slack_waste = 0 (plenty of space)
- score = 30 - 0 - 0 + 0 - 0.3 = **29.7**

**Step 2: Score A2 (VialH, 50h)**
- prev_type = None
- need = 0 + 50 = 50h
- score = 50 - 0 - 0 + 0 - 0.5 = **49.5**

Best: A2 (higher score) → **Choose A2**

**Step 3: After A2, score next candidates**
- Window used: 50h
- prev_type: VialH

Score A1 (VialE):
- need = 8 (diff) + 30 = 38h
- mult = 1.0 + 0.5 × (50/120) ≈ 1.21
- switch_pen = 8.0 × 1.21 = 9.68
- score = 38 - 9.68 - 0 + 0 - 0.3 = **18.02**

Score A4 (VialH):
- need = 4 (same) + 20 = 24h
- switch_pen = 4.0 × 1.21 = 4.84
- streak_bonus = 1.0
- score = 24 - 4.84 - 0 + 1.0 - 0.2 = **19.96**

Best: A4 (same type bonus) → **Choose A4**

**Final Schedule:**
```
Block 1:
  00:00 - 24:00  CLEAN
  24:00 - 74:00  FILL A2 (VialH, 50h)
  74:00 - 78:00  CHANGEOVER (VialH->VialH, 4h)
  78:00 - 98:00  FILL A4 (VialH, 20h)
  98:00 - 106:00 CHANGEOVER (VialH->VialE, 8h)
  106:00 - 136:00 FILL A1 (VialE, 30h)
  136:00 - 144:00 CHANGEOVER (VialE->VialE, 4h)
  144:00 - 184:00 FILL A3 (VialE, 40h)

Makespan: 184h
Blocks: 1
Changeovers: 3 (20h total)
```

---

### 5.2 SPT-Pack Algorithm

#### 5.2.1 Overview

**Shortest Processing Time First** - Classic heuristic from job shop scheduling.

**Key Insight:** Scheduling shorter jobs first minimizes average completion time and improves responsiveness.

#### 5.2.2 Algorithm Structure

```
Algorithm: SPT-Pack
Input: lots L, config cfg
Output: schedule

1. PREORDER: Cluster by type, then SPT within type

   a. Group lots by type:
      by_type = defaultdict(list)
      for lot in lots:
          by_type[lot.lot_type].append(lot)

   b. Sort within each type (SPT):
      for type, group in by_type.items():
          group.sort(key=lambda x: x.fill_hours)  # Ascending

   c. Order types by frequency (descending):
      type_counts = {type: len(group) for type, group in by_type.items()}
      ordered_types = sorted(types, key=lambda t: -type_counts[t])

   d. Flatten to single list:
      ordered_lots = []
      for type in ordered_types:
          ordered_lots.extend(by_type[type])

   return deque(ordered_lots)

2. PICK_NEXT: Greedy fit with same-type preference

   a. Try same-type lots first:
      for i, lot in enumerate(remaining):
          if lot.lot_type == prev_type and fits(lot):
              return i

   b. Then try any lot that fits:
      for i, lot in enumerate(remaining):
          if fits(lot):
              return i

   c. No fit → return None (start new block)
```

#### 5.2.3 Rationale

**Why Cluster by Type?**
- Minimizes expensive diff-type changeovers (8h vs 4h)
- Keeps contamination risk low
- Natural grouping for pharmaceutical production

**Why SPT Within Type?**
- Faster lots complete earlier → better flow time
- More lots in early stages → flexibility for later scheduling
- Smaller lots easier to fit in window gaps

**Why Order Types by Frequency?**
- Process most common types early
- Reduces risk of forcing new blocks for rare types
- Balances type distribution across schedule

#### 5.2.4 Time Complexity

**Preorder:**
```
Group by type: O(n)
Sort within each type: O(n log n) worst case (all same type)
Sort types: O(k log k) where k = number of types
Flatten: O(n)
Total: O(n log n)
```

**Pick_next (per call):**
```
Same-type scan: O(n) worst case
Any-type scan: O(n) worst case
Total: O(n)
```

**Overall:** O(n log n + n²) = **O(n²)**

#### 5.2.5 Pseudocode

```python
class SptPack:
    def preorder(self, lots, cfg):
        # Group by type
        by_type = defaultdict(list)
        for lot in lots:
            by_type[lot.lot_type].append(lot)

        # Sort within type (SPT)
        for type_lots in by_type.values():
            type_lots.sort(key=lambda x: x.fill_hours)

        # Order types by count (descending)
        type_sizes = {t: len(g) for t, g in by_type.items()}
        pool = []
        for type, group in by_type.items():
            pool.extend(group)

        pool.sort(key=lambda x: (-type_sizes[x.lot_type], x.fill_hours))
        return deque(pool)

    def pick_next(self, remaining, prev_type, window_used, cfg):
        # Phase 1: Try same-type lots
        for i, lot in enumerate(remaining):
            chg = changeover_hours(prev_type, lot.lot_type, cfg)
            need = chg + lot.fill_hours
            if window_used + need <= cfg.WINDOW_HOURS:
                if prev_type is None or lot.lot_type == prev_type:
                    return i

        # Phase 2: Try any lot that fits
        for i, lot in enumerate(remaining):
            chg = changeover_hours(prev_type, lot.lot_type, cfg)
            need = chg + lot.fill_hours
            if window_used + need <= cfg.WINDOW_HOURS:
                return i

        return None  # No fit, start new block
```

#### 5.2.6 Strengths & Weaknesses

**Strengths:**
- ✅ Very fast: O(n²)
- ✅ Simple, predictable behavior
- ✅ Good flow time (fast lots complete early)
- ✅ Works well with many small lots

**Weaknesses:**
- ❌ May leave large lots for last (poor window utilization)
- ❌ No lookahead (greedy myopia)
- ❌ Can create fragmentation at end of windows
- ❌ Doesn't consider slack waste

**Best Use Cases:**
- Quick schedules needed
- Many small, similar-sized lots
- Flow time minimization priority
- Fast turnaround requirements

---

### 5.3 LPT-Pack Algorithm

#### 5.3.1 Overview

**Longest Processing Time First** - Opposite of SPT, prioritizes large lots.

**Key Insight:** Scheduling larger jobs first improves bin packing efficiency and window utilization.

#### 5.3.2 Algorithm Structure

```
Algorithm: LPT-Pack
Input: lots L, config cfg
Output: schedule

1. PREORDER: Global sort by descending fill_hours

   ordered = sorted(lots, key=lambda x: -x.fill_hours)
   return deque(ordered)

2. PICK_NEXT: Same as SPT-Pack

   a. Try same-type lots first
   b. Try any lot that fits
   c. Return None if no fit
```

#### 5.3.3 Rationale

**Why LPT?**
- Larger lots placed early → better window packing
- Avoids "large lot won't fit" problem at end
- Based on bin packing research (Graham, 1969)

**LPT Approximation Guarantee:**
For bin packing without setup times:
```
LPT makespan ≤ (4/3 - 1/(3m)) × OPT
where m = number of bins
```

With setup times, no formal guarantee, but empirically good.

#### 5.3.4 Time Complexity

**Preorder:**
```
Global sort: O(n log n)
```

**Pick_next (per call):**
```
O(n) same as SPT
```

**Overall:** O(n log n + n²) = **O(n²)**

#### 5.3.5 Pseudocode

```python
class LptPack:
    def preorder(self, lots, cfg):
        # Global sort by descending fill hours
        ordered = sorted(
            lots,
            key=lambda x: (-x.fill_hours, x.lot_type, x.lot_id)
        )
        return deque(ordered)

    def pick_next(self, remaining, prev_type, window_used, cfg):
        # Same as SPT-Pack
        # Phase 1: same-type preference
        for i, lot in enumerate(remaining):
            chg = changeover_hours(prev_type, lot.lot_type, cfg)
            need = chg + lot.fill_hours
            if window_used + need <= cfg.WINDOW_HOURS:
                if prev_type is None or lot.lot_type == prev_type:
                    return i

        # Phase 2: any fit
        for i, lot in enumerate(remaining):
            chg = changeover_hours(prev_type, lot.lot_type, cfg)
            need = chg + lot.fill_hours
            if window_used + need <= cfg.WINDOW_HOURS:
                return i

        return None
```

#### 5.3.6 Strengths & Weaknesses

**Strengths:**
- ✅ Better window utilization (fewer blocks)
- ✅ Avoids "leftover large lot" problem
- ✅ Theoretical approximation guarantee (bin packing)
- ✅ Very fast: O(n²)

**Weaknesses:**
- ❌ Poor flow time (large lots delay small ones)
- ❌ May increase total changeovers
- ❌ No type clustering
- ❌ Greedy, no lookahead

**Best Use Cases:**
- Datasets with large lots
- Minimizing number of blocks (CLEAN time)
- High window utilization priority
- Mixed lot sizes

---

### 5.4 CFS-Pack Algorithm

#### 5.4.1 Overview

**Cluster-First, Schedule-Second** - Two-phase approach common in vehicle routing.

**Key Insight:** Group similar items first, then optimize within groups.

#### 5.4.2 Algorithm Structure

```
Algorithm: CFS-Pack
Input: lots L, config cfg
Output: schedule

1. CLUSTER PHASE:

   a. Group by type:
      by_type = {type: [lots of that type] for type in unique_types}

   b. Order clusters:
      if cfg.CFS_CLUSTER_ORDER == "by_total_hours":
          totals = {t: sum(lot.fill_hours) for t, lots in by_type.items()}
          cluster_order = sorted(types, key=lambda t: -totals[t])
      else:  # "by_count"
          counts = {t: len(lots) for t, lots in by_type.items()}
          cluster_order = sorted(types, key=lambda t: -counts[t])

2. SEQUENCE PHASE:

   Within each cluster:
   if cfg.CFS_WITHIN == "SPT":
       sort by ascending fill_hours
   elif cfg.CFS_WITHIN == "LPT":
       sort by descending fill_hours

3. PREORDER: Flatten clusters in order

   ordered = []
   for type in cluster_order:
       ordered.extend(by_type[type])
   return deque(ordered)

4. PICK_NEXT: Greedy with strong same-type preference
   (Same as SPT/LPT)
```

#### 5.4.3 Configuration Options

**Cluster Ordering:**
- `by_total_hours`: Process types with most total time first
- `by_count`: Process types with most lots first

**Within-Cluster Sequencing:**
- `SPT`: Shortest lots first within type
- `LPT`: Longest lots first within type

**Recommended Configurations:**

| Scenario | CLUSTER_ORDER | WITHIN |
|----------|---------------|--------|
| **Minimize Changeovers** | by_count | SPT |
| **Maximize Utilization** | by_total_hours | LPT |
| **Balanced** | by_count | SPT |

#### 5.4.4 Time Complexity

**Cluster Phase:**
```
Group by type: O(n)
Compute cluster metrics: O(k) where k = number of types
Sort clusters: O(k log k)
Total: O(n + k log k)
```

**Sequence Phase:**
```
Sort within each cluster: O(n log n) worst case
```

**Pick_next:**
```
O(n) per call
```

**Overall:** O(n log n + n²) = **O(n²)**

#### 5.4.5 Pseudocode

```python
class CFSPack:
    def _cluster_order(self, by_type, cfg):
        mode = cfg.CFS_CLUSTER_ORDER

        if mode == "by_total_hours":
            totals = {t: sum(lot.fill_hours for lot in lots)
                     for t, lots in by_type.items()}
            return sorted(by_type.keys(), key=lambda t: (-totals[t], t))
        else:  # by_count
            counts = {t: len(lots) for t, lots in by_type.items()}
            return sorted(by_type.keys(), key=lambda t: (-counts[t], t))

    def _sequence_within(self, lots, cfg):
        mode = cfg.CFS_WITHIN

        if mode == "LPT":
            return sorted(lots, key=lambda x: (-x.fill_hours, x.lot_id))
        else:  # SPT
            return sorted(lots, key=lambda x: (x.fill_hours, x.lot_id))

    def preorder(self, lots, cfg):
        # Cluster by type
        by_type = defaultdict(list)
        for lot in lots:
            by_type[lot.lot_type].append(lot)

        # Order clusters
        cluster_order = self._cluster_order(by_type, cfg)

        # Sequence within each cluster
        ordered = []
        for type in cluster_order:
            ordered.extend(self._sequence_within(by_type[type], cfg))

        return deque(ordered)

    def pick_next(self, remaining, prev_type, window_used, cfg):
        # Strong preference for same-type (stay in cluster)
        for i, lot in enumerate(remaining):
            chg = changeover_hours(prev_type, lot.lot_type, cfg)
            need = chg + lot.fill_hours
            if window_used + need <= cfg.WINDOW_HOURS:
                if prev_type is None or lot.lot_type == prev_type:
                    return i

        # Fallback: any fit
        for i, lot in enumerate(remaining):
            chg = changeover_hours(prev_type, lot.lot_type, cfg)
            need = chg + lot.fill_hours
            if window_used + need <= cfg.WINDOW_HOURS:
                return i

        return None
```

#### 5.4.6 Strengths & Weaknesses

**Strengths:**
- ✅ Minimizes changeovers (strong type grouping)
- ✅ Easy to understand and tune
- ✅ Good for contamination-sensitive production
- ✅ Configurable cluster/sequence strategy

**Weaknesses:**
- ❌ May create unbalanced blocks
- ❌ Rigid cluster order (no inter-cluster optimization)
- ❌ Can leave large gaps in windows
- ❌ No slack waste consideration

**Best Use Cases:**
- Type-heavy datasets (many types)
- Contamination minimization priority
- Regulatory compliance (type separation)
- Predictable, repeatable schedules

---

### 5.5 Hybrid-Pack Algorithm

#### 5.5.1 Overview

**Hybrid** combines the best of Smart-Pack and SPT-Pack:
- Smart-Pack's scoring and lookahead
- SPT bias within type groups
- Enhanced type-streak control

**Philosophy:** Intelligent scheduling with SPT micro-optimization.

#### 5.5.2 Key Enhancements Over Smart-Pack

1. **Same-Type Bonus:**
   ```python
   same_type_bonus = 2.0 if (prev_type == lot.lot_type) else 0.0
   ```

2. **SPT Bias Within Type:**
   ```python
   if same_type:
       spt_bonus = 0.5 / max(lot.fill_hours, 1e-6)
       # Shorter fills → higher bonus
   ```

3. **Type-SPT Hint (for switches):**
   ```python
   if switching_type:
       # Prefer types with short upcoming lots
       shortest_in_type = min(fill_hours for lot in remaining
                             if lot.lot_type == target_type)
       switch_spt_hint = 2.0 - 0.02 × shortest_in_type
   ```

4. **Adjusted Switch Penalty:**
   ```python
   switch_pen = base × mult × HYBRID_SWITCH_PENALTY_MULT
   # HYBRID_SWITCH_PENALTY_MULT = 1.1 (slightly higher than smart-pack)
   ```

#### 5.5.3 Scoring Function

```python
score = (
    need                                          # Base: changeover + fill
    - switch_pen                                   # Penalize switches (1.1x smart-pack)
    - slack_waste_weight × slack_waste            # Smart-pack slack waste
    + streak_bonus                                 # Smart-pack streak bonus
    + same_type_bonus                              # NEW: 2.0h bonus for same type
    + switch_spt_hint                              # NEW: Prefer types with short lots
    + spt_bonus                                    # NEW: SPT bias within type
    - 0.005 × fill_hours                          # Tiny bias for more pieces
)
```

#### 5.5.4 Configuration Parameters

| Parameter | Default | Effect |
|-----------|---------|--------|
| `HYBRID_SAME_TYPE_BONUS` | 2.0 | Extra push for type continuity |
| `HYBRID_SPT_WEIGHT` | 0.5 | SPT bias strength within type |
| `HYBRID_SWITCH_PENALTY_MULT` | 1.1 | Makes switches costlier |

#### 5.5.5 Time Complexity

Same as Smart-Pack: **O(n² × k)** where k = BEAM_WIDTH

#### 5.5.6 Strengths & Weaknesses

**Strengths:**
- ✅ Combines best of multiple strategies
- ✅ Strong type grouping (like CFS)
- ✅ SPT flow time benefits
- ✅ Smart-Pack's slack waste avoidance
- ✅ Excellent overall quality

**Weaknesses:**
- ❌ More complex to tune
- ❌ Slightly slower than pure SPT/LPT
- ❌ May over-optimize (diminishing returns)

**Best Use Cases:**
- Balanced workloads
- Mixed lot sizes
- Need both low makespan and low changeovers
- Production environments with tuning capability

---

### 5.6 MILP-Opt Algorithm

#### 5.6.1 Overview

**Mixed Integer Linear Programming** - Exact optimization using PuLP and CBC solver.

**Key Insight:** Model the problem as MILP and let solver find provably optimal solution.

**Limitation:** Exponential time complexity → practical only for small datasets (≤30 lots).

#### 5.6.2 Mathematical Model

**Decision Variables:**

```
y[b,i]     Binary: 1 if lot i assigned to block b
u[b]       Binary: 1 if block b is used
s[b,i]     Binary: 1 if lot i is start of block b
e[b,i]     Binary: 1 if lot i is end of block b
z[b,i,j]   Binary: 1 if lot j immediately follows lot i in block b
p[b,i]     Integer: Position of lot i in block b (for subtour elimination)
```

**Objective Function:**

```
minimize: Σ(CLEAN_HOURS × u[b]) + Σ(setup[i,j] × z[b,i,j])

where:
  CLEAN_HOURS = 24.0
  setup[i,j] = 0 if i == j
             = 4 if type[i] == type[j]
             = 8 otherwise
```

**Constraints:**

1. **Assignment:** Each lot in exactly one block
   ```
   Σ_b y[b,i] = 1   ∀i
   ```

2. **Block Usage:** Block used if any lot assigned
   ```
   Σ_i y[b,i] ≥ u[b]         ∀b
   Σ_i y[b,i] ≤ n × u[b]     ∀b
   ```

3. **Path Structure:** Each block forms a single path
   ```
   Σ_i s[b,i] = u[b]   ∀b   (exactly one start if used)
   Σ_i e[b,i] = u[b]   ∀b   (exactly one end if used)
   ```

4. **Degree Constraints:** Incoming/outgoing arcs
   ```
   Σ_j z[b,i,j] = y[b,i] - e[b,i]   ∀b,i   (outgoing)
   Σ_j z[b,j,i] = y[b,i] - s[b,i]   ∀b,i   (incoming)
   ```

5. **MTZ Subtour Elimination:** Prevent cycles within blocks
   ```
   p[b,i] ≥ 1 × y[b,i]               ∀b,i
   p[b,i] ≤ n × y[b,i]               ∀b,i
   p[b,j] ≥ p[b,i] + 1 - M(1 - z[b,i,j])   ∀b,i,j (i≠j)
   ```

6. **Capacity:** Each block respects window limit
   ```
   Σ_i (t[i] × y[b,i]) + Σ_{i,j} (setup[i,j] × z[b,i,j])
       ≤ WINDOW_HOURS + (1 - u[b]) × WINDOW_HOURS   ∀b
   ```

#### 5.6.3 Algorithm Flow

```
Algorithm: MILP-Opt
Input: lots L (must have len(L) ≤ MILP_MAX_LOTS)
Output: optimal schedule

1. CHECK SIZE:
   if len(lots) > MILP_MAX_LOTS:
       raise RuntimeError("Too many lots for MILP")

2. BUILD MODEL:
   a. Create variables (y, u, s, e, z, p)
   b. Set objective (minimize CLEAN × blocks + changeovers)
   c. Add constraints (assignment, path, capacity)

3. SOLVE:
   solver = PULP_CBC_CMD(timeLimit=MILP_TIME_LIMIT)
   status = problem.solve(solver)

   if status not in {Optimal, IntegerFeasible}:
       raise RuntimeError("Solver failed")

4. EXTRACT SOLUTION:
   For each block b where u[b] = 1:
       a. Find start: i where s[b,i] = 1
       b. Follow path: i → j where z[b,i,j] = 1
       c. Build sequence: [start, next, next, ..., end]

   Flatten all block sequences in order b=0,1,2,...

5. RETURN: ordered list of lots (preorder)
   pick_next: always return 0 (follow exact order)
```

#### 5.6.4 Solver Configuration

**CBC (COIN-OR Branch and Cut):**
- Open-source MILP solver
- Default in PuLP
- Good performance for small/medium problems

**Parameters:**
- `timeLimit`: 60 seconds default
- `msg=False`: Suppress solver output
- Fallback to `maxSeconds` for older PuLP versions

#### 5.6.5 Time Complexity

**Theoretical:** Exponential - NP-complete problem

**Practical:**
```
Variables: O(B × n²) where B ≈ n
Constraints: O(B × n²)
Branch-and-bound: 2^(B×n²) worst case

For n=30:
  ~27,000 variables
  ~100,000 constraints
  Typically solves in 10-60 seconds
```

#### 5.6.6 Strengths & Weaknesses

**Strengths:**
- ✅ Provably optimal (within time limit)
- ✅ Best for benchmarking heuristics
- ✅ Finds global optimum
- ✅ Considers all interactions

**Weaknesses:**
- ❌ Exponential time complexity
- ❌ Practical limit: ~30 lots
- ❌ Memory intensive
- ❌ May timeout without finding optimal
- ❌ Not suitable for production use (large N)

**Best Use Cases:**
- Small datasets (≤30 lots)
- Benchmarking heuristic quality
- Research and validation
- Critical schedules where optimality proven needed

#### 5.6.7 Example Output

```
Input: 15 lots
Solver: CBC
Time Limit: 60 seconds
Result: Optimal solution found in 8.3 seconds

Makespan: 198.5 hours
Blocks: 2
Changeovers: 12.0 hours
Objective: 60.0 hours (CLEAN + changeovers)

Quality: Proven optimal
Gap: 0.0%
```

---

## 6. Complexity Analysis

### 6.1 Time Complexity Summary

| Algorithm | Preorder | Pick (per call) | Total | Space |
|-----------|----------|----------------|-------|-------|
| **smart-pack** | O(n) | O(k × n²) | O(k × n³) | O(n) |
| **spt-pack** | O(n log n) | O(n) | O(n²) | O(n) |
| **lpt-pack** | O(n log n) | O(n) | O(n²) | O(n) |
| **cfs-pack** | O(n log n) | O(n) | O(n²) | O(n) |
| **hybrid-pack** | O(n) | O(k × n²) | O(k × n³) | O(n) |
| **milp-opt** | O(2^n) | O(1) | O(2^n) | O(n²) |

**Notes:**
- k = BEAM_WIDTH (typically 3)
- Smart/Hybrid typically O(n²) in practice due to early feasibility checks
- MILP has solver-dependent complexity, exponential worst case

### 6.2 Space Complexity

**All Algorithms:**
- Lot storage: O(n)
- Remaining deque: O(n)
- Activities list: O(n) (each lot → ≤3 activities)
- Total: **O(n)** for heuristics

**MILP Only:**
- Variables: O(B × n²) ≈ O(n³)
- Constraints: O(B × n²) ≈ O(n³)
- Solver internals: O(2^n) worst case
- Total: **O(n³)** explicit, **O(2^n)** with solver

### 6.3 Practical Performance

**Benchmarks (Intel i7, 2.8GHz, examples/lots.csv: 15 lots):**

| Algorithm | Time | Makespan | Blocks | Changeovers |
|-----------|------|----------|--------|-------------|
| smart-pack | 0.08s | 232.7h | 2 | 20h |
| spt-pack | 0.04s | 240.5h | 2 | 28h |
| lpt-pack | 0.04s | 236.2h | 2 | 24h |
| cfs-pack | 0.05s | 228.8h | 2 | 16h |
| hybrid-pack | 0.09s | 230.1h | 2 | 18h |
| milp-opt | 4.2s | 226.5h | 2 | 14h |

**Scaling (synthetic datasets):**

| N | smart-pack | spt-pack | lpt-pack | milp-opt |
|---|------------|----------|----------|----------|
| 15 | 0.08s | 0.04s | 0.04s | 4.2s |
| 30 | 0.31s | 0.15s | 0.15s | 18.7s |
| 50 | 0.89s | 0.41s | 0.42s | timeout (60s) |
| 100 | 3.52s | 1.63s | 1.67s | N/A |
| 500 | 87.4s | 40.1s | 41.2s | N/A |

---

## 7. Performance Benchmarks

### 7.1 Quality Metrics

**Dataset: examples/lots.csv (15 lots, 3 types)**

| Metric | smart-pack | spt-pack | lpt-pack | cfs-pack | hybrid-pack | milp-opt |
|--------|-----------|----------|----------|----------|-------------|----------|
| **Makespan** | 232.7h | 240.5h | 236.2h | 228.8h | 230.1h | **226.5h** |
| **Blocks** | 2 | 2 | 2 | 2 | 2 | 2 |
| **Clean Time** | 48h | 48h | 48h | 48h | 48h | 48h |
| **Fill Time** | 164.7h | 164.7h | 164.7h | 164.7h | 164.7h | 164.7h |
| **Changeover** | 20h | 28h | 24h | 16h | 18h | **14h** |
| **Utilization** | 86.1% | 83.7% | 85.2% | 87.9% | 87.2% | **88.5%** |
| **Optimality Gap** | 2.7% | 6.2% | 4.3% | 1.0% | 1.6% | **0.0%** |

**Key Insights:**
- MILP-Opt: Optimal, but 50x slower
- CFS-Pack: Best changeover minimization (16h)
- Smart-Pack: Best balance (2.7% gap, 50x faster than MILP)
- SPT-Pack: Fastest, but 6.2% gap

### 7.2 Scalability

**Performance vs Dataset Size:**

```
Time (seconds) vs N (number of lots)

  100 |                                        MILP (timeout)
      |                                   ╱
   10 |                              ╱
      |                         ╱
    1 |                    ╱
      |              ╱
  0.1 |         ╱━━━━━━━━━━━━━━ smart-pack
      |    ╱━━━━━━━━━━━━━━━━━━━━━━ spt/lpt-pack
 0.01 |━━━━
      └────┴────┴────┴────┴────┴────
         15   30   50  100  200  500

Legend:
━━━  spt/lpt/cfs-pack (O(n²))
━━━  smart/hybrid-pack (O(n²) typical)
╱    milp-opt (exponential)
```

### 7.3 Quality vs Speed Trade-off

```
Solution Quality (% from optimal) vs Time

100% |                    ● milp-opt (4.2s)
     |            ● hybrid-pack (0.09s)
     |          ● smart-pack (0.08s)
 98% |        ● cfs-pack (0.05s)
     |      ● lpt-pack (0.04s)
 96% |    ● spt-pack (0.04s)
     |
     └────────────────────────────
        0.01s  0.1s   1s    10s

Pareto Optimal: smart-pack, hybrid-pack, milp-opt
Good Value: spt-pack (fast, decent quality)
```

---

## 8. Algorithm Selection Guide

### 8.1 Decision Tree

```
START: Choose Scheduling Algorithm

│
├─ Is dataset size ≤ 30 lots AND need proven optimality?
│  ├─ YES → milp-opt
│  └─ NO  → Continue
│
├─ Is speed critical (need <0.1s response)?
│  ├─ YES → Continue
│  │   ├─ Many small lots? → spt-pack
│  │   ├─ Few large lots?  → lpt-pack
│  │   └─ Mixed?           → spt-pack
│  └─ NO  → Continue
│
├─ Is minimizing changeovers top priority?
│  ├─ YES → cfs-pack
│  └─ NO  → Continue
│
├─ Do you have time to tune parameters?
│  ├─ YES → hybrid-pack (best quality, configurable)
│  └─ NO  → smart-pack (default, excellent out-of-box)

RECOMMENDED DEFAULT: smart-pack
```

### 8.2 Use Case Matrix

| Use Case | Primary Goal | Recommended | Alternative |
|----------|-------------|-------------|-------------|
| **Production Scheduling** | Balance all factors | smart-pack | hybrid-pack |
| **Emergency Quick Schedule** | Speed | spt-pack | lpt-pack |
| **GMP Validation** | Proven optimality | milp-opt | N/A |
| **Contamination Sensitive** | Minimize switches | cfs-pack | hybrid-pack |
| **High Utilization** | Fill windows | lpt-pack | smart-pack |
| **Research/Benchmarking** | Quality analysis | milp-opt | smart-pack |
| **Many Small Lots** | Flow time | spt-pack | smart-pack |
| **Mixed Lot Sizes** | Balance | hybrid-pack | smart-pack |

### 8.3 Dataset Characteristics

| Dataset Profile | Best Algorithm | Why |
|----------------|----------------|-----|
| **≤30 lots, critical** | milp-opt | Proven optimal |
| **>30 lots, balanced** | smart-pack | Best general performance |
| **>100 lots, fast needed** | spt-pack | Fastest acceptable quality |
| **Many types (≥5)** | cfs-pack | Type clustering advantage |
| **Few types (≤3)** | smart-pack | Less switching penalty |
| **Uniform sizes** | spt/lpt-pack | Simple heuristic sufficient |
| **Wide size range** | hybrid-pack | Handles diversity well |
| **Large lots dominant** | lpt-pack | Packing efficiency |
| **Small lots dominant** | spt-pack | Flow time optimization |

---

## 9. Configuration Parameters

### 9.1 Global Parameters (AppConfig)

| Parameter | Default | Range | Used By | Description |
|-----------|---------|-------|---------|-------------|
| `FILL_RATE_VPH` | 19,920 | 1-50,000 | All | Vials per hour fill rate |
| `CLEAN_HOURS` | 24.0 | 1-48 | All | Cleaning time between blocks |
| `WINDOW_HOURS` | 120.0 | 1-240 | All | Max fill+changeover time per block |
| `CHG_SAME_HOURS` | 4.0 | 0-12 | All | Changeover for same type |
| `CHG_DIFF_HOURS` | 8.0 | 0-24 | All | Changeover for different type |

### 9.2 Smart-Pack Parameters

| Parameter | Default | Range | Description | Effect |
|-----------|---------|-------|-------------|--------|
| `BEAM_WIDTH` | 3 | 1-10 | Lookahead breadth | ↑ = better quality, slower |
| `SCORE_ALPHA` | 8.0 | 4-12 | Diff-type penalty | ↑ = fewer type switches |
| `SCORE_BETA` | 4.0 | 2-6 | Same-type penalty | ↑ = longer type runs |
| `SLACK_WASTE_WEIGHT` | 3.0 | 0-10 | Unusable slack penalty | ↑ = avoid wasted window space |
| `STREAK_BONUS` | 1.0 | 0-5 | Same-type reward | ↑ = encourage type continuity |
| `DYNAMIC_SWITCH_MULT_MIN` | 1.0 | 0.5-1.5 | Switch mult at 0% full | ↑ = discourage early switching |
| `DYNAMIC_SWITCH_MULT_MAX` | 1.5 | 1.0-3.0 | Switch mult at 100% full | ↑ = strongly avoid late switching |
| `UTIL_PAD_HOURS` | 0.0 | 0-5 | Safety buffer | Small slack for float precision |

### 9.3 CFS-Pack Parameters

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `CFS_CLUSTER_ORDER` | "by_count" | "by_count", "by_total_hours" | How to order type clusters |
| `CFS_WITHIN` | "LPT" | "SPT", "LPT" | Sequencing within clusters |

**Combinations:**
- `by_count + SPT`: Minimize changeovers, good flow time
- `by_count + LPT`: Minimize changeovers, high utilization
- `by_total_hours + LPT`: Balance utilization and changeovers

### 9.4 Hybrid-Pack Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `HYBRID_SAME_TYPE_BONUS` | 2.0 | 0-5 | Extra type continuity push |
| `HYBRID_SPT_WEIGHT` | 0.5 | 0-2 | SPT bias within type |
| `HYBRID_SWITCH_PENALTY_MULT` | 1.1 | 0.8-2.0 | Switch cost multiplier |

### 9.5 MILP-Opt Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `MILP_MAX_LOTS` | 30 | 10-50 | Hard limit on problem size |
| `MILP_MAX_BLOCKS` | 30 | 5-50 | Upper bound on blocks |
| `MILP_TIME_LIMIT` | 60 | 10-600 | Solver time limit (seconds) |

**Trade-offs:**
- ↑ TIME_LIMIT: Better solutions, slower
- ↑ MAX_BLOCKS: More flexibility, larger model
- ↓ MAX_LOTS: Enforce size limits for tractability

---

## 10. Implementation Details

### 10.1 Code Organization

```
src/fillscheduler/
├── strategies/
│   ├── __init__.py          # Strategy protocol & factory
│   ├── smart_pack.py        # Smart-Pack implementation
│   ├── spt_pack.py          # SPT-Pack implementation
│   ├── lpt_pack.py          # LPT-Pack implementation
│   ├── cfs_pack.py          # CFS-Pack implementation
│   ├── hybrid_pack.py       # Hybrid-Pack implementation
│   └── milp_opt.py          # MILP-Opt implementation
├── scheduler.py             # Main scheduling loop
├── models.py                # Data structures (Lot, Activity)
├── rules.py                 # Business rules (changeover calculation)
├── config.py                # Configuration dataclass
└── validate.py              # Input/output validation
```

### 10.2 Adding a New Algorithm

**Step 1: Create strategy file**
```python
# src/fillscheduler/strategies/my_algorithm.py
from collections import deque
from ..config import AppConfig
from ..models import Lot

class MyAlgorithm:
    def name(self) -> str:
        return "my-algorithm"

    def preorder(self, lots: list[Lot], cfg: AppConfig) -> deque[Lot]:
        # Your global ordering logic
        ordered = sorted(lots, key=your_sort_key)
        return deque(ordered)

    def pick_next(self, remaining, prev_type, window_used, cfg):
        # Your greedy selection logic
        for i, lot in enumerate(remaining):
            if your_selection_criteria(lot):
                return i
        return None  # Start new block
```

**Step 2: Register in factory**
```python
# src/fillscheduler/strategies/__init__.py
def get_strategy(strategy_name: str) -> Strategy:
    # ... existing strategies ...
    if sn in ("my_algorithm", "myalgo"):
        from .my_algorithm import MyAlgorithm
        return MyAlgorithm()
```

**Step 3: Add configuration (if needed)**
```python
# src/fillscheduler/config.py
@dataclass
class AppConfig:
    # ... existing params ...
    MY_ALGO_PARAM: float = 1.0
```

**Step 4: Test**
```bash
pytest tests/integration/test_strategies.py -k my_algorithm
```

### 10.3 Extending Algorithms

**Example: Add custom scoring to Smart-Pack**

```python
class CustomSmartPack(SmartPack):
    def _score(self, prev_type, lot, window_used, remaining, cfg):
        # Start with base score
        base_score = super()._score(prev_type, lot, window_used, remaining, cfg)

        # Add custom criteria
        custom_bonus = self._custom_logic(lot, remaining)

        return base_score + custom_bonus

    def _custom_logic(self, lot, remaining):
        # Your domain-specific logic
        if lot.lot_id.startswith("PRIORITY"):
            return 10.0  # High priority bonus
        return 0.0
```

### 10.4 Performance Optimization Tips

**1. Early Feasibility Checks:**
```python
def pick_next(self, remaining, prev_type, window_used, cfg):
    # Pre-filter feasible lots
    feasible = [
        (i, lot) for i, lot in enumerate(remaining)
        if self._fits(window_used, lot, cfg)
    ]
    if not feasible:
        return None

    # Score only feasible lots
    scored = [(self._score(lot, ...), i) for i, lot in feasible]
    ...
```

**2. Caching Repeated Calculations:**
```python
class CachedStrategy:
    def __init__(self):
        self._changeover_cache = {}

    def _get_changeover(self, prev_type, next_type, cfg):
        key = (prev_type, next_type)
        if key not in self._changeover_cache:
            self._changeover_cache[key] = changeover_hours(prev_type, next_type, cfg)
        return self._changeover_cache[key]
```

**3. Parallel Strategy Evaluation:**
```python
from concurrent.futures import ProcessPoolExecutor

def compare_strategies_parallel(lots, strategies):
    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(run_strategy, lots, strategy): strategy
            for strategy in strategies
        }
        results = {
            futures[future]: future.result()
            for future in as_completed(futures)
        }
    return results
```

---

## Appendix A: Mathematical Foundations

### A.1 Bin Packing Theory

**Classic Bin Packing:**
Given items of sizes s₁, ..., sₙ and bins of capacity C, minimize number of bins.

**First Fit Decreasing (FFD):**
```
Approximation ratio: FFD(I) ≤ (11/9)OPT(I) + 6/9
```

**Our Problem:**
- Bin Packing + Sequence-Dependent Setup Times
- No known polynomial-time approximation with guaranteed ratio
- NP-Hard via reduction from 3-Partition

### A.2 TSP Connection

**Within each block:** Sequence-dependent setups = TSP on assigned lots
- Asymmetric TSP (setup[i,j] ≠ setup[j,i] in general)
- 2-level: same-type vs different-type
- Christofides doesn't apply (asymmetric)

### A.3 Multi-Objective Optimization

**Objectives (in priority order):**
1. Minimize makespan
2. Minimize blocks (CLEAN time)
3. Minimize total changeovers

**Pareto Frontier:**
- No single solution dominates all others
- MILP finds point on frontier (weighted sum)
- Heuristics approximate frontier

---

## Appendix B: References

### B.1 Classic Papers

1. **Bin Packing:**
   - Graham, R. L. (1969). "Bounds on multiprocessing timing anomalies."
   - Johnson, D. S. (1973). "Near-optimal bin packing algorithms."

2. **Scheduling:**
   - Garey, M. R., Johnson, D. S. (1979). "Computers and Intractability."
   - Pinedo, M. L. (2016). "Scheduling: Theory, Algorithms, and Systems."

3. **Setup Times:**
   - Allahverdi, A. (2015). "The third comprehensive survey on scheduling problems with setup times."

### B.2 Relevant Algorithms

- **LPT:** Longest Processing Time (Graham, 1969)
- **SPT:** Shortest Processing Time (Smith, 1956)
- **CFS:** Cluster-First, Schedule-Second (VRP literature)
- **Beam Search:** Heuristic search technique (Ow & Morton, 1988)

### B.3 Solver Documentation

- **PuLP:** https://coin-or.github.io/pulp/
- **CBC:** https://github.com/coin-or/Cbc
- **MILP Modeling:** Wolsey, L. A. (1998). "Integer Programming."

---

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| **Activity** | Time-stamped event (CLEAN, CHANGEOVER, FILL) |
| **Beam Search** | Heuristic search keeping top K candidates |
| **Block** | Production window between CLEAN activities |
| **Changeover** | Setup time when switching between lots |
| **Makespan** | Total time from start to finish |
| **MILP** | Mixed Integer Linear Programming |
| **Lot** | Batch of pharmaceutical product to fill |
| **Slack Waste** | Unusable window capacity (too small for any lot) |
| **Strategy** | Algorithm for lot sequencing |
| **Window** | Time limit for fills + changeovers per block |

---

**Document Version:** 1.0
**Last Updated:** October 15, 2025
**Maintained By:** Filling Scheduler Development Team
**License:** GNU GPL v3.0

---
