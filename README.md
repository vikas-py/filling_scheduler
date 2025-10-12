# Filling Scheduler

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/vikas-py/filling_scheduler)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)

A production-grade pharmaceutical filling line scheduler that optimizes lot sequencing under strict operational constraints. The system implements multiple scheduling strategies ranging from fast heuristics to exact optimization.

---

## ✨ Features

### Multiple Optimization Strategies
- **``smart-pack``** - Advanced heuristic with look-ahead and slack optimization _(recommended)_
- **``spt-pack``** - Shortest Processing Time first
- **``lpt-pack``** - Longest Processing Time first
- **``cfs-pack``** - Cluster-First, Schedule-Second approach
- **``hybrid-pack``** - Combined heuristic strategy
- **``milp-opt``** - Exact Mixed Integer Linear Programming optimization

### Strict Constraint Validation
- ✅ Clean before use (24h requirement)
- ✅ Clean window limits (≤ 120h for fills + changeovers)
- ✅ Changeover times (4h same type, 8h different type)
- ✅ Fill rate enforcement (332 vials/min = 19,920 vials/h)
- ✅ No lot splitting allowed
- ✅ Preflight and postflight validation

### Rich Reporting
- 📊 CSV schedule exports
- 🎨 Interactive HTML reports with color-coded activities
- 📈 KPI tracking (makespan, utilization, changeover analysis)
- 🔄 Multi-strategy comparison tools

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/vikas-py/filling_scheduler.git
cd filling_scheduler

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
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

---

## 📋 Operational Constraints

| Constraint | Value | Description |
|:-----------|:------|:------------|
| **Clean Time** | 24 hours | Required cleaning before each production block |
| **Clean Window** | ≤ 120 hours | Maximum time for fills + changeovers per block |
| **Changeover (Same)** | 4 hours | Setup time when switching between same vial types |
| **Changeover (Different)** | 8 hours | Setup time when switching between different vial types |
| **Fill Rate** | 19,920 vials/hour | 332 vials/minute production rate |
| **Lot Splitting** | ❌ Not allowed | Each lot must be completed in a single block |

---

## 🎯 Strategy Comparison

| Strategy | Speed | Quality | Best For |
|:---------|:------|:--------|:---------|
| **``smart-pack``** | ⚡ Fast | ⭐⭐⭐⭐⭐ Excellent | **Recommended for most cases** |
| **``spt-pack``** | ⚡⚡ Very Fast | ⭐⭐⭐⭐ Good | Quick schedules, many small lots |
| **``lpt-pack``** | ⚡⚡ Very Fast | ⭐⭐⭐⭐ Good | Datasets with large lots |
| **``cfs-pack``** | ⚡ Fast | ⭐⭐⭐⭐ Good | Type-heavy datasets |
| **``hybrid-pack``** | ⚡ Fast | ⭐⭐⭐⭐ Good | Balanced datasets |
| **``milp-opt``** | 🐌 Slow | ⭐⭐⭐⭐⭐ Optimal | Small datasets (≤30 lots), benchmarking |

### Performance Guide

| Dataset Size | smart-pack | spt/lpt-pack | milp-opt |
|:-------------|:-----------|:-------------|:---------|
| **15 lots** | < 0.1s | < 0.05s | 1-10s ✅ |
| **50 lots** | < 0.5s | < 0.1s | ⚠️ Slow |
| **100 lots** | < 1s | < 0.2s | ❌ Not recommended |
| **500+ lots** | < 5s | < 1s | ❌ Not supported |

---

## ⚙️ Configuration

See full documentation in [``docs/configuration.md``](docs/configuration.md)

---

## 📊 Input Data Format

```csv
Lot ID,Type,Vials
A1,VialE,100000
A2,VialH,900000
A3,VialE,750000
```

📁 See [``examples/lots.csv``](examples/lots.csv) for a complete example.

---

## 🧪 Testing

```bash
pytest                                     # Run all tests
pytest --cov=fillscheduler --cov-report=html  # With coverage
```

**Current Status:** ✅ 11/11 tests passing

---

## 📚 Documentation

| Document | Description |
|:---------|:------------|
| [Getting Started](docs/getting_started.md) | Installation, first schedule, troubleshooting |
| [Strategies Guide](docs/strategies.md) | Detailed strategy comparison (4500+ words) |
| [Configuration](docs/configuration.md) | All configuration options |
| [API Reference](docs/api_reference.md) | Programmatic usage |
| [Examples](docs/examples.md) | Real-world scenarios |

---

## 🤝 Contributing

See [``Restructuring_TODO.md``](Restructuring_TODO.md) for planned improvements.

---

## 📝 License

GNU General Public License v3.0 or later - see [LICENSE](LICENSE)

---

<div align="center">

**Made with ❤️ for pharmaceutical manufacturing optimization**

⭐ **Star this repo if you find it useful!** ⭐

</div>
