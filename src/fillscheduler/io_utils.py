from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import AppConfig
from .models import Activity, Lot


def read_lots_with_pandas(path: Path, cfg: AppConfig) -> list[Lot]:
    df = pd.read_csv(path)

    required = {"Lot ID", "Type", "Vials"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    # Normalize text fields; ensure blanks not NaN
    df["Lot ID"] = df["Lot ID"].fillna("").astype(str).str.strip()
    df["Type"] = df["Type"].fillna("").astype(str).str.strip()

    # Vials: must be numeric and present
    if df["Vials"].isnull().any():
        raise ValueError("One or more lots have missing Vials values.")
    df["Vials"] = pd.to_numeric(df["Vials"], errors="raise")

    # Fill hours at configured rate
    df["fill_hours"] = df["Vials"] / cfg.FILL_RATE_VPH

    lots: list[Lot] = [
        Lot(row["Lot ID"], row["Type"], int(row["Vials"]), float(row["fill_hours"]))
        for _, row in df.iterrows()
    ]
    if not lots:
        raise ValueError("No lots found after reading CSV.")
    return lots


def activities_to_dataframe(activities: list[Activity], cfg: AppConfig) -> pd.DataFrame:
    rows = []
    for a in activities:
        hrs = (a.end - a.start).total_seconds() / 3600.0
        rows.append(
            {
                "Start": a.start.strftime(cfg.DATETIME_FMT),
                "End": a.end.strftime(cfg.DATETIME_FMT),
                "Hours": round(hrs, 2),
                "Activity": a.kind,
                "Lot ID": a.lot_id or "",
                "Type": a.lot_type or "",
                "Note": a.note or "",
            }
        )
    return pd.DataFrame(
        rows, columns=["Start", "End", "Hours", "Activity", "Lot ID", "Type", "Note"]
    )


def write_schedule_with_pandas(
    activities: list[Activity], path: Path, cfg: AppConfig | None = None
) -> None:
    cfg = cfg or AppConfig()
    df = activities_to_dataframe(activities, cfg)
    df.to_csv(path, index=False)


def write_summary_txt(kpis: dict, errors: list[str], warnings: list[str], path: Path) -> None:
    with path.open("w") as f:
        f.write("=== Schedule Summary ===\n")
        for k, v in kpis.items():
            f.write(f"{k}: {v}\n")
        if errors:
            f.write("\n=== Errors ===\n")
            for e in errors:
                f.write(f"- {e}\n")
        if warnings:
            f.write("\n=== Warnings ===\n")
            for w in warnings:
                f.write(f"- {w}\n")
