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
```

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

```bash
python main.py
```

This will:
- Read `examples/lots.csv` (default)
- Generate schedule using `smart-pack` strategy (default)
- Output to `output/` directory

### 3. View Results

Check the output directory:

- **schedule.csv** - Complete schedule with timestamps
- **summary.txt** - KPI summary
- **report.html** - Interactive visualization (open in browser)

## Configuration

### Basic Configuration

Edit `src/fillscheduler/config.py`:

```python
from fillscheduler.config import AppConfig

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

Example:

```python
cfg = AppConfig(STRATEGY="lpt-pack")
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
