# Filling Scheduler# Filling Scheduler# Filling Scheduler



[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/vikas-py/filling_scheduler)

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

[![License](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/vikas-py/filling_scheduler)

Generates a filling line schedule under strict constraints:

A production-grade pharmaceutical filling line scheduler that optimizes lot sequencing under strict operational constraints. The system implements multiple scheduling strategies ranging from fast heuristics to exact optimization.[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)- Clean before use (24h)



## ✨ Features[![License](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)- Clean window <= 120h (fills + changeovers)



- **Multiple Optimization Strategies**- Changeover: 4h (same type), 8h (different type)

  - `smart-pack` - Advanced heuristic with look-ahead and slack optimization (recommended)

  - `spt-pack` - Shortest Processing Time firstA production-grade pharmaceutical filling line scheduler that optimizes lot sequencing under strict operational constraints. The system implements multiple scheduling strategies ranging from fast heuristics to exact optimization.- Fill rate: 332 vials/min (19,920 vials/h)

  - `lpt-pack` - Longest Processing Time first

  - `cfs-pack` - Cluster-First, Schedule-Second approach- No lot splitting

  - `hybrid-pack` - Combined heuristic strategy

  - `milp-opt` - Exact Mixed Integer Linear Programming optimization## ✨ Features- Strict validation: impossible inputs fail early



- **Strict Constraint Validation**

  - Clean before use (24h requirement)

  - Clean window limits (≤ 120h for fills + changeovers)- **Multiple Optimization Strategies**## Run

  - Changeover times (4h same type, 8h different type)

  - Fill rate enforcement (332 vials/min = 19,920 vials/h)  - `smart-pack` - Advanced heuristic with look-ahead and slack optimization (recommended)

  - No lot splitting allowed

  - Preflight and postflight validation  - `spt-pack` - Shortest Processing Time first```bash



- **Rich Reporting**  - `lpt-pack` - Longest Processing Time firstpython -m venv .venv

  - CSV schedule exports

  - Interactive HTML reports with color-coded activities  - `cfs-pack` - Cluster-First, Schedule-Second approachsource .venv/bin/activate    # Windows: .venv\Scripts\activate

  - KPI tracking (makespan, utilization, changeover analysis)

  - Multi-strategy comparison tools  - `hybrid-pack` - Combined heuristic strategypip install -r requirements.txt



## 🚀 Quick Start  - `milp-opt` - Exact Mixed Integer Linear Programming optimizationpython main.py



### Installation- **Strict Constraint Validation**

  - Clean before use (24h requirement)

```bash  - Clean window limits (≤ 120h for fills + changeovers)

# Clone the repository  - Changeover times (4h same type, 8h different type)

git clone https://github.com/vikas-py/filling_scheduler.git  - Fill rate enforcement (332 vials/min = 19,920 vials/h)

cd filling_scheduler  - No lot splitting allowed

  - Preflight and postflight validation

# Create virtual environment

python -m venv .venv- **Rich Reporting**

  - CSV schedule exports

# Activate virtual environment  - Interactive HTML reports with color-coded activities

# On Windows:  - KPI tracking (makespan, utilization, changeover analysis)

.venv\Scripts\activate  - Multi-strategy comparison tools

# On macOS/Linux:

source .venv/bin/activate## 🚀 Quick Start



# Install dependencies### Installation

pip install -r requirements.txt

```bash

# Optional: Install MILP optimization support# Clone the repository

pip install pulp>=2.7git clone https://github.com/vikas-py/filling_scheduler.git

cd filling_scheduler

# Optional: Install development dependencies

pip install -r requirements-dev.txt# Create virtual environment

```python -m venv .venv



### Basic Usage# Activate virtual environment

# On Windows:

```bash.venv\Scripts\activate

# Run with default settings (smart-pack strategy, example data)# On macOS/Linux:

python main.pysource .venv/bin/activate



# Outputs will be in: ./output/# Install dependencies

#   - schedule.csv      (detailed schedule)pip install -r requirements.txt

#   - summary.txt       (KPI summary)

#   - report.html       (interactive visualization)# Optional: Install MILP optimization support

```pip install pulp>=2.7



### Compare Strategies# Optional: Install development dependencies

pip install -r requirements-dev.txt

```bash```

# Compare multiple strategies on the same dataset

python compare_runs.py --data examples/lots.csv --strategies smart-pack spt-pack lpt-pack### Basic Usage



# Outputs:```bash

#   - output/comparison_kpis.csv# Run with default settings (smart-pack strategy, example data)

#   - output/comparison_report.htmlpython main.py

```

# Outputs will be in: ./output/

## 📋 Operational Constraints#   - schedule.csv      (detailed schedule)

#   - summary.txt       (KPI summary)

The scheduler operates under these pharmaceutical manufacturing constraints:#   - report.html       (interactive visualization)

```

| Constraint | Value | Description |

|------------|-------|-------------|### Compare Strategies

| **Clean Time** | 24 hours | Required cleaning before each production block |

| **Clean Window** | ≤ 120 hours | Maximum time for fills + changeovers per block |```bash

| **Changeover (Same Type)** | 4 hours | Setup time when switching between same vial types |# Compare multiple strategies on the same dataset

| **Changeover (Different Type)** | 8 hours | Setup time when switching between different vial types |python compare_runs.py --data examples/lots.csv --strategies smart-pack spt-pack lpt-pack

| **Fill Rate** | 19,920 vials/hour | 332 vials/minute production rate |

| **Lot Splitting** | Not allowed | Each lot must be completed in a single block |# Outputs:

#   - output/comparison_kpis.csv

## 🎯 Strategy Comparison#   - output/comparison_report.html

```

| Strategy | Speed | Quality | Best For |

|----------|-------|---------|----------|## 📋 Operational Constraints

| `smart-pack` | Fast | Excellent | **Recommended for most cases** |

| `spt-pack` | Very Fast | Good | Quick schedules, many small lots |The scheduler operates under these pharmaceutical manufacturing constraints:

| `lpt-pack` | Very Fast | Good | Datasets with large lots |

| `cfs-pack` | Fast | Good | Type-heavy datasets || Constraint | Value | Description |

| `hybrid-pack` | Fast | Good | Balanced datasets ||------------|-------|-------------|

| `milp-opt` | Slow | Optimal | Small datasets (≤30 lots), benchmarking || **Clean Time** | 24 hours | Required cleaning before each production block |

| **Clean Window** | ≤ 120 hours | Maximum time for fills + changeovers per block |

**Performance Guide:**| **Changeover (Same Type)** | 4 hours | Setup time when switching between same vial types |

- 15 lots: All strategies < 1 second| **Changeover (Different Type)** | 8 hours | Setup time when switching between different vial types |

- 100 lots: Heuristics < 1s, MILP not recommended| **Fill Rate** | 19,920 vials/hour | 332 vials/minute production rate |

- 500+ lots: Use heuristics only (smart-pack, spt-pack, lpt-pack)| **Lot Splitting** | Not allowed | Each lot must be completed in a single block |



## ⚙️ Configuration## 🎯 Strategy Comparison



Edit `src/fillscheduler/config.py` to customize:| Strategy | Speed | Quality | Best For |

|----------|-------|---------|----------|

```python| `smart-pack` | Fast | Excellent | **Recommended for most cases** |

from fillscheduler.config import AppConfig| `spt-pack` | Very Fast | Good | Quick schedules, many small lots |

from pathlib import Path| `lpt-pack` | Very Fast | Good | Datasets with large lots |

| `cfs-pack` | Fast | Good | Type-heavy datasets |

cfg = AppConfig(| `hybrid-pack` | Fast | Good | Balanced datasets |

    DATA_PATH=Path("examples/lots.csv"),| `milp-opt` | Slow | Optimal | Small datasets (≤30 lots), benchmarking |

    OUTPUT_DIR=Path("output"),

    START_TIME_STR="2025-01-01 08:00",**Performance Guide:**

    STRATEGY="smart-pack",           # Choose your strategy- 15 lots: All strategies < 1 second

    - 100 lots: Heuristics < 1s, MILP not recommended

    # Process constants- 500+ lots: Use heuristics only (smart-pack, spt-pack, lpt-pack)

    FILL_RATE_VPH=19920.0,           # Vials per hour

    CLEAN_HOURS=24.0,## ⚙️ Configuration

    WINDOW_HOURS=120.0,

    CHG_SAME_HOURS=4.0,Edit `fillscheduler/config.py` to customize:

    CHG_DIFF_HOURS=8.0,

    ```python

    # Strategy tuning (smart-pack)from fillscheduler.config import AppConfig

    BEAM_WIDTH=3,                     # Look-ahead depth

    SLACK_WASTE_WEIGHT=3.0,          # Penalty for wasted capacitycfg = AppConfig(

    STREAK_BONUS=1.0,                # Bonus for type consistency    DATA_PATH=Path("examples/lots.csv"),

)    OUTPUT_DIR=Path("output"),

