"""Schedule command for generating filling schedules."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from fillscheduler.config import AppConfig
from fillscheduler.config_loader import load_config_with_overrides
from fillscheduler.io_utils import (
    read_lots_with_pandas,
    write_schedule_with_pandas,
    write_summary_txt,
)
from fillscheduler.reporting import write_html_report
from fillscheduler.scheduler import plan_schedule
from fillscheduler.validate import validate_input_lots, validate_schedule

console = Console()


@click.command()
@click.option(
    "-d",
    "--data",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to lots CSV file",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=False, path_type=Path),
    help="Output directory for results",
)
@click.option(
    "-s",
    "--strategy",
    type=click.Choice(
        ["smart-pack", "spt-pack", "lpt-pack", "cfs-pack", "hybrid-pack", "milp-opt"],
        case_sensitive=False,
    ),
    help="Scheduling strategy to use",
)
@click.option(
    "--start-time",
    type=str,
    help="Schedule start time (format: YYYY-MM-DD HH:MM)",
)
@click.option(
    "--no-validation",
    is_flag=True,
    help="Skip validation checks (not recommended)",
)
@click.option(
    "--no-report",
    is_flag=True,
    help="Skip HTML report generation",
)
@click.pass_context
def schedule(
    ctx,
    data: Path | None,
    output: Path | None,
    strategy: str | None,
    start_time: str | None,
    no_validation: bool,
    no_report: bool,
):
    """
    Generate a filling schedule for the given lots.

    Reads lot data from a CSV file, applies scheduling constraints,
    and generates a schedule using the specified strategy.

    Examples:

        \b
        # Basic usage with default configuration
        fillscheduler schedule --data lots.csv

        \b
        # Use specific strategy
        fillscheduler schedule --data lots.csv --strategy lpt-pack

        \b
        # Custom output directory and start time
        fillscheduler schedule --data lots.csv --output results/ --start-time "2025-01-15 08:00"

        \b
        # Use configuration file
        fillscheduler --config config.yaml schedule
    """
    verbose = ctx.obj.get("verbose", False)
    config_file = ctx.obj.get("config")

    try:
        # Load configuration
        if config_file:
            if verbose:
                console.print(f"[dim]Loading configuration from {config_file}[/dim]")

            # Build overrides from command-line options
            overrides = {}
            if data:
                overrides["DATA_PATH"] = data
            if output:
                overrides["OUTPUT_DIR"] = output
            if strategy:
                overrides["STRATEGY"] = strategy
            if start_time:
                overrides["START_TIME_STR"] = start_time

            cfg = load_config_with_overrides(config_file, **overrides)
        else:
            # Use AppConfig with command-line overrides
            cfg_kwargs = {}
            if data:
                cfg_kwargs["DATA_PATH"] = data
            if output:
                cfg_kwargs["OUTPUT_DIR"] = output
            if strategy:
                cfg_kwargs["STRATEGY"] = strategy
            if start_time:
                cfg_kwargs["START_TIME_STR"] = start_time

            cfg = AppConfig(**cfg_kwargs)

        # Validate paths
        if not cfg.DATA_PATH.exists():
            console.print(f"[bold red]Error:[/bold red] CSV file not found: {cfg.DATA_PATH}")
            raise click.Abort()

        # Create output directory
        cfg.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Parse start time
        try:
            start_dt = datetime.strptime(cfg.START_TIME_STR, "%Y-%m-%d %H:%M")
        except ValueError as e:
            console.print(
                f"[bold red]Error:[/bold red] Invalid start time format. "
                f"Use 'YYYY-MM-DD HH:MM'. Got: {cfg.START_TIME_STR}"
            )
            raise click.Abort() from e

        # Show configuration summary
        if verbose:
            _print_config_summary(cfg)

        # Load lots with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Loading lots from CSV...", total=None)
            lots = read_lots_with_pandas(cfg.DATA_PATH, cfg)

        console.print(f"[green]✓[/green] Loaded {len(lots)} lots")

        # Validate input lots
        if not no_validation:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Validating input lots...", total=None)
                errors, warnings = validate_input_lots(
                    lots, cfg, fail_fast=False, raise_exceptions=False
                )

            if errors:
                console.print(
                    f"[bold red]✗ Validation failed with {len(errors)} error(s):[/bold red]"
                )
                for error in errors:
                    console.print(f"  • {error}")
                raise click.Abort()

            if warnings:
                console.print(f"[yellow]⚠ {len(warnings)} warning(s):[/yellow]")
                for warning in warnings:
                    console.print(f"  • {warning}")

            console.print("[green]✓[/green] Input validation passed")

        # Generate schedule
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(f"Planning schedule using {cfg.STRATEGY} strategy...", total=None)
            activities, makespan_hours, kpis = plan_schedule(
                lots=lots, start_time=start_dt, cfg=cfg, strategy=cfg.STRATEGY
            )

        console.print(f"[green]✓[/green] Schedule generated in {makespan_hours:.2f} hours")

        # Validate output schedule
        if not no_validation:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Validating schedule...", total=None)
                errors, warnings = validate_schedule(
                    activities, cfg, fail_fast=False, raise_exceptions=False
                )

            if errors:
                console.print(
                    f"[bold red]✗ Schedule validation failed with {len(errors)} error(s):[/bold red]"
                )
                for error in errors:
                    console.print(f"  • {error}")
                raise click.Abort()

            if warnings:
                console.print(f"[yellow]⚠ {len(warnings)} warning(s):[/yellow]")
                for warning in warnings:
                    console.print(f"  • {warning}")

            console.print("[green]✓[/green] Schedule validation passed")

        # Write outputs
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Writing outputs...", total=None)

            schedule_csv = cfg.OUTPUT_DIR / "schedule.csv"
            write_schedule_with_pandas(activities, schedule_csv, cfg)

            summary_txt = cfg.OUTPUT_DIR / "summary.txt"
            write_summary_txt(kpis, [], [], summary_txt)

            if not no_report:
                report_html = cfg.OUTPUT_DIR / "report.html"
                write_html_report(
                    activities=activities,
                    kpis=kpis,
                    errors=[],
                    warnings=[],
                    path=report_html,
                    cfg=cfg,
                )

        # Print success summary
        console.print("\n[bold green]✓ Schedule completed successfully![/bold green]")
        _print_kpi_table(kpis, makespan_hours)

        console.print("\n[bold]Output files:[/bold]")
        console.print(f"  • Schedule: {schedule_csv}")
        console.print(f"  • Summary:  {summary_txt}")
        if not no_report:
            console.print(f"  • Report:   {report_html}")

    except click.Abort:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        raise click.Abort() from e


def _print_config_summary(cfg: AppConfig):
    """Print configuration summary."""
    table = Table(title="Configuration", show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    table.add_row("Data Path", str(cfg.DATA_PATH))
    table.add_row("Output Directory", str(cfg.OUTPUT_DIR))
    table.add_row("Strategy", cfg.STRATEGY)
    table.add_row("Start Time", cfg.START_TIME_STR)
    table.add_row("Fill Rate", f"{cfg.FILL_RATE_VPH:,} vials/hour")
    table.add_row("Window Hours", f"{cfg.WINDOW_HOURS} hours")
    table.add_row("Clean Hours", f"{cfg.CLEAN_HOURS} hours")

    console.print(table)
    console.print()


def _print_kpi_table(kpis: dict, makespan_hours: float):
    """Print KPIs in a formatted table."""
    table = Table(title="Key Performance Indicators", box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="green")

    table.add_row("Makespan", f"{makespan_hours:.2f} hours")
    table.add_row("Lots Scheduled", str(kpis.get("Lots Scheduled", 0)))
    table.add_row("Fill Blocks", str(kpis.get("Fill Blocks", 0)))
    table.add_row("Changeovers", str(kpis.get("Changeovers", 0)))
    table.add_row("Type Changes", str(kpis.get("Type Changes", 0)))

    util = kpis.get("Utilization (%)", 0)
    table.add_row("Utilization", f"{util:.1f}%")

    console.print(table)
