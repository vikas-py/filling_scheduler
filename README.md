# Filling Scheduler

[![Tests](https://img.shields.io/badge/tests-160%20passed-brightgreen)](https://github.com/vikas-py/filling_scheduler)
[![Coverage](https://img.shields.io/badge/coverage-74.6%25-brightgreen)](htmlcov/index.html)
[![Code Quality](https://img.shields.io/badge/code%20quality-pre--commit%20hooks-blue)](.pre-commit-config.yaml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Ubuntu%20%7C%20Windows%20%7C%20macOS-lightgrey)](docs/UBUNTU_DEPLOYMENT_GUIDE.md)

A production-grade pharmaceutical filling line scheduler that optimizes lot sequencing under strict operational constraints. The system implements multiple scheduling strategies ranging from fast heuristics to exact optimization.

**🚀 Now with Web UI, PDF Reports, and Interactive Gantt Charts!**

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

### Modern Command-Line Interface
- 🖥️ Professional CLI with Click framework
- 🎨 Beautiful Rich terminal output with colors and progress bars
- ⚡ Progress indicators for long operations
- 📊 Formatted tables for KPIs and configuration
- 🔍 Verbose mode for debugging
- ✨ Syntax highlighting for configuration files

### Configuration Management
- ⚙️ YAML/JSON configuration file support
- 🔧 Environment variable support (12-factor app)
- ✅ Pydantic-based validation
- 📋 Automatic configuration discovery
- 💾 Export default configuration templates
- 🔍 Configuration validation commands

### Web Application
- 🌐 Modern React + TypeScript frontend with Material-UI
- 🔐 JWT authentication with role-based access control
- 📊 Interactive dashboard with real-time statistics
- 📈 Timeline Gantt chart with zoom/filter/highlight controls
- 📄 Professional PDF reports with embedded charts
- 📊 Excel export with multiple worksheets
- 🖼️ High-resolution PNG chart export
- 📱 Responsive design for mobile/tablet

### Rich Reporting
- 📊 CSV/JSON/Excel schedule exports
- 🎨 Interactive HTML reports with color-coded activities
- 📈 KPI tracking (makespan, utilization, changeover analysis)
- 🔄 Multi-strategy comparison tools
- 📄 **Professional PDF reports** with WeasyPrint and Plotly charts
- 📊 **Excel workbooks** with Summary, Activities, and Configuration sheets

---

## 🚀 Quick Start

### Ubuntu Server Deployment (Recommended for Production)

**One-command installation** with Nginx, systemd service, and SSL support:

```bash
cd /opt
sudo git clone https://github.com/vikas-py/filling_scheduler.git
cd filling_scheduler
sudo bash scripts/install_ubuntu.sh
```

**Access**: `http://your-server-ip`

📚 **Full Guide**: [Ubuntu Deployment Guide](docs/UBUNTU_DEPLOYMENT_GUIDE.md) | [Quick Start](docs/UBUNTU_QUICK_START.md)

---

### Local Development Installation

```bash
# Clone the repository
git clone https://github.com/vikas-py/filling_scheduler.git
cd filling_scheduler

# Backend Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend Setup
cd frontend
npm install
npm run dev

# Backend Server (separate terminal)
cd ..
uvicorn src.fillscheduler.api.main:app --reload
```

**Access**: `http://localhost:5173`

---

### CLI Usage Examples

```bash
# Generate a schedule (with beautiful progress indicators)
fillscheduler schedule --data examples/lots.csv --strategy smart-pack

# Compare multiple strategies
fillscheduler compare --data examples/lots.csv --strategies smart-pack spt-pack lpt-pack

# Compare all available strategies
fillscheduler compare --data examples/lots.csv --all-strategies

# Export default configuration
fillscheduler config export --output config.yaml

# Validate configuration
fillscheduler config validate --file config.yaml

# Show current configuration
fillscheduler config show

# View help and options
fillscheduler --help
fillscheduler schedule --help
```

### Using Configuration Files

```bash
# Export a configuration template
fillscheduler config export --output myconfig.yaml

# Edit myconfig.yaml with your preferred settings

# Use the configuration file
fillscheduler --config myconfig.yaml schedule

# Override specific settings
fillscheduler --config myconfig.yaml schedule --strategy lpt-pack --output results/
```

### Legacy Python Scripts (Deprecated)

```bash
# These still work but are deprecated - use the CLI instead
python main.py                    # Use: fillscheduler schedule
python compare_runs.py            # Use: fillscheduler compare
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

The scheduler supports flexible configuration through multiple methods:

### Configuration Files (Recommended)

```bash
# Export default configuration template
python -c "from fillscheduler.config_loader import export_default_config; export_default_config('yaml')"

# Creates .fillscheduler.yaml with all options documented
```

Edit the generated file:
```yaml
# .fillscheduler.yaml
strategy: "milp"
fill_rate_vph: 20000.0
strategies:
  milp:
    time_limit: 120
```

Configuration files are automatically discovered from:
1. `.fillscheduler.yaml` in current directory
2. `~/.config/fillscheduler/config.yaml` for user-wide settings

### Environment Variables

```bash
export FILLSCHEDULER_STRATEGY=milp
export FILLSCHEDULER_STRATEGIES__MILP__TIME_LIMIT=120
```

### Programmatic Configuration

```python
from fillscheduler.config_loader import load_config_with_overrides
from pathlib import Path

config = load_config_with_overrides(
    config_path=Path("my_config.yaml"),
    overrides={"strategy": "smart-pack"}
)
```

📖 **Full documentation:** [``docs/configuration.md``](docs/configuration.md)

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

**Current Status:**
- ✅ 160/160 tests passing (+334% from initial 37 tests)
- 📊 74.6% code coverage (+35% from initial 55.3%)
- 📈 Coverage report: `htmlcov/index.html`
- 🎯 34 tests for configuration validation
- 🧪 Test fixtures: 20 CSV files for comprehensive testing

### Coverage by Module

| Module | Coverage | Status |
|:-------|:---------|:-------|
| **Core Modules** | | |
| config.py | 100% | ✅ Excellent |
| models.py | 100% | ✅ Excellent |
| rules.py | 100% | ✅ Excellent |
| io_utils.py | 100% | ✅ Excellent |
| reporting.py | 100% | ✅ Excellent |
| compare.py | 100% | ✅ Excellent |
| seq_utils.py | 100% | ✅ Excellent |
| validate.py | 93.4% | ✅ Excellent |
| scheduler.py | 83.2% | ✅ Excellent |
| **Strategies** | | |
| spt_pack.py | 98.0% | ✅ Excellent |
| lpt_pack.py | 97.1% | ✅ Excellent |
| hybrid_pack.py | 90.8% | ✅ Excellent |
| smart_pack.py | 90.8% | ✅ Excellent |
| cfs_pack.py | 81.5% | ✅ Good |
| strategies/__init__.py | 80.0% | ✅ Good |
| **CLI Modules** | | |
| cli/schedule.py | 0% | ⚠️ Not tested |
| cli/compare.py | 0% | ⚠️ Not tested |
| compare_sequences.py | 0% | ⚠️ Not tested |
| milp_opt.py | 0% | ⚠️ Not tested |

---

## 📚 Documentation

### User Documentation
| Document | Description |
|:---------|:------------|
| [Getting Started](docs/getting_started.md) | Installation, first schedule, troubleshooting |
| [Configuration Guide](docs/configuration.md) | YAML/JSON configs, environment variables, validation |
| [Strategies Guide](docs/strategies.md) | Detailed strategy comparison (4500+ words) |
| [Type Checking](docs/type_checking.md) | mypy configuration and type hints guide |
| [API Reference](docs/api_reference.md) | Programmatic usage |
| [Examples](docs/examples.md) | Real-world scenarios |

### Project Planning
| Document | Description |
|:---------|:------------|
| [Restructuring TODO](Restructuring_TODO.md) | Main project roadmap (78% complete, 44/56 items) |
| [API & Frontend Plan](API_FRONTEND_TODO.md) | 🚀 **NEW**: Detailed plan for FastAPI + React web app (172 items) |
| [API Architecture](API_ARCHITECTURE.md) | 🚀 **NEW**: System design, data flow, deployment strategy |
| [Phase 1.6 WebSocket Design](docs/PHASE_1.6_WEBSOCKET_DESIGN.md) | ⚡ **IN PROGRESS**: Real-time progress updates design |

---

## 🚀 Future: Web Application

A comprehensive plan for a full-stack web application is available! See:
- **[API_FRONTEND_TODO.md](API_FRONTEND_TODO.md)** - Complete 172-item implementation plan
- **[API_ARCHITECTURE.md](API_ARCHITECTURE.md)** - Architecture diagrams and design

**Tech Stack**: FastAPI + React 18 + Vite + TypeScript + Material-UI + PostgreSQL
**Features**: Authentication, real-time progress (WebSocket), interactive Gantt charts, strategy comparison dashboards
**Timeline**: 8-12 weeks for MVP

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