```    START_TIME_STR="2025-01-01 08:00",

    STRATEGY="smart-pack",           # Choose your strategy

## 📊 Input Data Format    

    # Process constants

Create a CSV file with the following columns:    FILL_RATE_VPH=19920.0,           # Vials per hour

    CLEAN_HOURS=24.0,

```csv    WINDOW_HOURS=120.0,

Lot ID,Type,Vials    CHG_SAME_HOURS=4.0,

A1,VialE,100000    CHG_DIFF_HOURS=8.0,

A2,VialH,900000    

A3,VialE,750000    # Strategy tuning (smart-pack)

```    BEAM_WIDTH=3,                     # Look-ahead depth

    SLACK_WASTE_WEIGHT=3.0,          # Penalty for wasted capacity

- **Lot ID**: Unique identifier for each lot    STREAK_BONUS=1.0,                # Bonus for type consistency

- **Type**: Vial type (e.g., VialE, VialH, VialF))

- **Vials**: Number of vials to fill (positive integer)```



See `examples/lots.csv` for a complete example.## 📊 Input Data Format



### Generate Test DataCreate a CSV file with the following columns:



```bash```csv

cd examplesLot ID,Type,Vials

python gen_lots.py  # Generates lots_large.csv with 500 lotsA1,VialE,100000

