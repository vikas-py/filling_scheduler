# fillscheduler/rules.py
from __future__ import annotations

from .config import AppConfig


def changeover_hours(prev_type: str | None, next_type: str, cfg: AppConfig) -> float:
    """Changeover hours given previous and next lot types."""
    if prev_type is None:
        return 0.0  # first lot after CLEAN has no changeover
    return cfg.CHG_SAME_HOURS if prev_type == next_type else cfg.CHG_DIFF_HOURS
