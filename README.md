# Filling Scheduler# Filling Scheduler# Filling Scheduler# Filling Scheduler



[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/vikas-py/filling_scheduler)

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

[![License](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/vikas-py/filling_scheduler)
<<<<<<< HEAD



A production-grade pharmaceutical filling line scheduler that optimizes lot sequencing under strict operational constraints. The system implements multiple scheduling strategies ranging from fast heuristics to exact optimization.[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)



---[![License](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/vikas-py/filling_scheduler)Generates a filling line schedule under strict constraints:
=======

Generates a filling line schedule under strict constraints:

A production-grade pharmaceutical filling line scheduler that optimizes lot sequencing under strict operational constraints. The system implements multiple scheduling strategies ranging from fast heuristics to exact optimization. Clean before use (24h)



## ✨ Features:
>>>>>>> 94c06f5a1fe1f2fa79f46ef0693a2bd1822f9987



## ✨ Features



### Multiple Optimization StrategiesA production-grade pharmaceutical filling line scheduler that optimizes lot sequencing under strict operational constraints. The system implements multiple scheduling strategies ranging from fast heuristics to exact optimization.[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)- Clean before use (24h)

- **`smart-pack`** - Advanced heuristic with look-ahead and slack optimization _(recommended)_

- **`spt-pack`** - Shortest Processing Time first

- **`lpt-pack`** - Longest Processing Time first

- **`cfs-pack`** - Cluster-First, Schedule-Second approach## ✨ Features[![License](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)- Clean window <= 120h (fills + changeovers)

- **`hybrid-pack`** - Combined heuristic strategy

- **`milp-opt`** - Exact Mixed Integer Linear Programming optimization



### Strict Constraint Validation- **Multiple Optimization Strategies**- Changeover: 4h (same type), 8h (different type)

- ✅ Clean before use (24h requirement)

- ✅ Clean window limits (≤ 120h for fills + changeovers)  - `smart-pack` - Advanced heuristic with look-ahead and slack optimization (recommended)

- ✅ Changeover times (4h same type, 8h different type)

- ✅ Fill rate enforcement (332 vials/min = 19,920 vials/h)  - `spt-pack` - Shortest Processing Time firstA production-grade pharmaceutical filling line scheduler that optimizes lot sequencing under strict operational constraints. The system implements multiple scheduling strategies ranging from fast heuristics to exact optimization.- Fill rate: 332 vials/min (19,920 vials/h)

- ✅ No lot splitting allowed

- ✅ Preflight and postflight validation  - `lpt-pack` - Longest Processing Time first



### Rich Reporting  - `cfs-pack` - Cluster-First, Schedule-Second approach- No lot splitting

- 📊 CSV schedule exports

- 🎨 Interactive HTML reports with color-coded activities  - `hybrid-pack` - Combined heuristic strategy

- 📈 KPI tracking (makespan, utilization, changeover analysis)

- 🔄 Multi-strategy comparison tools  - `milp-opt` - Exact Mixed Integer Linear Programming optimization## ✨ Features- Strict validation: impossible inputs fail early



---



## 🚀 Quick Start- **Strict Constraint Validation**



### Installation  - Clean before use (24h requirement)



```bash  - Clean window limits (≤ 120h for fills + changeovers)- **Multiple Optimization Strategies**## Run

# Clone the repository

git clone https://github.com/vikas-py/filling_scheduler.git  - Changeover times (4h same type, 8h different type)

cd filling_scheduler

  - Fill rate enforcement (332 vials/min = 19,920 vials/h)  - `smart-pack` - Advanced heuristic with look-ahead and slack optimization (recommended)

# Create virtual environment

python -m venv .venv  - No lot splitting allowed



# Activate virtual environment  - Preflight and postflight validation  - `spt-pack` - Shortest Processing Time first```bash

# Windows:

.venv\Scripts\activate

# macOS/Linux:

source .venv/bin/activate- **Rich Reporting**  - `lpt-pack` - Longest Processing Time firstpython -m venv .venv



# Install dependencies  - CSV schedule exports

pip install -r requirements.txt

  - Interactive HTML reports with color-coded activities  - `cfs-pack` - Cluster-First, Schedule-Second approachsource .venv/bin/activate    # Windows: .venv\Scripts\activate

# Optional: Install MILP optimization support

pip install pulp>=2.7  - KPI tracking (makespan, utilization, changeover analysis)



# Optional: Install development dependencies  - Multi-strategy comparison tools  - `hybrid-pack` - Combined heuristic strategypip install -r requirements.txt

pip install -r requirements-dev.txt

```



### Basic Usage## 🚀 Quick Start  - `milp-opt` - Exact Mixed Integer Linear Programming optimizationpython main.py



```bash

# Run with default settings (smart-pack strategy, example data)

python main.py### Installation- **Strict Constraint Validation**



# Outputs will be in: ./output/  - Clean before use (24h requirement)

#   - schedule.csv      (detailed schedule)

#   - summary.txt       (KPI summary)```bash  - Clean window limits (≤ 120h for fills + changeovers)

#   - report.html       (interactive visualization)

```# Clone the repository  - Changeover times (4h same type, 8h different type)



### Compare Strategiesgit clone https://github.com/vikas-py/filling_scheduler.git  - Fill rate enforcement (332 vials/min = 19,920 vials/h)



```bashcd filling_scheduler  - No lot splitting allowed

# Compare multiple strategies on the same dataset

python compare_runs.py --data examples/lots.csv --strategies smart-pack spt-pack lpt-pack  - Preflight and postflight validation



# Outputs:# Create virtual environment

#   - output/comparison_kpis.csv

#   - output/comparison_report.htmlpython -m venv .venv- **Rich Reporting**

```

  - CSV schedule exports

---

# Activate virtual environment  - Interactive HTML reports with color-coded activities

## 📋 Operational Constraints

# On Windows:  - KPI tracking (makespan, utilization, changeover analysis)

The scheduler operates under these pharmaceutical manufacturing constraints:

.venv\Scripts\activate  - Multi-strategy comparison tools

| Constraint | Value | Description |

|:-----------|:------|:------------|# On macOS/Linux:

| **Clean Time** | 24 hours | Required cleaning before each production block |

| **Clean Window** | ≤ 120 hours | Maximum time for fills + changeovers per block |source .venv/bin/activate## 🚀 Quick Start

| **Changeover (Same)** | 4 hours | Setup time when switching between same vial types |

| **Changeover (Different)** | 8 hours | Setup time when switching between different vial types |

| **Fill Rate** | 19,920 vials/hour | 332 vials/minute production rate |

| **Lot Splitting** | ❌ Not allowed | Each lot must be completed in a single block |# Install dependencies### Installation



---pip install -r requirements.txt



## 🎯 Strategy Comparison```bash



| Strategy | Speed | Quality | Best For |# Optional: Install MILP optimization support# Clone the repository

|:---------|:------|:--------|:---------|

| **`smart-pack`** | ⚡ Fast | ⭐⭐⭐⭐⭐ Excellent | **Recommended for most cases** |pip install pulp>=2.7git clone https://github.com/vikas-py/filling_scheduler.git

| **`spt-pack`** | ⚡⚡ Very Fast | ⭐⭐⭐⭐ Good | Quick schedules, many small lots |

| **`lpt-pack`** | ⚡⚡ Very Fast | ⭐⭐⭐⭐ Good | Datasets with large lots |cd filling_scheduler

| **`cfs-pack`** | ⚡ Fast | ⭐⭐⭐⭐ Good | Type-heavy datasets |

| **`hybrid-pack`** | ⚡ Fast | ⭐⭐⭐⭐ Good | Balanced datasets |# Optional: Install development dependencies

| **`milp-opt`** | 🐌 Slow | ⭐⭐⭐⭐⭐ Optimal | Small datasets (≤30 lots), benchmarking |

pip install -r requirements-dev.txt# Create virtual environment

### Performance Guide

```python -m venv .venv

| Dataset Size | smart-pack | spt/lpt-pack | milp-opt |

|:-------------|:-----------|:-------------|:---------|

| **15 lots** | < 0.1s | < 0.05s | 1-10s ✅ |

| **50 lots** | < 0.5s | < 0.1s | ⚠️ Slow |### Basic Usage# Activate virtual environment

| **100 lots** | < 1s | < 0.2s | ❌ Not recommended |

| **500+ lots** | < 5s | < 1s | ❌ Not supported |# On Windows:



---```bash.venv\Scripts\activate



## ⚙️ Configuration# Run with default settings (smart-pack strategy, example data)# On macOS/Linux:



Edit `src/fillscheduler/config.py` to customize:python main.pysource .venv/bin/activate



```python

from fillscheduler.config import AppConfig

from pathlib import Path# Outputs will be in: ./output/# Install dependencies



cfg = AppConfig(#   - schedule.csv      (detailed schedule)pip install -r requirements.txt

    # Input/Output

    DATA_PATH=Path("examples/lots.csv"),#   - summary.txt       (KPI summary)

    OUTPUT_DIR=Path("output"),

    START_TIME_STR="2025-01-01 08:00",#   - report.html       (interactive visualization)# Optional: Install MILP optimization support

    STRATEGY="smart-pack",

    ```pip install pulp>=2.7

    # Process Constants

    FILL_RATE_VPH=19920.0,        # Vials per hour

    CLEAN_HOURS=24.0,

    WINDOW_HOURS=120.0,### Compare Strategies# Optional: Install development dependencies

    CHG_SAME_HOURS=4.0,

    CHG_DIFF_HOURS=8.0,pip install -r requirements-dev.txt

    

    # Strategy Tuning (smart-pack)```bash```

    BEAM_WIDTH=3,                  # Look-ahead depth

    SLACK_WASTE_WEIGHT=3.0,       # Penalty for wasted capacity# Compare multiple strategies on the same dataset

    STREAK_BONUS=1.0,             # Bonus for type consistency

)python compare_runs.py --data examples/lots.csv --strategies smart-pack spt-pack lpt-pack### Basic Usage

```



---

# Outputs:```bash

## 📊 Input Data Format

#   - output/comparison_kpis.csv# Run with default settings (smart-pack strategy, example data)

Create a CSV file with the following columns:

#   - output/comparison_report.htmlpython main.py

```csv

Lot ID,Type,Vials```

A1,VialE,100000

A2,VialH,900000# Outputs will be in: ./output/

A3,VialE,750000

```## 📋 Operational Constraints#   - schedule.csv      (detailed schedule)



**Column Descriptions:**#   - summary.txt       (KPI summary)

- **Lot ID** - Unique identifier for each lot

- **Type** - Vial type (e.g., VialE, VialH, VialF)The scheduler operates under these pharmaceutical manufacturing constraints:#   - report.html       (interactive visualization)

- **Vials** - Number of vials to fill (positive integer)

```

📁 See [`examples/lots.csv`](examples/lots.csv) for a complete example.

| Constraint | Value | Description |

### Generate Test Data

|------------|-------|-------------|### Compare Strategies

```bash

cd examples| **Clean Time** | 24 hours | Required cleaning before each production block |

python gen_lots.py  # Generates lots_large.csv with 500 lots

```| **Clean Window** | ≤ 120 hours | Maximum time for fills + changeovers per block |```bash



---| **Changeover (Same Type)** | 4 hours | Setup time when switching between same vial types |# Compare multiple strategies on the same dataset



## 📈 Output Format| **Changeover (Different Type)** | 8 hours | Setup time when switching between different vial types |python compare_runs.py --data examples/lots.csv --strategies smart-pack spt-pack lpt-pack



### Schedule CSV| **Fill Rate** | 19,920 vials/hour | 332 vials/minute production rate |



```csv| **Lot Splitting** | Not allowed | Each lot must be completed in a single block |# Outputs:

Start,End,Hours,Activity,Lot ID,Type,Note

2025-01-01 08:00,2025-01-02 08:00,24.0,CLEAN,,,Block reset#   - output/comparison_kpis.csv

2025-01-02 08:00,2025-01-02 13:01,5.02,FILL,A1,VialE,100000 vials

2025-01-02 13:01,2025-01-02 17:01,4.0,CHANGEOVER,,VialE->VialE,4h## 🎯 Strategy Comparison#   - output/comparison_report.html

2025-01-02 17:01,2025-01-03 07:48,14.78,FILL,A3,VialE,750000 vials

``````



### KPI Summary| Strategy | Speed | Quality | Best For |



```|----------|-------|---------|----------|## 📋 Operational Constraints

─────────────────────────────────

📊 Schedule Summary| `smart-pack` | Fast | Excellent | **Recommended for most cases** |

─────────────────────────────────

Makespan (h):         156.32| `spt-pack` | Very Fast | Good | Quick schedules, many small lots |The scheduler operates under these pharmaceutical manufacturing constraints:

Total Clean (h):       48.00

Total Changeover (h):  28.00| `lpt-pack` | Very Fast | Good | Datasets with large lots |

Total Fill (h):        80.32

Lots Scheduled:        15| `cfs-pack` | Fast | Good | Type-heavy datasets || Constraint | Value | Description |

Clean Blocks:          2

Utilization:          51.4%| `hybrid-pack` | Fast | Good | Balanced datasets ||------------|-------|-------------|

─────────────────────────────────

```| `milp-opt` | Slow | Optimal | Small datasets (≤30 lots), benchmarking || **Clean Time** | 24 hours | Required cleaning before each production block |



### Interactive HTML Report| **Clean Window** | ≤ 120 hours | Maximum time for fills + changeovers per block |



The generated `report.html` includes:**Performance Guide:**| **Changeover (Same Type)** | 4 hours | Setup time when switching between same vial types |

- 🎨 Color-coded Gantt chart

- 📊 KPI dashboard- 15 lots: All strategies < 1 second| **Changeover (Different Type)** | 8 hours | Setup time when switching between different vial types |

- 📋 Detailed activity timeline

- 🔍 Filterable lot information- 100 lots: Heuristics < 1s, MILP not recommended| **Fill Rate** | 19,920 vials/hour | 332 vials/minute production rate |



---- 500+ lots: Use heuristics only (smart-pack, spt-pack, lpt-pack)| **Lot Splitting** | Not allowed | Each lot must be completed in a single block |



## 🧪 Testing



```bash## ⚙️ Configuration## 🎯 Strategy Comparison

# Run all tests

pytest



# Run with coverageEdit `src/fillscheduler/config.py` to customize:| Strategy | Speed | Quality | Best For |

pytest --cov=fillscheduler --cov-report=html

|----------|-------|---------|----------|

# Run specific test file

pytest tests/test_input_validation.py -v```python| `smart-pack` | Fast | Excellent | **Recommended for most cases** |



# Run with verbose outputfrom fillscheduler.config import AppConfig| `spt-pack` | Very Fast | Good | Quick schedules, many small lots |

pytest -vv

```from pathlib import Path| `lpt-pack` | Very Fast | Good | Datasets with large lots |



**Current Status:** ✅ 11/11 tests passing| `cfs-pack` | Fast | Good | Type-heavy datasets |



---cfg = AppConfig(| `hybrid-pack` | Fast | Good | Balanced datasets |



## 🏗️ Project Structure    DATA_PATH=Path("examples/lots.csv"),| `milp-opt` | Slow | Optimal | Small datasets (≤30 lots), benchmarking |



```    OUTPUT_DIR=Path("output"),

filling_scheduler/

├── 📁 src/    START_TIME_STR="2025-01-01 08:00",**Performance Guide:**

│   └── fillscheduler/          # Main package

│       ├── cli/                # CLI commands    STRATEGY="smart-pack",           # Choose your strategy- 15 lots: All strategies < 1 second

│       │   ├── __init__.py

│       │   ├── schedule.py    - 100 lots: Heuristics < 1s, MILP not recommended

│       │   └── compare.py

│       ├── strategies/         # Optimization strategies    # Process constants- 500+ lots: Use heuristics only (smart-pack, spt-pack, lpt-pack)

│       │   ├── smart_pack.py   # Recommended

│       │   ├── spt_pack.py    FILL_RATE_VPH=19920.0,           # Vials per hour

│       │   ├── lpt_pack.py

│       │   ├── cfs_pack.py    CLEAN_HOURS=24.0,## ⚙️ Configuration

│       │   ├── hybrid_pack.py

│       │   └── milp_opt.py     # Exact optimization    WINDOW_HOURS=120.0,

│       ├── models.py           # Data models (Lot, Activity)

│       ├── config.py           # Configuration    CHG_SAME_HOURS=4.0,Edit `fillscheduler/config.py` to customize:

│       ├── scheduler.py        # Scheduling engine

│       ├── validate.py         # Validation logic    CHG_DIFF_HOURS=8.0,

│       ├── rules.py            # Business rules

│       ├── io_utils.py         # CSV I/O    ```python

│       ├── reporting.py        # Report generation

│       └── compare.py          # Strategy comparison    # Strategy tuning (smart-pack)from fillscheduler.config import AppConfig

├── 📁 docs/                    # Documentation

│   ├── index.md                # Documentation hub    BEAM_WIDTH=3,                     # Look-ahead depth

│   ├── getting_started.md      # Installation & first run

│   ├── strategies.md           # Strategy deep-dive (4500+ words)    SLACK_WASTE_WEIGHT=3.0,          # Penalty for wasted capacitycfg = AppConfig(

│   ├── configuration.md        # Configuration reference

│   ├── api_reference.md        # Programmatic usage    STREAK_BONUS=1.0,                # Bonus for type consistency    DATA_PATH=Path("examples/lots.csv"),

│   └── examples.md             # Real-world examples

├── 📁 tests/                   # Test suite (11 tests))    OUTPUT_DIR=Path("output"),

│   ├── conftest.py

│   ├── test_input_validation.py```    START_TIME_STR="2025-01-01 08:00",

│   └── test_schedule_validation.py

├── 📁 examples/                # Example datasets    STRATEGY="smart-pack",           # Choose your strategy

│   ├── lots.csv                # Small dataset (15 lots)

│   ├── lots_large.csv          # Large dataset (500 lots)## 📊 Input Data Format    

│   ├── gen_lots.py             # Data generator

│   └── README.md    # Process constants

├── 📁 scripts/                 # Utility scripts

├── main.py                     # CLI entry pointCreate a CSV file with the following columns:    FILL_RATE_VPH=19920.0,           # Vials per hour

├── compare_runs.py             # Strategy comparison tool

├── pyproject.toml              # Modern Python packaging    CLEAN_HOURS=24.0,

├── setup.py                    # Backward compatibility

├── requirements.txt            # Production dependencies```csv    WINDOW_HOURS=120.0,

├── requirements-dev.txt        # Development dependencies

├── MANIFEST.in                 # Distribution manifestLot ID,Type,Vials    CHG_SAME_HOURS=4.0,

├── CHANGELOG.md                # Version history

└── README.md                   # This fileA1,VialE,100000    CHG_DIFF_HOURS=8.0,

```

A2,VialH,900000    

---

A3,VialE,750000    # Strategy tuning (smart-pack)

## 📚 Documentation

```    BEAM_WIDTH=3,                     # Look-ahead depth

Comprehensive documentation is available in the [`docs/`](docs/) directory:

    SLACK_WASTE_WEIGHT=3.0,          # Penalty for wasted capacity

| Document | Description | Lines |

|:---------|:------------|:------|- **Lot ID**: Unique identifier for each lot    STREAK_BONUS=1.0,                # Bonus for type consistency

| **[Getting Started](docs/getting_started.md)** | Installation, first schedule, troubleshooting | 2,800+ |

| **[Strategies Guide](docs/strategies.md)** | Detailed strategy comparison, tuning, decision tree | 4,500+ |- **Type**: Vial type (e.g., VialE, VialH, VialF))

