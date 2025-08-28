# main.py
from __future__ import annotations
from datetime import datetime
from pathlib import Path

from fillscheduler.config import AppConfig
from fillscheduler.io_utils import (
    read_lots_with_pandas,
    write_schedule_with_pandas,
    write_summary_txt,
)
from fillscheduler.scheduler import plan_schedule
from fillscheduler.validate import validate_schedule
from fillscheduler.reporting import print_summary

def main():
    cfg = AppConfig()

    # Optionally ask for paths if INTERACTIVE is True
    data_path = cfg.DATA_PATH
    if cfg.INTERACTIVE:
        val = input(f"Path to Lots CSV [{data_path}]: ").strip()
        if val:
            data_path = Path(val)

    if not data_path.exists():
        raise SystemExit(f"CSV not found: {data_path}")

    outdir = cfg.OUTPUT_DIR
    outdir.mkdir(parents=True, exist_ok=True)

    try:
        start_dt = datetime.strptime(cfg.START_TIME_STR, "%Y-%m-%d %H:%M")
    except ValueError:
        raise SystemExit("Invalid START_TIME_STR in config. Use 'YYYY-MM-DD HH:MM'.")

    # 1) Load lots
    lots = read_lots_with_pandas(data_path, cfg)

    # 2) Plan schedule
    activities, makespan_hours, kpis = plan_schedule(
        lots=lots, start_time=start_dt, cfg=cfg, strategy=cfg.STRATEGY
    )

    # 3) Validate
    errors, warnings = validate_schedule(activities, cfg)

    # 4) Write outputs
    schedule_csv = outdir / "schedule.csv"
    write_schedule_with_pandas(activities, schedule_csv)

    summary_txt = outdir / "summary.txt"
    write_summary_txt(kpis, errors, warnings, summary_txt)

    # 5) Console recap
    print_summary(kpis, errors, warnings, schedule_csv, summary_txt)

if __name__ == "__main__":
    main()
