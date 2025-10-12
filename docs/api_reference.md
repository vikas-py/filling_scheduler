# API Reference

Programmatic API documentation for Filling Scheduler.

## Core Modules

### Models (`fillscheduler.models`)

#### `Lot`
```python
@dataclass
class Lot:
    lot_id: str
    lot_type: str
    vials: int
    fill_hours: float
```

#### `Activity`
```python
@dataclass
class Activity:
    start: datetime
    end: datetime
    kind: str  # "CLEAN" | "CHANGEOVER" | "FILL"
    lot_id: Optional[str] = None
    lot_type: Optional[str] = None
    note: Optional[str] = None
```

### Scheduler (`fillscheduler.scheduler`)

#### `plan_schedule()`
```python
def plan_schedule(
    lots: List[Lot],
    start_time: datetime,
    cfg: AppConfig,
    strategy: str = "smart-pack"
) -> Tuple[List[Activity], float, dict]:
    """
    Generate a schedule for the given lots.

    Returns:
        Tuple of (activities, makespan_hours, kpis)
    """
```

### Validation (`fillscheduler.validate`)

#### `validate_input_lots()`
```python
def validate_input_lots(
    lots: List[Lot],
    cfg: AppConfig,
    *,
    fail_fast: bool = True,
    raise_exceptions: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Validate input lots against constraints.

    Returns:
        Tuple of (errors, warnings)
    """
```

#### `validate_schedule()`
```python
def validate_schedule(
    activities: List[Activity],
    cfg: AppConfig,
    *,
    fail_fast: bool = True,
    raise_exceptions: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Validate generated schedule.

    Returns:
        Tuple of (errors, warnings)
    """
```

## Strategy Protocol

### Creating Custom Strategies

```python
from fillscheduler.strategies import Strategy
from collections import deque

class MyStrategy:
    def name(self) -> str:
        return "my-strategy"

    def preorder(self, lots: List[Lot], cfg: AppConfig) -> Deque[Lot]:
        """Optional: Reorder lots before scheduling"""
        return deque(lots)

    def pick_next(
        self,
        remaining: Deque[Lot],
        prev_type: Optional[str],
        window_used: float,
        cfg: AppConfig
    ) -> Optional[int]:
        """
        Select next lot index to schedule.
        Return None to start a new block.
        """
        return 0  # Always pick first
```

## Examples

### Basic Usage

```python
from fillscheduler.config import AppConfig
from fillscheduler.io_utils import read_lots_with_pandas
from fillscheduler.scheduler import plan_schedule
from datetime import datetime

# Load configuration and data
cfg = AppConfig()
lots = read_lots_with_pandas(cfg.DATA_PATH, cfg)

# Generate schedule
activities, makespan, kpis = plan_schedule(
    lots=lots,
    start_time=datetime.now(),
    cfg=cfg,
    strategy="smart-pack"
)

# Print KPIs
for key, value in kpis.items():
    print(f"{key}: {value}")
```

### With Validation

```python
from fillscheduler.validate import validate_input_lots, validate_schedule

# Validate inputs
errors, warnings = validate_input_lots(lots, cfg)
if errors:
    print("Validation failed!")
    for err in errors:
        print(f"  - {err}")
else:
    # Generate schedule
    activities, _, kpis = plan_schedule(lots, start_time, cfg)

    # Validate output
    errors, warnings = validate_schedule(activities, cfg)
    if not errors:
        print("Schedule is valid!")
```

## Full Documentation

For complete API documentation, see the source code docstrings or generate documentation with Sphinx:

```bash
cd docs
make html
```

(Coming soon: Auto-generated API documentation)
