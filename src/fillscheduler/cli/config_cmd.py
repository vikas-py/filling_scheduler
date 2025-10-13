"""Config command for configuration management."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from fillscheduler.config import AppConfig
from fillscheduler.config_loader import export_default_config, load_config_from_file

console = Console()


@click.group()
def config():
    """Manage configuration files and settings."""
    pass


@config.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    required=True,
    help="Output file path for configuration",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["yaml", "json"], case_sensitive=False),
    default="yaml",
    help="Configuration file format",
)
@click.option(
    "--no-comments",
    is_flag=True,
    help="Exclude documentation comments (YAML only)",
)
def export(output: Path, format: str, no_comments: bool):
    """
    Export default configuration template.

    Creates a configuration file with all available options
    and their default values, with inline documentation.

    Examples:

        \b
        # Export YAML configuration with comments
        fillscheduler config export --output config.yaml

        \b
        # Export JSON configuration
        fillscheduler config export --output config.json --format json

        \b
        # Export without documentation comments
        fillscheduler config export --output config.yaml --no-comments
    """
    try:
        # Ensure parent directory exists
        output.parent.mkdir(parents=True, exist_ok=True)

        # Export configuration
        export_default_config(
            format=format.lower(),
            path=output,
        )

        console.print(f"[green]✓[/green] Configuration exported to: {output}")

        # Show preview
        if output.exists():
            console.print("\n[bold]Preview:[/bold]")
            content = output.read_text()
            syntax = Syntax(content, format, theme="monokai", line_numbers=True)
            console.print(syntax)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort() from e


@config.command()
@click.option(
    "-f",
    "--file",
    "config_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Configuration file to validate",
)
def validate(config_file: Path):
    """
    Validate a configuration file.

    Checks the configuration file for syntax errors and
    validates all options against the schema.

    Examples:

        \b
        # Validate YAML configuration
        fillscheduler config validate --file config.yaml

        \b
        # Validate JSON configuration
        fillscheduler config validate --file config.json
    """
    try:
        console.print(f"Validating configuration file: {config_file}")

        # Try to load configuration
        cfg = load_config_from_file(config_file, validate=True)

        console.print("[green]✓ Configuration is valid![/green]\n")

        # Show summary
        _print_config_summary(cfg)

    except Exception as e:
        console.print("[bold red]✗ Validation failed:[/bold red]")
        console.print(f"  {e}")
        raise click.Abort() from e


@config.command()
@click.option(
    "-f",
    "--file",
    "config_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Configuration file to show (optional, defaults to current config)",
)
def show(config_file: Path | None):
    """
    Display current configuration settings.

    Shows all configuration values, either from a file
    or the default configuration.

    Examples:

        \b
        # Show default configuration
        fillscheduler config show

        \b
        # Show specific configuration file
        fillscheduler config show --file config.yaml
    """
    try:
        if config_file:
            console.print(f"Loading configuration from: {config_file}")
            cfg = load_config_from_file(config_file)
        else:
            console.print("Using default configuration")
            cfg = AppConfig()

        _print_config_summary(cfg)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort() from e


def _print_config_summary(cfg: AppConfig):
    """Print detailed configuration summary."""
    # Data paths
    table = Table(title="Data & Output", show_header=False, box=None)
    table.add_column("Setting", style="cyan")
    table.add_column("Value")
    table.add_row("Data Path", str(cfg.DATA_PATH))
    table.add_row("Output Directory", str(cfg.OUTPUT_DIR))
    table.add_row("Start Time", cfg.START_TIME_STR)
    console.print(table)
    console.print()

    # Strategy
    table = Table(title="Scheduling", show_header=False, box=None)
    table.add_column("Setting", style="cyan")
    table.add_column("Value")
    table.add_row("Strategy", cfg.STRATEGY)
    console.print(table)
    console.print()

    # Constraints
    table = Table(title="Constraints", show_header=False, box=None)
    table.add_column("Setting", style="cyan")
    table.add_column("Value")
    table.add_row("Fill Rate", f"{cfg.FILL_RATE_VPH:,} vials/hour")
    table.add_row("Window Hours", f"{cfg.WINDOW_HOURS} hours")
    table.add_row("Clean Hours", f"{cfg.CLEAN_HOURS} hours")
    table.add_row("Changeover Same Type", f"{cfg.CHG_SAME_HOURS} hours")
    table.add_row("Changeover Diff Type", f"{cfg.CHG_DIFF_HOURS} hours")
    console.print(table)
    console.print()

    # Strategy-specific settings
    if cfg.STRATEGY == "smart-pack":
        table = Table(title="Smart-Pack Settings", show_header=False, box=None)
        table.add_column("Setting", style="cyan")
        table.add_column("Value")
        table.add_row("Beam Width", str(cfg.BEAM_WIDTH))
        table.add_row("Slack Waste Weight", f"{cfg.SLACK_WASTE_WEIGHT:.1f}")
        table.add_row("Streak Bonus", f"{cfg.STREAK_BONUS:.1f}")
        console.print(table)
        console.print()
    elif cfg.STRATEGY == "cfs-pack":
        table = Table(title="CFS-Pack Settings", show_header=False, box=None)
        table.add_column("Setting", style="cyan")
        table.add_column("Value")
        table.add_row("Cluster Order", cfg.CFS_CLUSTER_ORDER)
        table.add_row("Within Cluster", cfg.CFS_WITHIN)
        console.print(table)
        console.print()
    elif cfg.STRATEGY == "milp-opt":
        table = Table(title="MILP Settings", show_header=False, box=None)
        table.add_column("Setting", style="cyan")
        table.add_column("Value")
        table.add_row("Max Lots", str(cfg.MILP_MAX_LOTS))
        table.add_row("Time Limit", f"{cfg.MILP_TIME_LIMIT} seconds")
        console.print(table)
        console.print()