```A2,VialH,900000

A3,VialE,750000

## 📈 Example Output```



### Schedule CSV- **Lot ID**: Unique identifier for each lot

```csv- **Type**: Vial type (e.g., VialE, VialH, VialF)

Start,End,Hours,Activity,Lot ID,Type,Note- **Vials**: Number of vials to fill (positive integer)

2025-01-01 08:00,2025-01-02 08:00,24.0,CLEAN,,,Block reset

2025-01-02 08:00,2025-01-02 13:01,5.02,FILL,A1,VialE,100000 vialsSee `examples/lots.csv` for a complete example.

2025-01-02 13:01,2025-01-02 17:01,4.0,CHANGEOVER,,VialE->VialE,4h

2025-01-02 17:01,2025-01-03 07:48,14.78,FILL,A3,VialE,750000 vials### Generate Test Data

```

```bash

### KPI Summarycd examples

```python gen_lots.py  # Generates lots_large.csv with 500 lots

Makespan (h): 156.32```

Total Clean (h): 48.00

Total Changeover (h): 28.00## 📈 Example Output

Total Fill (h): 80.32

Lots Scheduled: 15### Schedule CSV

Clean Blocks: 2```csv

```Start,End,Hours,Activity,Lot ID,Type,Note

2025-01-01 08:00,2025-01-02 08:00,24.0,CLEAN,,,Block reset

## 🧪 Testing2025-01-02 08:00,2025-01-02 13:01,5.02,FILL,A1,VialE,100000 vials

2025-01-02 13:01,2025-01-02 17:01,4.0,CHANGEOVER,,VialE->VialE,4h

```bash2025-01-02 17:01,2025-01-03 07:48,14.78,FILL,A3,VialE,750000 vials

# Run all tests```

pytest

### KPI Summary

# Run with coverage```

