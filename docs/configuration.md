# Configuration Guide

Detailed configuration options for Filling Scheduler.

## Configuration File

Edit `src/fillscheduler/config.py` or create your own configuration:

```python
from fillscheduler.config import AppConfig
from pathlib import Path

cfg = AppConfig(
    # File paths
    DATA_PATH=Path("examples/lots.csv"),
    OUTPUT_DIR=Path("output"),
    START_TIME_STR="2025-01-01 08:00",
    
    # Strategy selection
    STRATEGY="smart-pack",
    
    # Process constants
    FILL_RATE_VPH=19920.0,
    CLEAN_HOURS=24.0,
    WINDOW_HOURS=120.0,
    CHG_SAME_HOURS=4.0,
    CHG_DIFF_HOURS=8.0,
    
    # Reporting
    HTML_REPORT=True,
    HTML_FILENAME="report.html",
)
```

## All Configuration Options

See [strategies.md](strategies.md) for strategy-specific tuning parameters.

## Environment Variables

(Coming soon: Support for environment variable configuration)

## YAML Configuration

(Coming soon: Support for YAML configuration files)
