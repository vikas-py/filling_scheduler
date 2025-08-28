from __future__ import annotations
from collections import deque
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

from .models import Activity, Lot
from .config import AppConfig
from .heuristics import base_pool_order, changeover_hours, pick_next_that_fits

def plan_schedule(
    lots: List[Lot],
    start_time: datetime,
    cfg: AppConfig,
    strategy: str = "spt-pack",
) -> Tuple[List[Activity], float, dict]:
    """
    Returns (activities, makespan_hours, kpis)
    """
    pool = base_pool_order(lots)
    remaining = deque(pool)

    activities: List[Activity] = []
    now = start_time

    def start_clean_block(current_time: datetime) -> tuple[datetime, Optional[str]]:
        clean_start = current_time
        try:
            clean_end = clean_start + timedelta(hours=cfg.CLEAN_HOURS)
        except OverflowError as e:
            raise ValueError(
                f"Cannot start clean block at {clean_start}: adding {cfg.CLEAN_HOURS}h exceeds datetime range."
            ) from e
        activities.append(Activity(clean_start, clean_end, "CLEAN", note="Block reset"))
        return clean_end, None

    now, prev_type = start_clean_block(now)
    window_used = 0.0

    while remaining:
        pick_idx = pick_next_that_fits(remaining, prev_type, window_used, cfg)
        if pick_idx is None:
            now, prev_type = start_clean_block(now)
            window_used = 0.0
            continue

        # rotate to bring chosen to front
        for _ in range(pick_idx):
            remaining.append(remaining.popleft())
        lot = remaining.popleft()

        # changeover (if not first after clean)
        chg_h = changeover_hours(prev_type, lot.lot_type, cfg)
        if chg_h > 0:
            chg_start = now
            chg_end = chg_start + timedelta(hours=chg_h)
            activities.append(Activity(
                chg_start, chg_end, "CHANGEOVER",
                lot_type=f"{prev_type}->{lot.lot_type}", note=f"{int(chg_h)}h"
            ))
            now = chg_end
            window_used += chg_h

        # fill
        fill_start = now
        fill_end = fill_start + timedelta(hours=lot.fill_hours)
        activities.append(Activity(
            fill_start, fill_end, "FILL",
            lot_id=lot.lot_id, lot_type=lot.lot_type, note=f"{lot.vials} vials"
        ))
        now = fill_end
        window_used += lot.fill_hours
        prev_type = lot.lot_type

    makespan_hours = (activities[-1].end - activities[0].start).total_seconds() / 3600.0

    # KPIs
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

def _sum_kind(activities: List[Activity], kind: str) -> float:
    return sum((a.end - a.start).total_seconds() for a in activities if a.kind == kind) / 3600.0
