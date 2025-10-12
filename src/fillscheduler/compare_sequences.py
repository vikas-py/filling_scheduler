# filling_scheduler/compare_sequences.py
from __future__ import annotations

import argparse
from pathlib import Path

from fillscheduler.compare import compare_sequence_vs_optimized  # type: ignore[attr-defined]
from fillscheduler.config import AppConfig


def parse_args():
    p = argparse.ArgumentParser(description="Compare given sequence vs optimized schedule.")
    p.add_argument("--seq", required=True, help="Path to sequence CSV (column 'Lot ID').")
    p.add_argument("--data", default=None, help="Path to lots CSV (default from config).")
    p.add_argument("--out", default=None, help="Output folder (default from config).")
    return p.parse_args()


def main():
    args = parse_args()
    cfg = AppConfig()
    data_path = Path(args.data) if args.data else cfg.DATA_PATH
    outdir = Path(args.out) if args.out else cfg.OUTPUT_DIR
    seq_path = Path(args.seq)

    given_csv, opt_csv, cmp_csv, cmp_html = compare_sequence_vs_optimized(
        data_path=data_path,
        sequence_path=seq_path,
        outdir=outdir,
        cfg=cfg,
    )
    print("Saved:")
    print(f" - Given schedule:     {given_csv}")
    print(f" - Optimized schedule: {opt_csv}")
    print(f" - KPI comparison:     {cmp_csv}")
    print(f" - HTML comparison:    {cmp_html}")


if __name__ == "__main__":
    main()