pytest --cov=fillscheduler --cov-report=htmlMakespan (h): 156.32

Total Clean (h): 48.00

# Run specific test fileTotal Changeover (h): 28.00

pytest tests/test_input_validation.py -vTotal Fill (h): 80.32

```Lots Scheduled: 15

Clean Blocks: 2

**Current Test Coverage:** 11 tests passing ✅```



## 🏗️ Project Structure## 🧪 Testing



``````bash

filling_scheduler/# Run all tests

├── src/pytest

│   └── fillscheduler/       # Main package

│       ├── cli/            # CLI commands# Run with coverage

│       ├── strategies/     # Optimization strategiespytest --cov=fillscheduler --cov-report=html

│       ├── models.py       # Data models (Lot, Activity)

│       ├── config.py       # Configuration# Run specific test file

│       ├── scheduler.py    # Scheduling enginepytest tests/test_input_validation.py -v

│       ├── validate.py     # Validation logic```

│       ├── rules.py        # Business rules

│       ├── io_utils.py     # CSV I/O**Current Test Coverage:** 11 tests passing ✅

│       ├── reporting.py    # Report generation

│       └── compare.py      # Strategy comparison## 🏗️ Project Structure

├── docs/                   # Documentation

│   ├── getting_started.md```

│   ├── strategies.mdfilling_scheduler/

│   ├── configuration.md├── fillscheduler/           # Main package

│   ├── api_reference.md│   ├── models.py           # Data models (Lot, Activity)

│   └── examples.md│   ├── config.py           # Configuration

├── tests/                  # Test suite│   ├── scheduler.py        # Scheduling engine

├── examples/               # Example datasets│   ├── validate.py         # Validation logic

├── scripts/                # Utility scripts│   ├── rules.py            # Business rules

├── main.py                 # CLI entry point│   ├── io_utils.py         # CSV I/O

├── compare_runs.py         # Strategy comparison tool│   ├── reporting.py        # Report generation

├── pyproject.toml          # Modern Python packaging│   ├── compare.py          # Strategy comparison

├── requirements.txt        # Production dependencies│   └── strategies/         # Optimization strategies

└── requirements-dev.txt    # Development dependencies├── tests/                  # Test suite

```├── examples/               # Example datasets

├── main.py                 # CLI entry point

## 📚 Documentation├── compare_runs.py         # Strategy comparison tool

├── pyproject.toml          # Modern Python packaging

Comprehensive documentation is available in the `docs/` directory:├── requirements.txt        # Production dependencies

└── requirements-dev.txt    # Development dependencies

- **[Getting Started](docs/getting_started.md)** - Installation, first schedule, troubleshooting```

- **[Strategies Guide](docs/strategies.md)** - Detailed strategy comparison, tuning, decision tree

- **[Configuration](docs/configuration.md)** - All configuration options explained## 🤝 Contributing

- **[API Reference](docs/api_reference.md)** - Programmatic usage and examples

- **[Examples](docs/examples.md)** - Real-world scenarios and integration guidesContributions are welcome! This project follows modern Python best practices:



## 🤝 Contributing- **Code Style**: Black formatting (100 char line length)

- **Type Hints**: Comprehensive type annotations

Contributions are welcome! This project follows modern Python best practices:- **Testing**: pytest with good coverage

- **Documentation**: Docstrings for all public APIs

- **Code Style**: Black formatting (100 char line length)

- **Type Hints**: Comprehensive type annotationsSee `Restructuring_TODO.md` for planned improvements.

- **Testing**: pytest with good coverage

- **Documentation**: Docstrings for all public APIs## 📝 License



See `Restructuring_TODO.md` for planned improvements.This project is licensed under the GNU General Public License v3.0 or later - see the [LICENSE](LICENSE) file for details.



### Development Setup## 🔍 Algorithm Details



```bash### Smart-Pack Strategy (Recommended)

# Install development dependencies

pip install -r requirements-dev.txtThe `smart-pack` strategy uses:

1. **Greedy scoring** with multiple factors:

