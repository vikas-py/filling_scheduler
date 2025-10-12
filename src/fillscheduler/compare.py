# append to filling_scheduler/fillscheduler/compare.py

from __future__ import annotations
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime
import pandas as pd

from .config import AppConfig
from .io_utils import read_lots_with_pandas, write_schedule_with_pandas, activities_to_dataframe
from .validate import validate_input_lots, validate_schedule
from .scheduler import plan_schedule, plan_schedule_in_order

_ALL_KPI_KEYS = [
    "Makespan (h)",
    "Total Clean (h)",
    "Total Changeover (h)",
    "Total Fill (h)",
    "Lots Scheduled",
    "Clean Blocks",
]

def _kpi_float(s: str) -> float:
    try:
        return float(s)
    except Exception:
        return float("nan")

def _kpis_to_row(name: str, kpis: Dict[str, str]) -> Dict[str, str]:
    row = {"Run": name}
    for k in _ALL_KPI_KEYS:
        row[k] = kpis.get(k, "")
    return row

def _delta_to_given_df(given: Dict[str, str], other: Dict[str, str], label: str) -> pd.DataFrame:
    rows = []
    for k in _ALL_KPI_KEYS:
        g = given.get(k, "")
        o = other.get(k, "")
        if k.endswith("(h)"):
            d = _kpi_float(o) - _kpi_float(g)
            rows.append({"Metric": k, "Given": g, label: o, f"Delta ({label} - Given)": f"{d:.2f}"})
        else:
            rows.append({"Metric": k, "Given": g, label: o, f"Delta ({label} - Given)": ""})
    return pd.DataFrame(rows, columns=["Metric", "Given", label, f"Delta ({label} - Given)"])

def compare_multi_strategies(
    data_path: Path,
    outdir: Path,
    cfg: AppConfig,
    strategies: List[str],
) -> Tuple[Path, Path]:
    """
    Build a single consolidated report (HTML + CSV) for:
      - Given (CSV order) schedule
      - One optimized schedule per strategy in `strategies`
    Returns: (kpis_csv_path, multi_html_path)
    """
    outdir.mkdir(parents=True, exist_ok=True)

    # Load and validate once
    lots = read_lots_with_pandas(data_path, cfg)
    validate_input_lots(lots, cfg)

    start_dt = datetime.strptime(cfg.START_TIME_STR, "%Y-%m-%d %H:%M")

    # Given (CSV order)
    given_acts, _, given_kpis = plan_schedule_in_order(lots[:], start_dt, cfg)
    validate_schedule(given_acts, cfg)
    given_df = activities_to_dataframe(given_acts, cfg)

    # KPIs table (first row = Given)
    kpi_rows = [_kpis_to_row("Given (CSV Order)", given_kpis)]
    schedules_html_sections = []

    # HTML helpers
    css = """
    body { font-family: Arial, Helvetica, sans-serif; margin: 24px; }
    h1 { margin-bottom: 0; }
    h2 { margin-top: 28px; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0; }
    th, td { border: 1px solid #ddd; padding: 6px; font-size: 14px; }
    th { background: #f7f7f7; }
    details { margin: 10px 0; }
    summary { font-weight: 600; cursor: pointer; }
    .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    .note { color: #666; font-size: 13px; }
    """

    # Given schedule section
    given_section = f"""
    <details open>
      <summary>Given Schedule (CSV order)</summary>
      {given_df.to_html(index=False, escape=False)}
    </details>
    """

    schedules_html_sections.append(given_section)

    # Run each strategy
    per_strategy_deltas = []
    for strat in strategies:
        acts, _, kpis = plan_schedule(lots[:], start_dt, cfg, strategy=strat)
        validate_schedule(acts, cfg)
        df = activities_to_dataframe(acts, cfg)

        # Save schedules (optional single-file request doesn't forbid extra CSVs, but we keep everything in HTML)
        write_schedule_with_pandas(acts, outdir / f"optimized_schedule_{strat.replace('-','_')}.csv", cfg)

        # KPI row
        kpi_rows.append(_kpis_to_row(f"Optimized ({strat})", kpis))

        # Delta-to-given table for this strategy
        delta_df = _delta_to_given_df(given_kpis, kpis, f"Optimized ({strat})")
        per_strategy_deltas.append((strat, delta_df))

        # Add a collapsible schedule section
        schedules_html_sections.append(f"""
        <details>
          <summary>Optimized Schedule — {strat}</summary>
          {df.to_html(index=False, escape=False)}
        </details>
        """)

    # KPIs CSV for all runs
    kpis_df = pd.DataFrame(kpi_rows, columns=["Run"] + _ALL_KPI_KEYS)
    kpis_csv = outdir / "kpis_all_runs.csv"
    kpis_df.to_csv(kpis_csv, index=False)

    # Build consolidated HTML
    deltas_html = "\n".join(
        f"<h3>Delta to Given — {strat}</h3>\n{df.to_html(index=False, escape=False)}"
        for strat, df in per_strategy_deltas
    )
    schedules_html = "\n".join(schedules_html_sections)

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Consolidated Comparison Report</title>
<style>{css}</style></head>
<body>
  <h1>Consolidated Comparison</h1>
  <div class="note">Input: {data_path}</div>

  <h2>KPIs — All Runs</h2>
  {kpis_df.to_html(index=False, escape=False)}

  <h2>Delta to Given (per strategy)</h2>
  {deltas_html}

  <h2>Schedules</h2>
  {schedules_html}
</body></html>
"""
    multi_html = outdir / "comparison_all_in_one.html"
    multi_html.write_text(html, encoding="utf-8")

    return kpis_csv, multi_html
