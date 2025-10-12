# Filling Scheduler# Filling Scheduler



[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/vikas-py/filling_scheduler)Generates a filling line schedule under strict constraints:

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)- Clean before use (24h)

[![License](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)- Clean window <= 120h (fills + changeovers)

- Changeover: 4h (same type), 8h (different type)

A production-grade pharmaceutical filling line scheduler that optimizes lot sequencing under strict operational constraints. The system implements multiple scheduling strategies ranging from fast heuristics to exact optimization.- Fill rate: 332 vials/min (19,920 vials/h)

- No lot splitting

## ✨ Features- Strict validation: impossible inputs fail early



- **Multiple Optimization Strategies**## Run

  - `smart-pack` - Advanced heuristic with look-ahead and slack optimization (recommended)

  - `spt-pack` - Shortest Processing Time first```bash

  - `lpt-pack` - Longest Processing Time firstpython -m venv .venv

  - `cfs-pack` - Cluster-First, Schedule-Second approachsource .venv/bin/activate    # Windows: .venv\Scripts\activate

  - `hybrid-pack` - Combined heuristic strategypip install -r requirements.txt

  - `milp-opt` - Exact Mixed Integer Linear Programming optimizationpython main.py

- **Strict Constraint Validation**
  - Clean before use (24h requirement)
  - Clean window limits (≤ 120h for fills + changeovers)
  - Changeover times (4h same type, 8h different type)
  - Fill rate enforcement (332 vials/min = 19,920 vials/h)
  - No lot splitting allowed
  - Preflight and postflight validation

- **Rich Reporting**
  - CSV schedule exports
  - Interactive HTML reports with color-coded activities
  - KPI tracking (makespan, utilization, changeover analysis)
  - Multi-strategy comparison tools

## 🚀 Quick Start

### Installation

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

# Optional: Install MILP optimization support
pip install pulp>=2.7

# Optional: Install development dependencies
pip install -r requirements-dev.txt
```

### Basic Usage

```bash
# Run with default settings (smart-pack strategy, example data)
python main.py

# Outputs will be in: ./output/
#   - schedule.csv      (detailed schedule)
#   - summary.txt       (KPI summary)
#   - report.html       (interactive visualization)
```

### Compare Strategies

```bash
# Compare multiple strategies on the same dataset
python compare_runs.py --data examples/lots.csv --strategies smart-pack spt-pack lpt-pack

# Outputs:
#   - output/comparison_kpis.csv
#   - output/comparison_report.html
```

## 📋 Operational Constraints

The scheduler operates under these pharmaceutical manufacturing constraints:

| Constraint | Value | Description |
|------------|-------|-------------|
| **Clean Time** | 24 hours | Required cleaning before each production block |
| **Clean Window** | ≤ 120 hours | Maximum time for fills + changeovers per block |
| **Changeover (Same Type)** | 4 hours | Setup time when switching between same vial types |
| **Changeover (Different Type)** | 8 hours | Setup time when switching between different vial types |
| **Fill Rate** | 19,920 vials/hour | 332 vials/minute production rate |
| **Lot Splitting** | Not allowed | Each lot must be completed in a single block |

## 🎯 Strategy Comparison

| Strategy | Speed | Quality | Best For |
|----------|-------|---------|----------|
| `smart-pack` | Fast | Excellent | **Recommended for most cases** |
| `spt-pack` | Very Fast | Good | Quick schedules, many small lots |
| `lpt-pack` | Very Fast | Good | Datasets with large lots |
| `cfs-pack` | Fast | Good | Type-heavy datasets |
| `hybrid-pack` | Fast | Good | Balanced datasets |
| `milp-opt` | Slow | Optimal | Small datasets (≤30 lots), benchmarking |

**Performance Guide:**
- 15 lots: All strategies < 1 second
- 100 lots: Heuristics < 1s, MILP not recommended
- 500+ lots: Use heuristics only (smart-pack, spt-pack, lpt-pack)

## ⚙️ Configuration

Edit `fillscheduler/config.py` to customize:

```python
from fillscheduler.config import AppConfig

cfg = AppConfig(
    DATA_PATH=Path("examples/lots.csv"),
    OUTPUT_DIR=Path("output"),
    START_TIME_STR="2025-01-01 08:00",
    STRATEGY="smart-pack",           # Choose your strategy
    
    # Process constants
    FILL_RATE_VPH=19920.0,           # Vials per hour
    CLEAN_HOURS=24.0,
    WINDOW_HOURS=120.0,
    CHG_SAME_HOURS=4.0,
    CHG_DIFF_HOURS=8.0,
    
    # Strategy tuning (smart-pack)
    BEAM_WIDTH=3,                     # Look-ahead depth
    SLACK_WASTE_WEIGHT=3.0,          # Penalty for wasted capacity
    STREAK_BONUS=1.0,                # Bonus for type consistency
)
```

## 📊 Input Data Format

Create a CSV file with the following columns:

```csv
Lot ID,Type,Vials
A1,VialE,100000
A2,VialH,900000
A3,VialE,750000
```

- **Lot ID**: Unique identifier for each lot
- **Type**: Vial type (e.g., VialE, VialH, VialF)
- **Vials**: Number of vials to fill (positive integer)

See `examples/lots.csv` for a complete example.

### Generate Test Data

```bash
cd examples
python gen_lots.py  # Generates lots_large.csv with 500 lots
```

## 📈 Example Output

### Schedule CSV
```csv
Start,End,Hours,Activity,Lot ID,Type,Note
2025-01-01 08:00,2025-01-02 08:00,24.0,CLEAN,,,Block reset
2025-01-02 08:00,2025-01-02 13:01,5.02,FILL,A1,VialE,100000 vials
2025-01-02 13:01,2025-01-02 17:01,4.0,CHANGEOVER,,VialE->VialE,4h
2025-01-02 17:01,2025-01-03 07:48,14.78,FILL,A3,VialE,750000 vials
```

### KPI Summary
```
Makespan (h): 156.32
Total Clean (h): 48.00
Total Changeover (h): 28.00
Total Fill (h): 80.32
Lots Scheduled: 15
Clean Blocks: 2
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fillscheduler --cov-report=html

# Run specific test file
pytest tests/test_input_validation.py -v
```

**Current Test Coverage:** 11 tests passing ✅

## 🏗️ Project Structure

```
filling_scheduler/
├── fillscheduler/           # Main package
│   ├── models.py           # Data models (Lot, Activity)
│   ├── config.py           # Configuration
│   ├── scheduler.py        # Scheduling engine
│   ├── validate.py         # Validation logic
│   ├── rules.py            # Business rules
│   ├── io_utils.py         # CSV I/O
│   ├── reporting.py        # Report generation
│   ├── compare.py          # Strategy comparison
│   └── strategies/         # Optimization strategies
├── tests/                  # Test suite
├── examples/               # Example datasets
├── main.py                 # CLI entry point
├── compare_runs.py         # Strategy comparison tool
├── pyproject.toml          # Modern Python packaging
├── requirements.txt        # Production dependencies
└── requirements-dev.txt    # Development dependencies
```

## 🤝 Contributing

Contributions are welcome! This project follows modern Python best practices:

- **Code Style**: Black formatting (100 char line length)
- **Type Hints**: Comprehensive type annotations
- **Testing**: pytest with good coverage
- **Documentation**: Docstrings for all public APIs

See `Restructuring_TODO.md` for planned improvements.

## 📝 License

This project is licensed under the GNU General Public License v3.0 or later - see the [LICENSE](LICENSE) file for details.

## 🔍 Algorithm Details

### Smart-Pack Strategy (Recommended)

The `smart-pack` strategy uses:
1. **Greedy scoring** with multiple factors:
   - Changeover penalties (type-dependent)
   - Slack waste prediction (lookahead)
   - Type streak bonuses
   - Dynamic penalties based on window utilization

2. **Beam search** with configurable width for limited lookahead

3. **Adaptive selection** that considers downstream effects

**Key Advantages:**
- Minimizes changeovers while maximizing window utilization
- Avoids creating unusable slack in windows
- Balances competing objectives effectively

### MILP Optimization (Exact Solution)

For small instances (≤30 lots), the MILP strategy provides provably optimal schedules:
- Formulated as a traveling salesman variant with block constraints
- Uses PuLP with CBC/GLPK solvers
- Minimizes total changeover time + clean blocks
- Enforces all operational constraints exactly

## 📚 Further Reading

- **Strategy Tuning**: See `fillscheduler/config.py` for all tunable parameters
- **Validation Logic**: See `fillscheduler/validate.py` for constraint checks
- **Adding Strategies**: Implement the `Strategy` protocol in `fillscheduler/strategies/__init__.py`

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/vikas-py/filling_scheduler/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vikas-py/filling_scheduler/discussions)

---

**Made with ❤️ for pharmaceutical manufacturing optimization**
