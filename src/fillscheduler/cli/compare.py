"""Compare command for multi-strategy comparison."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from fillscheduler.compare import compare_multi_strategies
from fillscheduler.config import AppConfig
from fillscheduler.config_loader import load_config_with_overrides

console = Console()

ALL_STRATEGIES = ["smart-pack", "spt-pack", "lpt-pack", "cfs-pack", "hybrid-pack", "milp-opt"]


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
    help="Output directory for comparison results",
)
@click.option(
    "-s",
    "--strategies",
    multiple=True,
    type=click.Choice(ALL_STRATEGIES, case_sensitive=False),
    help="Strategies to compare (can be specified multiple times)",
)
@click.option(
    "--all-strategies",
    is_flag=True,
    help="Compare all available strategies",
)
@click.option(
    "--sort-by",
    type=click.Choice(["makespan", "utilization", "changeovers"], case_sensitive=False),
    default="makespan",
    help="Sort comparison results by this metric",
)
@click.pass_context
def compare(
    ctx,
    data: Path | None,
    output: Path | None,
    strategies: tuple[str, ...],
    all_strategies: bool,
    sort_by: str,
):
    """
    Compare multiple scheduling strategies side-by-side.

    Generates schedules using different strategies and produces a
    comprehensive comparison report with KPIs and visualizations.

    Examples:

        \b
        # Compare specific strategies
        fillscheduler compare --data lots.csv --strategies smart-pack spt-pack lpt-pack

        \b
        # Compare all strategies
        fillscheduler compare --data lots.csv --all-strategies

        \b
        # Custom output and sorting
        fillscheduler compare --data lots.csv --strategies smart-pack milp-opt --sort-by utilization

        \b
        # Use configuration file
        fillscheduler --config config.yaml compare --all-strategies
    """
    verbose = ctx.obj.get("verbose", False)
    config_file = ctx.obj.get("config")

    try:
        # Determine which strategies to compare
        if all_strategies:
            strategy_list = list(ALL_STRATEGIES)
        elif strategies:
            strategy_list = list(strategies)
        else:
            # Default strategies
            strategy_list = ["smart-pack", "spt-pack", "lpt-pack"]

        console.print(f"[bold]Comparing {len(strategy_list)} strategies:[/bold]")
        for s in strategy_list:
            console.print(f"  • {s}")
        console.print()

        # Load configuration
        if config_file:
            if verbose:
                console.print(f"[dim]Loading configuration from {config_file}[/dim]")

            overrides = {}
            if data:
                overrides["DATA_PATH"] = data
            if output:
                overrides["OUTPUT_DIR"] = output

            cfg = load_config_with_overrides(config_file, **overrides)
        else:
            cfg_kwargs = {}
            if data:
                cfg_kwargs["DATA_PATH"] = data
            if output:
                cfg_kwargs["OUTPUT_DIR"] = output

            cfg = AppConfig(**cfg_kwargs)

        # Validate paths
        if not cfg.DATA_PATH.exists():
            console.print(f"[bold red]Error:[/bold red] CSV file not found: {cfg.DATA_PATH}")
            raise click.Abort()

        # Create output directory
        output_dir = cfg.OUTPUT_DIR / "comparison"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run comparison with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("Running comparisons...", total=len(strategy_list))

            # Note: compare_multi_strategies doesn't provide progress callbacks
            # For now, we'll just show a spinner
            results = compare_multi_strategies(
                data_path=cfg.DATA_PATH,
                output_dir=output_dir,
                strategies=strategy_list,
                cfg=cfg,
            )
            progress.update(task, completed=len(strategy_list))

        console.print(
            f"\n[green]✓[/green] Comparison completed for {len(strategy_list)} strategies"
        )

        # Display comparison table
        _print_comparison_table(results, sort_by)

        # Show output files
        console.print("\n[bold]Output files:[/bold]")
        console.print(f"  • Comparison report: {output_dir / 'comparison_report.html'}")
        console.print(f"  • CSV results: {output_dir}")

    except click.Abort:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        raise click.Abort() from e


def _print_comparison_table(results: dict, sort_by: str):
    """Print comparison results in a formatted table."""
    table = Table(title="Strategy Comparison", box=None)
    table.add_column("Strategy", style="cyan")
    table.add_column("Makespan (h)", justify="right")
    table.add_column("Utilization (%)", justify="right")
    table.add_column("Changeovers", justify="right")
    table.add_column("Type Changes", justify="right")

    # Sort results
    sorted_results = sorted(
        results.items(),
        key=lambda x: _get_sort_key(x[1], sort_by),
    )

    for strategy, data in sorted_results:
        kpis = data.get("kpis", {})
        makespan = data.get("makespan_hours", 0)
        util = kpis.get("Utilization (%)", 0)
        changeovers = kpis.get("Changeovers", 0)
        type_changes = kpis.get("Type Changes", 0)

        # Highlight best value in each column
        makespan_style = (
            "green"
            if makespan == min(r[1].get("makespan_hours", 999) for r in results.items())
            else ""
        )
        util_style = (
            "green"
            if util == max(r[1].get("kpis", {}).get("Utilization (%)", 0) for r in results.items())
            else ""
        )

        table.add_row(
            strategy,
            (
                f"[{makespan_style}]{makespan:.2f}[/{makespan_style}]"
                if makespan_style
                else f"{makespan:.2f}"
            ),
            f"[{util_style}]{util:.1f}[/{util_style}]" if util_style else f"{util:.1f}",
            str(changeovers),
            str(type_changes),
        )

    console.print(table)


def _get_sort_key(data: dict, sort_by: str):
    """Get sort key based on sort_by parameter."""
    if sort_by == "makespan":
        return data.get("makespan_hours", 999)
    elif sort_by == "utilization":
        return -data.get("kpis", {}).get("Utilization (%)", 0)  # Negative for descending
    elif sort_by == "changeovers":
        return data.get("kpis", {}).get("Changeovers", 999)
    return 0
    cfg = AppConfig()