| **[Configuration](docs/configuration.md)** | All configuration options explained | 1,500+ |

| **[API Reference](docs/api_reference.md)** | Programmatic usage and examples | 1,200+ |- **Vials**: Number of vials to fill (positive integer)```

| **[Examples](docs/examples.md)** | Real-world scenarios and integration guides | 1,000+ |



**Total documentation:** 10,000+ words

See `examples/lots.csv` for a complete example.## 📊 Input Data Format

---



## 🤝 Contributing

### Generate Test DataCreate a CSV file with the following columns:

Contributions are welcome! This project follows modern Python best practices:



- **Code Style:** Black formatting (100 char line length)

- **Type Hints:** Comprehensive type annotations```bash```csv

- **Testing:** pytest with good coverage

- **Documentation:** Docstrings for all public APIscd examplesLot ID,Type,Vials



### Development Setuppython gen_lots.py  # Generates lots_large.csv with 500 lotsA1,VialE,100000



```bash```A2,VialH,900000

# Install development dependencies

pip install -r requirements-dev.txtA3,VialE,750000



# Run tests## 📈 Example Output```

pytest tests/ -v



# Run with coverage

pytest --cov=fillscheduler --cov-report=html### Schedule CSV- **Lot ID**: Unique identifier for each lot



# Format code (when pre-commit is set up)```csv- **Type**: Vial type (e.g., VialE, VialH, VialF)

