from __future__ import annotations
from collections import deque
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Deque

from .models import Activity, Lot
from .config import AppConfig
from .heuristics import (
    base_pool_order,
    changeover_hours,
    pick_next_that_fits,
    pick_next_scored_beam1,
)

def _sum_kind(activities: List[Activity], kind: str) -> float:
    return sum((a.end - a.start).total_seconds() for a in activities if a.kind == kind) / 3600.0

def _emit_block(activities: List[Activity],
                block_lots: List[Lot],
                block_start: datetime,
                cfg: AppConfig) -> datetime:
    """
    Given a sequence of lots for a block, emit CHANGEOVER + FILL activities starting at block_start.
    Returns the end timestamp after the block.
    """
    now = block_start
    prev_type: Optional[str] = None
    for i, lot in enumerate(block_lots):
        chg_h = changeover_hours(prev_type, lot.lot_type, cfg)
        if chg_h > 0.0:
            chg_start = now
            chg_end = chg_start + timedelta(hours=chg_h)
            activities.append(Activity(
                chg_start, chg_end, "CHANGEOVER",
                lot_type=f"{prev_type}->{lot.lot_type}", note=f"{int(chg_h)}h"
            ))
            now = chg_end

        fill_start = now
        fill_end = fill_start + timedelta(hours=lot.fill_hours)
        activities.append(Activity(
            fill_start, fill_end, "FILL",
            lot_id=lot.lot_id, lot_type=lot.lot_type, note=f"{lot.vials} vials"
        ))
        now = fill_end
        prev_type = lot.lot_type

    return now

def plan_schedule(
    lots: List[Lot],
    start_time: datetime,
    cfg: AppConfig,
    strategy: str = "smart-pack",
) -> Tuple[List[Activity], float, dict]:
    """
    Build schedule using chosen strategy.
    - "smart-pack": scored + short look-ahead packing inside each 120h window
    - "spt-pack"  : original heuristic
    Returns (activities, makespan_hours, kpis)
    """
    # We keep a candidate deque; selection chooses indices from it
    remaining: Deque[Lot] = deque(lots if strategy != "spt-pack" else base_pool_order(lots))

    activities: List[Activity] = []
    now = start_time

    # Start first CLEAN block
    clean_start = now
    clean_end = clean_start + timedelta(hours=cfg.CLEAN_HOURS)
    activities.append(Activity(clean_start, clean_end, "CLEAN", note="Block reset"))
    block_start = clean_end

    window_used = 0.0
    prev_type: Optional[str] = None
    block_lots: List[Lot] = []

    def close_and_start_new_block(current_end: datetime) -> None:
        nonlocal now, block_start, window_used, prev_type, block_lots
        # emit current block lots
        if block_lots:
            now = _emit_block(activities, block_lots, block_start, cfg)
            block_lots.clear()
        else:
            now = current_end  # nothing emitted; stay at current_end

        # start new CLEAN
        c_start = now
        c_end = c_start + timedelta(hours=cfg.CLEAN_HOURS)
        activities.append(Activity(c_start, c_end, "CLEAN", note="Block reset"))
        block_start = c_end
        window_used = 0.0
        prev_type = None

    while remaining:
        # pick next lot by strategy (must fit within window)
        if strategy == "smart-pack":
            pick_idx = pick_next_scored_beam1(remaining, prev_type, window_used, cfg)
        else:
            pick_idx = pick_next_that_fits(remaining, prev_type, window_used, cfg)

        if pick_idx is None:
            # No more lots fit in this 120h window: close block and start a new one
            close_and_start_new_block(block_start)
            continue

        # rotate deque to bring chosen to front
        for _ in range(pick_idx):
            remaining.append(remaining.popleft())
        lot = remaining.popleft()

        # compute hours needed if we add this lot now
        chg_h = changeover_hours(prev_type, lot.lot_type, cfg)
        need = chg_h + lot.fill_hours

        # defensive: if it doesn't fit, force close/start new block and retry
        if window_used + need > cfg.WINDOW_HOURS + 1e-9:
            close_and_start_new_block(block_start)
            # put lot back to consider in new block
            remaining.appendleft(lot)
            continue

        # accept lot into the current block sequence
        block_lots.append(lot)
        window_used += need
        prev_type = lot.lot_type

    # Flush the final block
    if block_lots:
        now = _emit_block(activities, block_lots, block_start, cfg)

    # KPIs
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
    lots_in_order: List[Lot],
    start_time: datetime,
    cfg: AppConfig,
) -> Tuple[List[Activity], float, dict]:
    """
    Build a schedule strictly following CSV order.
    Respects the 120h window (starts a new CLEAN if next lot doesn't fit).
    """
    activities: List[Activity] = []
    now = start_time

    clean_start = now
    clean_end = clean_start + timedelta(hours=cfg.CLEAN_HOURS)
    activities.append(Activity(clean_start, clean_end, "CLEAN", note="Block reset"))
    block_start = clean_end

    window_used = 0.0
    prev_type: Optional[str] = None
    block_lots: List[Lot] = []

    def close_and_start_new_block(current_end: datetime) -> None:
        nonlocal now, block_start, window_used, prev_type, block_lots
        if block_lots:
            now = _emit_block(activities, block_lots, block_start, cfg)
            block_lots.clear()
        else:
            now = current_end
        c_start = now
        c_end = c_start + timedelta(hours=cfg.CLEAN_HOURS)
        activities.append(Activity(c_start, c_end, "CLEAN", note="Block reset"))
        block_start = c_end
        window_used = 0.0
        prev_type = None

    for lot in lots_in_order:
        chg_h = changeover_hours(prev_type, lot.lot_type, cfg)
        need = chg_h + lot.fill_hours
        if window_used + need > cfg.WINDOW_HOURS + 1e-9:
            close_and_start_new_block(block_start)
            chg_h = 0.0  # first in new block
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
