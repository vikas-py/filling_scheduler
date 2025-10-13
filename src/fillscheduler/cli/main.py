"""Main CLI entry point for Filling Scheduler."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console

from fillscheduler import __version__
from fillscheduler.cli.compare import compare
from fillscheduler.cli.config_cmd import config
from fillscheduler.cli.schedule import schedule

# Rich console for better output
console = Console()

# Context settings for consistent help formatting
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__, prog_name="fillscheduler")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to configuration file (YAML or JSON)",
)
@click.pass_context
def cli(ctx, verbose: bool, config: Path | None):
    """
    Filling Scheduler - Pharmaceutical filling line scheduler.

    Plan optimal schedules for filling line operations with multiple strategies,
    constraint validation, and comprehensive reporting.

    Examples:

        \b
        # Schedule with default configuration
        fillscheduler schedule --data lots.csv

        \b
        # Compare multiple strategies
        fillscheduler compare --data lots.csv --strategies smart-pack spt-pack lpt-pack

        \b
        # Export default configuration
        fillscheduler config export --output config.yaml

    For more information, visit: https://github.com/vikas-py/filling_scheduler
    """
    # Ensure ctx.obj exists for sharing data between commands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config

    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")
        if config:
            console.print(f"[dim]Using config file: {config}[/dim]")


# Register subcommands
cli.add_command(schedule)
cli.add_command(compare)
cli.add_command(config)


def main():
    """Entry point for the CLI."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