black src/ tests/

```Start,End,Hours,Activity,Lot ID,Type,Note- **Vials**: Number of vials to fill (positive integer)



### Contribution Guidelines2025-01-01 08:00,2025-01-02 08:00,24.0,CLEAN,,,Block reset



1. 🍴 Fork the repository2025-01-02 08:00,2025-01-02 13:01,5.02,FILL,A1,VialE,100000 vialsSee `examples/lots.csv` for a complete example.

2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)

3. ✅ Add tests for new functionality2025-01-02 13:01,2025-01-02 17:01,4.0,CHANGEOVER,,VialE->VialE,4h

4. 💄 Ensure code passes linting and formatting

5. 📝 Update documentation as needed2025-01-02 17:01,2025-01-03 07:48,14.78,FILL,A3,VialE,750000 vials### Generate Test Data

6. 🚀 Submit a pull request

```

See [`Restructuring_TODO.md`](Restructuring_TODO.md) for planned improvements and areas where contributions are needed.

```bash

---

### KPI Summarycd examples

## 📝 License

```python gen_lots.py  # Generates lots_large.csv with 500 lots

This project is licensed under the **GNU General Public License v3.0 or later**.

Makespan (h): 156.32```

See the [LICENSE](LICENSE) file for full details.

Total Clean (h): 48.00

---

Total Changeover (h): 28.00## 📈 Example Output

## 🔍 Algorithm Details

Total Fill (h): 80.32

### Smart-Pack Strategy (Recommended)

Lots Scheduled: 15### Schedule CSV

The `smart-pack` strategy uses a sophisticated multi-factor scoring system:

Clean Blocks: 2```csv

