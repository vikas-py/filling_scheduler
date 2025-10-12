# fillscheduler/scheduler.py
from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta

from .config import AppConfig
from .models import Activity, Lot
from .rules import changeover_hours
from .strategies import get_strategy  # NEW


def _sum_kind(activities: list[Activity], kind: str) -> float:
    return sum((a.end - a.start).total_seconds() for a in activities if a.kind == kind) / 3600.0


def _emit_block(
    activities: list[Activity], block_lots: list[Lot], block_start: datetime, cfg: AppConfig
) -> datetime:
    now = block_start
    prev_type: str | None = None
    for lot in block_lots:
        chg_h = changeover_hours(prev_type, lot.lot_type, cfg)
        if chg_h > 0.0:
            chg_start = now
            chg_end = chg_start + timedelta(hours=chg_h)
            activities.append(
                Activity(
                    chg_start,
                    chg_end,
                    "CHANGEOVER",
                    lot_type=f"{prev_type}->{lot.lot_type}",
                    note=f"{int(chg_h)}h",
                )
            )
            now = chg_end
        fill_start = now
        fill_end = fill_start + timedelta(hours=lot.fill_hours)
        activities.append(
            Activity(
                fill_start,
                fill_end,
                "FILL",
                lot_id=lot.lot_id,
                lot_type=lot.lot_type,
                note=f"{lot.vials} vials",
            )
        )
        now = fill_end
        prev_type = lot.lot_type
    return now


def plan_schedule(
    lots: list[Lot], start_time: datetime, cfg: AppConfig, strategy: str = "smart-pack"
) -> tuple[list[Activity], float, dict]:
    strat = get_strategy(strategy)
    remaining: deque[Lot] = strat.preorder(lots, cfg)

    activities: list[Activity] = []
    now = start_time

    # Start first CLEAN
    c_start = now
    c_end = c_start + timedelta(hours=cfg.CLEAN_HOURS)
    activities.append(Activity(c_start, c_end, "CLEAN", note="Block reset"))
    block_start = c_end

    window_used = 0.0
    prev_type: str | None = None
    block_lots: list[Lot] = []

    def close_and_start_new_block():
        nonlocal now, block_start, window_used, prev_type, block_lots
        if block_lots:
            now = _emit_block(activities, block_lots, block_start, cfg)
            block_lots.clear()
        else:
            now = block_start
        cs = now
        ce = cs + timedelta(hours=cfg.CLEAN_HOURS)
        activities.append(Activity(cs, ce, "CLEAN", note="Block reset"))
        block_start = ce
        window_used = 0.0
        prev_type = None

    while remaining:
        pick_idx = strat.pick_next(remaining, prev_type, window_used, cfg)
        if pick_idx is None:
            close_and_start_new_block()
            continue

        # rotate chosen to front
        for _ in range(pick_idx):
            remaining.append(remaining.popleft())
        lot = remaining.popleft()

        chg_h = changeover_hours(prev_type, lot.lot_type, cfg)
        need = chg_h + lot.fill_hours
        if window_used + need > cfg.WINDOW_HOURS + 1e-9:
            # shouldn't happen if strategy respects fit, but guard anyway
            close_and_start_new_block()
            remaining.appendleft(lot)
            continue

        block_lots.append(lot)
        window_used += need
        prev_type = lot.lot_type

    if block_lots:
        now = _emit_block(activities, block_lots, block_start, cfg)

    makespan_hours = (activities[-1].end - activities[0].start).total_seconds() / 3600.0
    total_clean = _sum_kind(activities, "CLEAN")
    total_chg = _sum_kind(activities, "CHANGEOVER")
    total_fill = _sum_kind(activities, "FILL")
    kpis = {
        "Makespan (h)": f"{makespan_hours:.2f}",
        "Total Clean (h)": f"{total_clean:.2f}",
        "Total Changeover (h)": f"{total_chg:.2f}",
        "Total Fill (h)": f"{total_fill:.2f}",
        "Lots Scheduled": f"{sum(1 for a in activities if a.kind=='FILL')}",
        "Clean Blocks": f"{sum(1 for a in activities if a.kind=='CLEAN')}",
    }
    return activities, makespan_hours, kpis


def plan_schedule_in_order(
    lots_in_order: list[Lot], start_time: datetime, cfg: AppConfig
) -> tuple[list[Activity], float, dict]:
    activities: list[Activity] = []
    now = start_time

    c_start = now
    c_end = c_start + timedelta(hours=cfg.CLEAN_HOURS)
    activities.append(Activity(c_start, c_end, "CLEAN", note="Block reset"))
    block_start = c_end

    window_used = 0.0
    prev_type: str | None = None
    block_lots: list[Lot] = []

    def close_and_start_new_block():
        nonlocal now, block_start, window_used, prev_type, block_lots
        if block_lots:
            now = _emit_block(activities, block_lots, block_start, cfg)
            block_lots.clear()
        else:
            now = block_start
        cs = now
        ce = cs + timedelta(hours=cfg.CLEAN_HOURS)
        activities.append(Activity(cs, ce, "CLEAN", note="Block reset"))
        block_start = ce
        window_used = 0.0
        prev_type = None

    for lot in lots_in_order:
        chg_h = changeover_hours(prev_type, lot.lot_type, cfg)
        need = chg_h + lot.fill_hours
        if window_used + need > cfg.WINDOW_HOURS + 1e-9:
            close_and_start_new_block()
            chg_h = 0.0
            need = lot.fill_hours
        block_lots.append(lot)
        window_used += need
        prev_type = lot.lot_type

    if block_lots:
        now = _emit_block(activities, block_lots, block_start, cfg)

    makespan_hours = (activities[-1].end - activities[0].start).total_seconds() / 3600.0
    total_clean = _sum_kind(activities, "CLEAN")
    total_chg = _sum_kind(activities, "CHANGEOVER")
    total_fill = _sum_kind(activities, "FILL")
    kpis = {
        "Makespan (h)": f"{makespan_hours:.2f}",
        "Total Clean (h)": f"{total_clean:.2f}",
        "Total Changeover (h)": f"{total_chg:.2f}",
        "Total Fill (h)": f"{total_fill:.2f}",
        "Lots Scheduled": f"{sum(1 for a in activities if a.kind=='FILL')}",
        "Clean Blocks": f"{sum(1 for a in activities if a.kind=='CLEAN')}",
    }
    return activities, makespan_hours, kpis
