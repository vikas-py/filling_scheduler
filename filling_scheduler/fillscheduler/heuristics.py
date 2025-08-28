# fillscheduler/heuristics.py
from __future__ import annotations
from collections import defaultdict, deque
from typing import Deque, List, Optional
from .models import Lot
from .config import AppConfig

def base_pool_order(lots: List[Lot]) -> List[Lot]:
    """Cluster by type size (desc) then inside by SPT (fill_hours asc)."""
    by_type = defaultdict(list)
    for lot in lots:
        by_type[lot.lot_type].append(lot)
    for t in by_type:
        by_type[t].sort(key=lambda x: x.fill_hours)
    type_sizes = {t: len(g) for t, g in by_type.items()}

    pool = []
    for t, group in by_type.items():
        pool.extend(group)
    pool.sort(key=lambda x: (-type_sizes[x.lot_type], x.fill_hours))
    return pool

def changeover_hours(prev_type: Optional[str], next_type: str, cfg: AppConfig) -> float:
    if prev_type is None:
        return 0.0  # First lot after clean: setup is covered by the clean
    return cfg.CHG_SAME_HOURS if prev_type == next_type else cfg.CHG_DIFF_HOURS

def pick_next_that_fits(remaining: Deque[Lot],
                        prev_type: Optional[str],
                        window_used: float,
                        cfg: AppConfig) -> Optional[int]:
    """Prefer same-type lots that fit; otherwise any lot that fits within the window."""
    # Pass 1: same type
    for i in range(len(remaining)):
        cand = remaining[i]
        chg = changeover_hours(prev_type, cand.lot_type, cfg)
        need = chg + cand.fill_hours
        if window_used + need <= cfg.WINDOW_HOURS:
            if prev_type is None or cand.lot_type == prev_type:
                return i
    # Pass 2: any type
    for i in range(len(remaining)):
        cand = remaining[i]
        chg = changeover_hours(prev_type, cand.lot_type, cfg)
        need = chg + cand.fill_hours
        if window_used + need <= cfg.WINDOW_HOURS:
            return i
    return None