#### 1. Greedy Scoring

```python```Start,End,Hours,Activity,Lot ID,Type,Note

score = (

    - changeover_penalty          # Type-dependent (4h or 8h)2025-01-01 08:00,2025-01-02 08:00,24.0,CLEAN,,,Block reset

    - slack_waste_penalty         # Predicted unused capacity

    + type_streak_bonus           # Consistency reward## 🧪 Testing2025-01-02 08:00,2025-01-02 13:01,5.02,FILL,A1,VialE,100000 vials

    - dynamic_utilization_penalty # Adapts to window fullness

)2025-01-02 13:01,2025-01-02 17:01,4.0,CHANGEOVER,,VialE->VialE,4h

```

```bash2025-01-02 17:01,2025-01-03 07:48,14.78,FILL,A3,VialE,750000 vials

#### 2. Beam Search

- Configurable look-ahead width (`BEAM_WIDTH`)# Run all tests```

- Limited exploration of future states

- Balances speed vs. qualitypytest



#### 3. Adaptive Selection### KPI Summary

- Considers downstream scheduling effects

- Avoids creating unusable slack in windows# Run with coverage```

- Dynamically adjusts priorities based on remaining lots

pytest --cov=fillscheduler --cov-report=htmlMakespan (h): 156.32

**Key Advantages:**