# Install pre-commit hooks (coming soon)   - Changeover penalties (type-dependent)

# pre-commit install   - Slack waste prediction (lookahead)

   - Type streak bonuses

# Run tests   - Dynamic penalties based on window utilization

pytest tests/ -v

2. **Beam search** with configurable width for limited lookahead

# Run with coverage

pytest --cov=fillscheduler --cov-report=html3. **Adaptive selection** that considers downstream effects

```

**Key Advantages:**

## 📝 License- Minimizes changeovers while maximizing window utilization

- Avoids creating unusable slack in windows

This project is licensed under the GNU General Public License v3.0 or later - see the [LICENSE](LICENSE) file for details.- Balances competing objectives effectively



## 🔍 Algorithm Details### MILP Optimization (Exact Solution)



### Smart-Pack Strategy (Recommended)For small instances (≤30 lots), the MILP strategy provides provably optimal schedules:

- Formulated as a traveling salesman variant with block constraints

The `smart-pack` strategy uses:- Uses PuLP with CBC/GLPK solvers

1. **Greedy scoring** with multiple factors:- Minimizes total changeover time + clean blocks

   - Changeover penalties (type-dependent)- Enforces all operational constraints exactly

   - Slack waste prediction (lookahead)

   - Type streak bonuses## 📚 Further Reading

   - Dynamic penalties based on window utilization

- **Strategy Tuning**: See `fillscheduler/config.py` for all tunable parameters

2. **Beam search** with configurable width for limited lookahead- **Validation Logic**: See `fillscheduler/validate.py` for constraint checks

- **Adding Strategies**: Implement the `Strategy` protocol in `fillscheduler/strategies/__init__.py`

3. **Adaptive selection** that considers downstream effects

## 🆘 Support

**Key Advantages:**

- Minimizes changeovers while maximizing window utilization- **Issues**: [GitHub Issues](https://github.com/vikas-py/filling_scheduler/issues)

- Avoids creating unusable slack in windows- **Discussions**: [GitHub Discussions](https://github.com/vikas-py/filling_scheduler/discussions)

- Balances competing objectives effectively

---

### MILP Optimization (Exact Solution)

**Made with ❤️ for pharmaceutical manufacturing optimization**

For small instances (≤30 lots), the MILP strategy provides provably optimal schedules:
- Formulated as a traveling salesman variant with block constraints
- Uses PuLP with CBC/GLPK solvers
- Minimizes total changeover time + clean blocks
- Enforces all operational constraints exactly

## 📈 Performance

Typical performance on standard hardware:

| Dataset Size | smart-pack | spt/lpt-pack | milp-opt |
|--------------|------------|--------------|----------|
| 15 lots | < 0.1s | < 0.05s | 1-10s |
| 50 lots | < 0.5s | < 0.1s | ⚠️ Slow |
| 100 lots | < 1s | < 0.2s | ❌ Not recommended |
| 500 lots | < 5s | < 1s | ❌ Not supported |

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/vikas-py/filling_scheduler/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vikas-py/filling_scheduler/discussions)
- **Documentation**: See `docs/` directory

## 🎯 Use Cases

- **Pharmaceutical Manufacturing**: Optimize filling line schedules
- **Production Planning**: Minimize changeover times and maximize utilization
- **Capacity Analysis**: Evaluate different scheduling strategies
- **Research**: Benchmark heuristic vs optimal solutions
- **Education**: Learn about scheduling algorithms

## 🚀 Roadmap

See [Restructuring_TODO.md](Restructuring_TODO.md) for planned improvements:
- [ ] CLI improvements with Click/Typer
- [ ] Additional test coverage
- [ ] Structured logging
- [ ] CI/CD workflows
- [ ] Pre-commit hooks
- [ ] Web interface (future)

## 📊 Related Projects

- [OR-Tools](https://developers.google.com/optimization) - Google's optimization tools
- [PuLP](https://coin-or.github.io/pulp/) - Linear programming library
- [Schedule](https://schedule.readthedocs.io/) - Simple job scheduling

---

**Made with ❤️ for pharmaceutical manufacturing optimization**
