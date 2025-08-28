# fillscheduler/reporting.py
from __future__ import annotations
from pathlib import Path

def print_summary(kpis: dict, errors: list[str], warnings: list[str],
                  schedule_csv: Path, summary_txt: Path) -> None:
    print("\n=== Schedule KPIs ===")
    for k, v in kpis.items():
        print(f"{k}: {v}")

    if errors:
        print("\n=== ERRORS ===")
        for e in errors:
            print(f"- {e}")
    if warnings:
        print("\n=== WARNINGS ===")
        for w in warnings:
            print(f"- {w}")

    print(f"\nSaved schedule to: {schedule_csv}")
    print(f"Saved summary to : {summary_txt}")
