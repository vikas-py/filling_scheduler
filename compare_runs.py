# replace filling_scheduler/compare_runs.py with this

from __future__ import annotations

import argparse
from pathlib import Path

from fillscheduler.compare import compare_multi_strategies
from fillscheduler.config import AppConfig


def parse_args():
    p = argparse.ArgumentParser(
        description="Build a single consolidated comparison report for given order and multiple strategies."
    )
    p.add_argument("--data", default=None, help="Path to lots CSV (default from config).")
    p.add_argument("--out", default=None, help="Output folder (default from config).")
    p.add_argument(
        "--strategies",
        nargs="+",
        default=["smart-pack", "spt-pack", "lpt_pack", "cfs_pack", "hybrid"],
        help="Strategies to compare (default: smart-pack spt-pack).",
    )
    return p.parse_args()


def main():
    args = parse_args()
    cfg = AppConfig()

    data_path = Path(args.data) if args.data else cfg.DATA_PATH
    outdir = Path(args.out) if args.out else cfg.OUTPUT_DIR

    print(f"Input CSV : {data_path}")
    print(f"Output dir: {outdir}")
    print(f"Strategies: {', '.join(args.strategies)}")

    kpis_csv, multi_html = compare_multi_strategies(
        data_path=data_path,
        outdir=outdir,
        cfg=cfg,
        strategies=args.strategies,
    )
    print("\nSaved consolidated outputs:")
    print(f" - KPIs CSV : {kpis_csv}")
    print(f" - HTML     : {multi_html}")


if __name__ == "__main__":
    main()
