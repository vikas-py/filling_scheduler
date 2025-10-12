# tests/test_schedule_validation.py
from datetime import datetime, timedelta

from fillscheduler.config import AppConfig
from fillscheduler.models import Activity
from fillscheduler.validate import validate_schedule


def h(hours: float):
    return timedelta(hours=hours)


def test_window_overrun_error(cfg: AppConfig):
    # Build a schedule where FILL+CHANGEOVER within a block exceeds WINDOW_HOURS
    start = datetime(2025, 1, 1, 8, 0, 0)
    acts = []
    # Clean block
    acts.append(Activity(start, start + h(cfg.CLEAN_HOURS), "CLEAN", note="Block reset"))

    # Stuff the window with exactly the limit, then add 1 minute overflow
    block_start = acts[-1].end
    # First fill: WINDOW_HOURS - 0.1 h
    a1_start = block_start
    a1_end = a1_start + h(cfg.WINDOW_HOURS - 0.1)
    acts.append(Activity(a1_start, a1_end, "FILL", lot_id="L1", lot_type="T", note=""))

    # Add 0.2 h changeover → overrun (total = WINDOW_HOURS + 0.1)
    chg_start = a1_end
    chg_end = chg_start + h(0.2)
    acts.append(Activity(chg_start, chg_end, "CHANGEOVER", lot_type="T->T", note=""))

    errors, warnings = validate_schedule(acts, cfg, fail_fast=False)
    assert any("Window overrun" in e for e in errors)


def test_single_fill_longer_than_window_error(cfg: AppConfig):
    start = datetime(2025, 1, 1, 8, 0, 0)
    acts = []
    acts.append(Activity(start, start + h(cfg.CLEAN_HOURS), "CLEAN", note="Block reset"))
    a1_start = acts[-1].end
    a1_end = a1_start + h(cfg.WINDOW_HOURS + 0.5)  # too long
    acts.append(Activity(a1_start, a1_end, "FILL", lot_id="BIG", lot_type="T", note=""))

    errors, warnings = validate_schedule(acts, cfg, fail_fast=False)
    assert any("exceeds 120 h limit" in e or "exceeds" in e for e in errors)


def test_lot_split_error(cfg: AppConfig):
    start = datetime(2025, 1, 1, 8, 0, 0)
    acts = []
    acts.append(Activity(start, start + h(cfg.CLEAN_HOURS), "CLEAN", note="Block reset"))
    a1_start = acts[-1].end
    # Two fills with same Lot ID "A1"
    acts.append(Activity(a1_start, a1_start + h(1.0), "FILL", lot_id="A1", lot_type="T", note=""))
    acts.append(
        Activity(a1_start + h(1.0), a1_start + h(2.0), "FILL", lot_id="A1", lot_type="T", note="")
    )

    errors, warnings = validate_schedule(acts, cfg, fail_fast=False)
    assert any("Lot split detected: A1" in e for e in errors)
