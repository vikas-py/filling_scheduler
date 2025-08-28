from __future__ import annotations
from pathlib import Path
import pandas as pd
from typing import Tuple
from datetime import datetime

from .config import AppConfig
from .io_utils import read_lots_with_pandas, write_schedule_with_pandas, activities_to_dataframe
from .validate import validate_input_lots, validate_schedule
from .scheduler import plan_schedule, plan_schedule_in_order

def _kpi_float(s: str) -> float:
    try:
        return float(s)
    except Exception:
        return float("nan")

def _kpi_delta(kpis_given: dict, kpis_opt: dict) -> pd.DataFrame:
    keys = [
        "Makespan (h)",
        "Total Clean (h)",
        "Total Changeover (h)",
        "Total Fill (h)",
        "Lots Scheduled",
        "Clean Blocks",
    ]
    rows = []
    for k in keys:
        a = kpis_given.get(k, "")
        b = kpis_opt.get(k, "")
        if k.endswith("(h)"):
            a_f, b_f = _kpi_float(a), _kpi_float(b)
            d = b_f - a_f
            rows.append({"Metric": k, "Given-Order": a, "Optimized": b, "Delta (Opt - Given)": f"{d:.2f}"})
        else:
            rows.append({"Metric": k, "Given-Order": a, "Optimized": b, "Delta (Opt - Given)": ""})
    return pd.DataFrame(rows, columns=["Metric", "Given-Order", "Optimized", "Delta (Opt - Given)"])

def compare_input_order_vs_optimized(
    data_path: Path,
    outdir: Path,
    cfg: AppConfig,
) -> Tuple[Path, Path, Path, Path]:
    """
    Compare schedules using the SAME input CSV:
      - Given order: rows as-is from the CSV (no reordering)
      - Optimized: heuristic reordering (cfg.STRATEGY)
    Writes:
      - given_schedule.csv
      - optimized_schedule.csv
      - comparison.csv
      - comparison.html
    Returns the 4 paths.
    """
    outdir.mkdir(parents=True, exist_ok=True)

    # Load once and validate strictly
    lots = read_lots_with_pandas(data_path, cfg)
    validate_input_lots(lots, cfg)  # fail-fast on input errors

    start_dt = datetime.strptime(cfg.START_TIME_STR, "%Y-%m-%d %H:%M")

    # Given-order plan (CSV order)
    given_acts, _, given_kpis = plan_schedule_in_order(lots[:], start_dt, cfg)
    validate_schedule(given_acts, cfg)

    # Optimized plan (heuristic)
    opt_acts, _, opt_kpis = plan_schedule(lots, start_dt, cfg, strategy=cfg.STRATEGY)
    validate_schedule(opt_acts, cfg)

    # Write schedules
    given_csv = outdir / "given_schedule.csv"
    opt_csv = outdir / "optimized_schedule.csv"
    write_schedule_with_pandas(given_acts, given_csv, cfg)
    write_schedule_with_pandas(opt_acts, opt_csv, cfg)

    # KPI comparison table
    cmp_df = _kpi_delta(given_kpis, opt_kpis)
    cmp_csv = outdir / "comparison.csv"
    cmp_df.to_csv(cmp_csv, index=False)

    # HTML comparison (side-by-side)
    given_df = activities_to_dataframe(given_acts, cfg)
    opt_df = activities_to_dataframe(opt_acts, cfg)
    css = """
    body { font-family: Arial, Helvetica, sans-serif; margin: 24px; }
    h1 { margin-bottom: 0; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0; }
    th, td { border: 1px solid #ddd; padding: 6px; font-size: 14px; }
    th { background: #f7f7f7; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    """
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Comparison Report</title>
<style>{css}</style></head>
<body>
<h1>Input Order vs Optimized</h1>

<h2>KPIs</h2>
{cmp_df.to_html(index=False, escape=False)}

<div class="grid">
  <div>
    <h2>Given (CSV Order) Schedule</h2>
    {given_df.to_html(index=False, escape=False)}
  </div>
  <div>
    <h2>Optimized Schedule</h2>
    {opt_df.to_html(index=False, escape=False)}
  </div>
</div>
</body></html>"""
    cmp_html = outdir / "comparison.html"
    cmp_html.write_text(html, encoding="utf-8")

    return given_csv, opt_csv, cmp_csv, cmp_html
