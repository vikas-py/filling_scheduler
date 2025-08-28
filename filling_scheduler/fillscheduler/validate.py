# fillscheduler/validate.py
from __future__ import annotations
from typing import List, Tuple, Optional
from .models import Activity
from .config import AppConfig

def validate_schedule(activities: List[Activity], cfg: AppConfig) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    window_sum = 0.0
    in_block = False

    for a in activities:
        if a.kind == "CLEAN":
            if in_block and window_sum > cfg.WINDOW_HOURS + 1e-6:
                errors.append(f"Window overrun: {window_sum:.2f}h > {cfg.WINDOW_HOURS}h")
            window_sum = 0.0
            in_block = True
        else:
            dur_h = (a.end - a.start).total_seconds() / 3600.0
            window_sum += dur_h

            # strict check: no lot longer than 120h
            if a.kind == "FILL" and dur_h > cfg.WINDOW_HOURS + 1e-6:
                errors.append(
                    f"Lot {a.lot_id} ({dur_h:.2f}h) exceeds {cfg.WINDOW_HOURS}h limit – cannot be scheduled."
                )

    if in_block and window_sum > cfg.WINDOW_HOURS + 1e-6:
        errors.append(f"Window overrun: {window_sum:.2f}h > {cfg.WINDOW_HOURS}h")

    # no lot should appear more than once
    seen = set()
    for a in activities:
        if a.kind == "FILL" and a.lot_id:
            if a.lot_id in seen:
                errors.append(f"Lot split detected: {a.lot_id}")
            seen.add(a.lot_id)

    return errors, warnings