- ⚡ Fast execution (< 1s for 100 lots)Total Clean (h): 48.00

- 🎯 Near-optimal results (typically within 5% of MILP)

- 🧠 Intelligent slack management# Run specific test fileTotal Changeover (h): 28.00

- 🔄 Minimizes changeovers while maximizing utilization

pytest tests/test_input_validation.py -vTotal Fill (h): 80.32

### MILP Optimization (Exact Solution)

```Lots Scheduled: 15

For small instances (≤30 lots), the MILP strategy provides **provably optimal** schedules:

Clean Blocks: 2

- 📐 Formulated as a traveling salesman variant with block constraints

- 🔧 Uses PuLP with CBC/GLPK solvers**Current Test Coverage:** 11 tests passing ✅```

- 🎯 Minimizes: `total_changeover_time + clean_blocks × penalty`

- ✅ Enforces all operational constraints exactly



**When to use MILP:**## 🏗️ Project Structure## 🧪 Testing

- Small datasets (≤30 lots)

- Benchmarking other strategies

- High-stakes scenarios requiring guaranteed optimality

- Research and academic purposes``````bash



---filling_scheduler/# Run all tests



## 🎯 Use Cases├── src/pytest



- **💊 Pharmaceutical Manufacturing** - Optimize filling line schedules│   └── fillscheduler/       # Main package

