# Configuration Guide# Configuration Guide



The Filling Scheduler supports flexible configuration through multiple methods:Detailed configuration options for Filling Scheduler.

- YAML configuration files (recommended)

- JSON configuration files## Configuration File

- Environment variables

- Command-line arguments (when using CLI)Edit `src/fillscheduler/config.py` or create your own configuration:



## Quick Start```python

from fillscheduler.config import AppConfig

### 1. Create a Configuration Filefrom pathlib import Path



The easiest way to get started is to export the default configuration:cfg = AppConfig(

    # File paths

```bash    DATA_PATH=Path("examples/lots.csv"),

# Export as YAML (recommended)    OUTPUT_DIR=Path("output"),

python -c "from fillscheduler.config_loader import export_default_config; export_default_config('yaml')"    START_TIME_STR="2025-01-01 08:00",



# Export as JSON    # Strategy selection

python -c "from fillscheduler.config_loader import export_default_config; export_default_config('json')"    STRATEGY="smart-pack",

```

    # Process constants

This creates a `.fillscheduler.yaml` (or `.json`) file in your current directory with all available options and documentation.    FILL_RATE_VPH=19920.0,

    CLEAN_HOURS=24.0,

### 2. Edit the Configuration    WINDOW_HOURS=120.0,

    CHG_SAME_HOURS=4.0,

Open the generated file and modify the values:    CHG_DIFF_HOURS=8.0,



```yaml    # Reporting

# .fillscheduler.yaml    HTML_REPORT=True,

strategy: "milp"  # Change from smart-pack to milp    HTML_FILENAME="report.html",

fill_rate_vph: 20000.0  # Increase fill rate)

strategies:```

  milp:

    time_limit: 120  # Increase solver time limit## All Configuration Options

```

See [strategies.md](strategies.md) for strategy-specific tuning parameters.

### 3. Use the Configuration

## Environment Variables

The configuration file is automatically discovered when you run the scheduler:

(Coming soon: Support for environment variable configuration)

```python

from fillscheduler.config_loader import load_config_with_overrides## YAML Configuration



# Loads from .fillscheduler.yaml automatically(Coming soon: Support for YAML configuration files)

config = load_config_with_overrides()
```

## Configuration File Locations

Configuration files are searched in the following order (first found wins):

1. **Specified path** - Via `--config` CLI option or `config_path` parameter
2. **Current directory** - `.fillscheduler.yaml` or `.fillscheduler.yml`
3. **User config directory** - `~/.config/fillscheduler/config.yaml`
4. **Default values** - If no config file found

### Recommended Setup

For **project-specific** configuration:
```bash
# In your project directory
.fillscheduler.yaml
```

For **user-wide** configuration:
```bash
# Linux/macOS
~/.config/fillscheduler/config.yaml

# Windows
%USERPROFILE%\.config\fillscheduler\config.yaml
```

## Configuration Options

### File & Run Options

```yaml
data_path: "examples/lots.csv"    # Input CSV file path
output_dir: "output"               # Output directory
start_time_str: "2025-01-01 08:00"  # Start time (YYYY-MM-DD HH:MM)
strategy: "smart-pack"             # Scheduling strategy
interactive: false                 # Enable interactive mode
```

**Available Strategies:**
- `smart-pack` - Intelligent heuristic with look-ahead (recommended)
- `spt-pack` - Shortest Processing Time first
- `lpt-pack` - Longest Processing Time first
- `cfs-pack` - Cluster First Schedule
- `hybrid-pack` - Hybrid heuristic approach
- `milp` - Mixed Integer Linear Programming (optimal but slow)

### Process Constants

```yaml
fill_rate_vph: 19920.0   # Fill rate (vials/hour)
clean_hours: 24.0        # Cleaning duration (hours)
window_hours: 120.0      # Time window (hours)
chg_same_hours: 4.0      # Same-type changeover (hours)
chg_diff_hours: 8.0      # Different-type changeover (hours)
```

### Strategy-Specific Settings

#### Smart-Pack Strategy (Recommended)

```yaml
strategies:
  smart_pack:
    beam_width: 3              # Look-ahead width (1-10)
    score_alpha: 8.0           # Different-type changeover penalty
    score_beta: 4.0            # Same-type changeover penalty
    slack_waste_weight: 3.0    # Slack waste penalty
    streak_bonus: 1.0          # Same-type streak bonus
```

**Tuning Tips:**
- **Higher `beam_width`** (e.g., 5-7): Better quality, slower computation
- **Lower `beam_width`** (e.g., 1-2): Faster, may miss opportunities
- **Higher `score_alpha`**: Discourages type switching more strongly
- **Higher `slack_waste_weight`**: Packs window more tightly

#### CFS Strategy

```yaml
strategies:
  cfs:
    cluster_order: "by_count"  # or "by_total_hours"
    within: "LPT"              # or "SPT"
```

#### Hybrid Strategy

```yaml
strategies:
  hybrid:
    same_type_bonus: 2.0        # Type streak bonus
    spt_weight: 0.5             # SPT bias for same type
    switch_penalty_mult: 1.1    # Switch penalty multiplier
```

#### MILP Strategy

```yaml
strategies:
  milp:
    max_lots: 30       # Maximum lots (tractability limit)
    max_blocks: 30     # Maximum cleaning blocks
    time_limit: 60     # Solver time limit (seconds)
```

**MILP Notes:**
- Provides optimal solutions but much slower
- Increase `time_limit` for better solutions (may still timeout)
- Reduce `max_lots` if model becomes intractable

### Reporting Options

```yaml
html_report: true              # Generate HTML report
html_filename: "report.html"   # Report filename
datetime_fmt: "%Y-%m-%d %H:%M" # Datetime format
```

## Environment Variables

Override any configuration value using environment variables with the `FILLSCHEDULER_` prefix:

```bash
# Simple values
export FILLSCHEDULER_STRATEGY=milp
export FILLSCHEDULER_FILL_RATE_VPH=20000

# Nested values (use double underscores)
export FILLSCHEDULER_STRATEGIES__MILP__TIME_LIMIT=120
export FILLSCHEDULER_STRATEGIES__SMART_PACK__BEAM_WIDTH=5

# Boolean values (use JSON format)
export FILLSCHEDULER_INTERACTIVE=true
export FILLSCHEDULER_HTML_REPORT=false
```

### Docker/Container Usage

Environment variables are particularly useful in containerized environments:

```dockerfile
# Dockerfile
ENV FILLSCHEDULER_STRATEGY=milp
ENV FILLSCHEDULER_STRATEGIES__MILP__TIME_LIMIT=180
```

```bash
# docker-compose.yml
environment:
  - FILLSCHEDULER_STRATEGY=milp
  - FILLSCHEDULER_DATA_PATH=/data/lots.csv
```

## Programmatic Usage

### Basic Loading

```python
from fillscheduler.config_loader import load_config_with_overrides

# Load from default location
config = load_config_with_overrides()

# Load from specific file
from pathlib import Path
config = load_config_with_overrides(
    config_path=Path("my_config.yaml")
)
```

### With Overrides

```python
# Override specific values
config = load_config_with_overrides(
    config_path=Path("base_config.yaml"),
    overrides={
        "strategy": "milp",
        "strategies.milp.time_limit": 180
    }
)
```

### Export Configuration

```python
from fillscheduler.config_loader import export_default_config
from pathlib import Path

# Export to specific location
export_default_config("yaml", Path("my_config.yaml"))
export_default_config("json", Path("my_config.json"))
```

### Validation

Configuration is automatically validated using Pydantic:

```python
from fillscheduler.config_loader import ConfigFile

try:
    config = ConfigFile(strategy="invalid-strategy")
except ValueError as e:
    print(f"Invalid configuration: {e}")
    # Output: strategy must be one of [...], got 'invalid-strategy'
```

## Configuration Examples

### Example 1: Quick Heuristic Run

```yaml
# fast-config.yaml
strategy: "spt-pack"
data_path: "data/lots.csv"
output_dir: "results"
html_report: false  # Skip HTML for speed
```

### Example 2: High-Quality MILP

```yaml
# optimal-config.yaml
strategy: "milp"
data_path: "data/lots.csv"
strategies:
  milp:
    max_lots: 50      # Increase capacity
    time_limit: 300   # 5 minute limit
    max_blocks: 40
```

### Example 3: Tuned Smart-Pack

```yaml
# tuned-config.yaml
strategy: "smart-pack"
strategies:
  smart_pack:
    beam_width: 5           # Better look-ahead
    score_alpha: 10.0       # Discourage type switches
    slack_waste_weight: 5.0  # Pack tighter
    streak_bonus: 2.0       # Favor type streaks
```

## Troubleshooting

### Configuration Not Found

**Problem:** "No configuration file found, using defaults"

**Solution:**
1. Check file exists: `ls .fillscheduler.yaml`
2. Check filename spelling (`.fillscheduler.yaml` not `.fillscheduler.yml`)
3. Check current directory: `pwd`
4. Try absolute path in code

### Invalid Strategy

**Problem:** `ValueError: strategy must be one of [...], got 'my-strategy'`

**Solution:**
Use one of the valid strategies:
- `smart-pack`, `spt-pack`, `lpt-pack`, `cfs-pack`, `hybrid-pack`, `milp`

### Invalid Date Format

**Problem:** `ValueError: start_time_str must be in format 'YYYY-MM-DD HH:MM'`

**Solution:**
Use exactly this format: `2025-01-01 08:00` (not `01/01/2025` or `2025-01-01T08:00:00`)

### YAML Syntax Error

**Problem:** `yaml.YAMLError: ...`

**Solution:**
1. Check indentation (use spaces, not tabs)
2. Check colon spacing: `key: value` (not `key:value`)
3. Validate YAML: https://www.yamllint.com/

## Migration from Old Config

If you're upgrading from the old `AppConfig` class:

**Old code:**
```python
from fillscheduler.config import AppConfig

cfg = AppConfig()
cfg.STRATEGY = "milp"
cfg.MILP_TIME_LIMIT = 120
```

**New code (Option 1 - Use config file):**
```yaml
# .fillscheduler.yaml
strategy: "milp"
strategies:
  milp:
    time_limit: 120
```

```python
from fillscheduler.config_loader import load_config_with_overrides

cfg = load_config_with_overrides()  # Automatically loads .fillscheduler.yaml
```

**New code (Option 2 - Programmatic):**
```python
from fillscheduler.config_loader import load_config_with_overrides

cfg = load_config_with_overrides(overrides={
    "strategy": "milp",
    "strategies.milp.time_limit": 120
})
```

## Schema Reference

For the complete configuration schema, see:
- `src/fillscheduler/config_loader.py` - Full Pydantic models
- `config.example.yaml` - Annotated example
- `config.example.json` - JSON format example

## Related Documentation

- [Getting Started Guide](getting_started.md) - Initial setup
- [Strategies Guide](strategies.md) - Strategy comparison and selection
- [API Reference](api_reference.md) - Programmatic API
