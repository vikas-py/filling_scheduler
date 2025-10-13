# CLI Improvements Implementation Guide

## Status: In Progress (Session 9)

### Completed
- ✅ Added click>=8.0 and rich>=13.0 to requirements.txt
- ✅ Installed Click and Rich packages
- ✅ Added __version__ = "0.2.0" to src/fillscheduler/__init__.py
- ✅ Created src/fillscheduler/cli/main.py with Click command group

### In Progress
- 🔄 Creating CLI command modules (schedule, compare, config)

### Pending
- ⏳ Update pyproject.toml with CLI entry point
- ⏳ Test new CLI commands
- ⏳ Update documentation
- ⏳ Deprecate old entry points

---

## Implementation Plan

### 1. CLI Entry Point (main.py) ✅ DONE
Location: `src/fillscheduler/cli/main.py`

```python
@click.group()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", is_flag=True)
@click.option("--config", type=click.Path())
def cli(ctx, verbose, config):
    """Filling Scheduler CLI"""
    ctx.obj = {"verbose": verbose, "config": config}
```

### 2. Schedule Command
Location: `src/fillscheduler/cli/schedule.py`

**Features to implement:**
- Load configuration from file or command-line args
- Rich progress indicators during processing
- Formatted output tables for KPIs
- Proper error handling with user-friendly messages
- Validation with detailed error reporting

**Usage:**
```bash
fillscheduler schedule --data lots.csv --strategy smart-pack
fillscheduler --config config.yaml schedule
fillscheduler schedule --data lots.csv --output results/ --no-report
```

**Options:**
- `-d, --data PATH`: Input CSV file
- `-o, --output PATH`: Output directory
- `-s, --strategy CHOICE`: Strategy (smart-pack, spt-pack, etc.)
- `--start-time TEXT`: Start time (YYYY-MM-DD HH:MM)
- `--no-validation`: Skip validation
- `--no-report`: Skip HTML report

### 3. Compare Command
Location: `src/fillscheduler/cli/compare.py`

**Features:**
- Compare multiple strategies side-by-side
- Progress bars for each strategy
- Comparison table with color-coded winners
- Export comparison report

**Usage:**
```bash
fillscheduler compare --data lots.csv --strategies smart-pack spt-pack lpt-pack
fillscheduler compare --data lots.csv --all-strategies
fillscheduler compare --config config.yaml --strategies smart-pack milp-opt
```

**Options:**
- `-d, --data PATH`: Input CSV file
- `-o, --output PATH`: Output directory
- `-s, --strategies CHOICE...`: List of strategies to compare
- `--all-strategies`: Compare all available strategies
- `--sort-by CHOICE`: Sort results by (makespan, utilization, changeovers)

### 4. Config Command
Location: `src/fillscheduler/cli/config_cmd.py`

**Subcommands:**
- `export`: Export default configuration template
- `validate`: Validate a configuration file
- `show`: Display current configuration

**Usage:**
```bash
fillscheduler config export --output config.yaml --format yaml
fillscheduler config export --output config.json --format json
fillscheduler config validate --file config.yaml
fillscheduler config show
```

### 5. Entry Point Configuration
Location: `pyproject.toml`

Add to `[project.scripts]`:
```toml
[project.scripts]
fillscheduler = "fillscheduler.cli.main:main"
```

After installation, users can run:
```bash
fillscheduler --help
fillscheduler --version
fillscheduler schedule --data lots.csv
```

---

## Rich Features to Use

### Progress Indicators
```python
from rich.progress import Progress, SpinnerColumn, TextColumn

with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
    task = progress.add_task("Loading lots...", total=None)
    lots = read_lots_with_pandas(path, cfg)
```

### Tables
```python
from rich.table import Table

table = Table(title="KPIs")
table.add_column("Metric", style="cyan")
table.add_column("Value", justify="right", style="green")
table.add_row("Makespan", f"{makespan:.2f} hours")
console.print(table)
```

### Colored Output
```python
console.print("[green]✓[/green] Schedule completed successfully!")
console.print("[bold red]Error:[/bold red] Invalid configuration")
console.print("[yellow]⚠ Warning:[/yellow] Large dataset may take time")
```

---

## Documentation Updates Needed

### README.md
Update usage examples:
```markdown
## Usage

### Command Line

\`\`\`bash
# Generate schedule
fillscheduler schedule --data examples/lots.csv

# Compare strategies
fillscheduler compare --data examples/lots.csv --strategies smart-pack spt-pack

# Export configuration
fillscheduler config export --output config.yaml
\`\`\`
```

### docs/getting_started.md
Add CLI section:
```markdown
## Using the CLI

After installation, the `fillscheduler` command is available:

\`\`\`bash
# View help
fillscheduler --help

# Generate schedule
fillscheduler schedule --data lots.csv --strategy smart-pack

# Use configuration file
fillscheduler --config config.yaml schedule
\`\`\`
```

### docs/examples.md
Update all examples to show CLI usage first, then programmatic usage

---

## Backward Compatibility

Keep existing scripts during transition:
- `main.py` → Add deprecation warning, redirect to CLI
- `compare_runs.py` → Add deprecation warning, redirect to CLI

Example deprecation:
```python
# main.py
import sys
print("Warning: main.py is deprecated. Please use 'fillscheduler schedule' instead.")
print("Run 'fillscheduler --help' for more information.\n")

from fillscheduler.cli.schedule import schedule
if __name__ == "__main__":
    schedule()
```

---

## Testing

### Manual Testing
```bash
# Install in development mode
pip install -e .

# Test commands
fillscheduler --version
fillscheduler --help
fillscheduler schedule --help
fillscheduler schedule --data examples/lots.csv
fillscheduler compare --data examples/lots.csv --strategies smart-pack spt-pack
fillscheduler config export --output test-config.yaml
```

### Unit Tests
Create `tests/unit/test_cli.py`:
```python
from click.testing import CliRunner
from fillscheduler.cli.main import cli

def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.2.0" in result.output

def test_schedule_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["schedule", "--help"])
    assert result.exit_code == 0
    assert "Generate a filling schedule" in result.output
```

---

## Next Steps

1. **Complete schedule.py** - Implement full schedule command with all options
2. **Create compare.py** - Implement compare command with multi-strategy support
3. **Create config_cmd.py** - Implement config management commands
4. **Update pyproject.toml** - Add entry point
5. **Test installation** - `pip install -e .` and test all commands
6. **Update documentation** - Update all docs with CLI examples
7. **Add deprecation warnings** - Update old entry points
8. **Create tests** - Add CLI unit tests
9. **Update TODO** - Mark CLI section as complete

---

## Files Created/Modified

- ✅ `requirements.txt` - Added click and rich
- ✅ `src/fillscheduler/__init__.py` - Added __version__
- ✅ `src/fillscheduler/cli/main.py` - Created CLI entry point
- 🔄 `src/fillscheduler/cli/schedule.py` - In progress
- ⏳ `src/fillscheduler/cli/compare.py` - Pending
- ⏳ `src/fillscheduler/cli/config_cmd.py` - Pending
- ⏳ `pyproject.toml` - Needs entry point update
- ⏳ `README.md` - Needs CLI examples
- ⏳ `docs/getting_started.md` - Needs CLI section
- ⏳ `docs/examples.md` - Needs CLI examples

---

*Created: October 12, 2025 - Session 9*
*Status: Implementation paused due to file handling issues*
*Recommendation: Continue with manual implementation or smaller file chunks*