- **🏭 Production Planning** - Minimize changeover times and maximize utilization

- **📊 Capacity Analysis** - Evaluate different scheduling strategies│       ├── cli/            # CLI commands# Run with coverage

- **🔬 Research** - Benchmark heuristic vs optimal solutions

- **🎓 Education** - Learn about scheduling algorithms│       ├── strategies/     # Optimization strategiespytest --cov=fillscheduler --cov-report=html



---│       ├── models.py       # Data models (Lot, Activity)



## 🚀 Roadmap│       ├── config.py       # Configuration# Run specific test file



See [`Restructuring_TODO.md`](Restructuring_TODO.md) for the complete improvement plan.│       ├── scheduler.py    # Scheduling enginepytest tests/test_input_validation.py -v



### High Priority│       ├── validate.py     # Validation logic```

- [ ] CLI improvements with Click/Typer

- [ ] Additional test coverage (strategy-specific tests)│       ├── rules.py        # Business rules

- [ ] Structured logging with configurable levels

- [ ] CI/CD workflows (GitHub Actions)│       ├── io_utils.py     # CSV I/O**Current Test Coverage:** 11 tests passing ✅

- [ ] Pre-commit hooks (black, ruff, mypy)

│       ├── reporting.py    # Report generation

### Medium Priority

