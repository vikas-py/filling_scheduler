# Getting Started

This guide will help you get started with Filling Scheduler.

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/vikas-py/filling_scheduler.git
cd filling_scheduler

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the package (makes 'fillscheduler' command available)
pip install -e .

# Verify installation
fillscheduler --version
```

### Optional: MILP Support

For exact optimization using the MILP strategy:

```bash
pip install pulp>=2.7
```

### Development Installation

If you plan to contribute or develop:

```bash
# Install with development dependencies
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .

# Install pre-commit hooks (recommended)
pip install pre-commit
pre-commit install

# Run tests
pytest tests/ -v
```

With pre-commit hooks enabled, your code will automatically be formatted and checked before each commit.

## Your First Schedule

### 1. Prepare Your Data

Create a CSV file with your lots:

```csv
Lot ID,Type,Vials
A1,VialE,100000
A2,VialH,900000
A3,VialE,750000
```

Or use the included example:

```bash
# Example data is in: examples/lots.csv
```

### 2. Run the Scheduler

Using the modern CLI (recommended):

```bash
fillscheduler schedule --data examples/lots.csv
```

Or with a specific strategy:

```bash
fillscheduler schedule --data examples/lots.csv --strategy smart-pack
```

You'll see beautiful progress indicators:

```
⠋ Loading lots from CSV...
✓ Loaded 15 lots
⠋ Validating input lots...
✓ Input validation passed
⠋ Planning schedule using smart-pack strategy...
✓ Schedule generated in 513.16 hours
⠋ Writing outputs...

✓ Schedule completed successfully!
```

This will:
- Read your CSV file
- Generate schedule using the specified strategy
- Output to `output/` directory

### 3. View Results

Check the output directory:

- **schedule.csv** - Complete schedule with timestamps
- **summary.txt** - KPI summary
- **report.html** - Interactive visualization (open in browser)

## Configuration

You can configure Filling Scheduler in three ways:

### 1. Configuration Files (Recommended)

Create a `config.yaml` file:

```yaml
data:
  input_path: "examples/lots.csv"
  output_dir: "output"

schedule:
  strategy: "smart-pack"
  start_time: "2025-01-01 08:00"

constraints:
  window_hours: 120.0
  clean_hours: 24.0
  changeover_same_hours: 4.0
  changeover_diff_hours: 8.0
```

Then use it with the CLI:

```bash
fillscheduler --config config.yaml schedule
```

Or export a template first:

```bash
fillscheduler config export --output myconfig.yaml
# Edit myconfig.yaml with your preferred settings
fillscheduler --config myconfig.yaml schedule
```

See the [Configuration Guide](configuration.md) for complete details.

### 2. Environment Variables

```bash
export FILLSCHEDULER_STRATEGY="smart-pack"
export FILLSCHEDULER_DATA_PATH="my_data.csv"
fillscheduler schedule
```

### 3. Programmatic Configuration

```python
from fillscheduler.config import AppConfig
from pathlib import Path

cfg = AppConfig(
    DATA_PATH=Path("my_data.csv"),
    STRATEGY="smart-pack",
    START_TIME_STR="2025-01-01 08:00",
)
```

### Choosing a Strategy

Available strategies:
- `smart-pack` - **Recommended** for most cases
- `spt-pack` - Fast, good for many small lots
- `lpt-pack` - Fast, good for large lots
- `cfs-pack` - Type-clustering approach
- `hybrid-pack` - Balanced approach
- `milp-opt` - Exact optimization (small datasets only, ≤30 lots)

Example (CLI):

```bash
fillscheduler schedule --data lots.csv --strategy lpt-pack
```

Example (Programmatic):

```python
cfg = AppConfig(STRATEGY="lpt-pack")
```

## CLI Commands

### Schedule Command

```bash
# Basic usage
fillscheduler schedule --data lots.csv

# With options
fillscheduler schedule \
  --data lots.csv \
  --strategy smart-pack \
  --output results/ \
  --start-time "2025-01-15 08:00"

# Skip validation (not recommended)
fillscheduler schedule --data lots.csv --no-validation

# Skip HTML report generation
fillscheduler schedule --data lots.csv --no-report

# View all options
fillscheduler schedule --help
```

### Compare Command

```bash
# Compare specific strategies
fillscheduler compare --data lots.csv --strategies smart-pack spt-pack lpt-pack

# Compare all strategies
fillscheduler compare --data lots.csv --all-strategies

# Sort by utilization instead of makespan
fillscheduler compare --data lots.csv --all-strategies --sort-by utilization

# View all options
fillscheduler compare --help
```

### Config Commands

```bash
# Export default configuration template
fillscheduler config export --output config.yaml

# Export JSON format
fillscheduler config export --output config.json --format json

# Validate a configuration file
fillscheduler config validate --file config.yaml

# Show current configuration
fillscheduler config show

# Show configuration from file
fillscheduler config show --file config.yaml
```

### Global Options

```bash
# Enable verbose mode (detailed output)
fillscheduler --verbose schedule --data lots.csv

# Use configuration file
fillscheduler --config config.yaml schedule

# Show version
fillscheduler --version

# Show help
fillscheduler --help
```

## Next Steps

- [Learn about strategies](strategies.md) - Detailed strategy comparison
- [Tune configuration](configuration.md) - Optimize for your use case
- [View examples](examples.md) - Real-world scenarios
- [API Reference](api_reference.md) - Programmatic usage

## Common Issues

### Import Errors

If you get import errors, make sure:
1. Virtual environment is activated
2. Dependencies are installed: `pip install -r requirements.txt`
3. You're in the project root directory

### MILP Strategy Fails

If MILP strategy fails:
1. Install PuLP: `pip install pulp>=2.7`
2. Ensure dataset has ≤30 lots (MILP has a hard limit)
3. Try a heuristic strategy instead for larger datasets

### Tests Fail

If tests fail after installation:

```bash
# Ensure test dependencies are installed
pip install pytest

# Run tests
pytest tests/ -v
```

## Getting Help

- **Documentation**: Check other docs in this folder
- **GitHub Issues**: [Report bugs or ask questions](https://github.com/vikas-py/filling_scheduler/issues)
- **Examples**: See `examples/` directory for sample data