- [ ] Docker containerization│       └── compare.py      # Strategy comparison## 🏗️ Project Structure

- [ ] REST API with FastAPI

- [ ] Database support for input/output├── docs/                   # Documentation

- [ ] Enhanced HTML reports with plotly

- [ ] Performance profiling and optimization│   ├── getting_started.md```



### Future Ideas│   ├── strategies.mdfilling_scheduler/

- [ ] Web interface (React/Vue)

- [ ] Real-time schedule updates│   ├── configuration.md├── fillscheduler/           # Main package

- [ ] Multi-line scheduling

- [ ] Integration with ERP systems│   ├── api_reference.md│   ├── models.py           # Data models (Lot, Activity)



---│   └── examples.md│   ├── config.py           # Configuration



## 📊 Related Projects├── tests/                  # Test suite│   ├── scheduler.py        # Scheduling engine



- **[OR-Tools](https://developers.google.com/optimization)** - Google's optimization tools├── examples/               # Example datasets│   ├── validate.py         # Validation logic

- **[PuLP](https://coin-or.github.io/pulp/)** - Linear programming library (used by milp-opt)

- **[Schedule](https://schedule.readthedocs.io/)** - Simple job scheduling library├── scripts/                # Utility scripts│   ├── rules.py            # Business rules

- **[Python-MIP](https://www.python-mip.com/)** - Mixed Integer Linear Programming tools

- **[Pyomo](http://www.pyomo.org/)** - Python optimization modeling├── main.py                 # CLI entry point│   ├── io_utils.py         # CSV I/O



---├── compare_runs.py         # Strategy comparison tool│   ├── reporting.py        # Report generation



## 🆘 Support├── pyproject.toml          # Modern Python packaging│   ├── compare.py          # Strategy comparison



Need help? Here are your options:├── requirements.txt        # Production dependencies│   └── strategies/         # Optimization strategies



- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/vikas-py/filling_scheduler/issues)└── requirements-dev.txt    # Development dependencies├── tests/                  # Test suite

- 💬 **Discussions:** [GitHub Discussions](https://github.com/vikas-py/filling_scheduler/discussions)

- 📖 **Documentation:** See [`docs/`](docs/) directory```├── examples/               # Example datasets

- 📧 **Contact:** Open an issue for project-related questions

├── main.py                 # CLI entry point

---

## 📚 Documentation├── compare_runs.py         # Strategy comparison tool

## 🙏 Acknowledgments

├── pyproject.toml          # Modern Python packaging

This project uses several excellent open-source libraries:

Comprehensive documentation is available in the `docs/` directory:├── requirements.txt        # Production dependencies

- **pandas** - Data manipulation and analysis

- **PuLP** - Linear programming (optional, for MILP strategy)└── requirements-dev.txt    # Development dependencies

- **pytest** - Testing framework

- **[Getting Started](docs/getting_started.md)** - Installation, first schedule, troubleshooting```

---

- **[Strategies Guide](docs/strategies.md)** - Detailed strategy comparison, tuning, decision tree

<div align="center">

- **[Configuration](docs/configuration.md)** - All configuration options explained## 🤝 Contributing

**Made with ❤️ for pharmaceutical manufacturing optimization**

- **[API Reference](docs/api_reference.md)** - Programmatic usage and examples

⭐ **Star this repo if you find it useful!** ⭐

- **[Examples](docs/examples.md)** - Real-world scenarios and integration guidesContributions are welcome! This project follows modern Python best practices:

</div>



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
