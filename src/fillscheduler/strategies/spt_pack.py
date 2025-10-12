# fillscheduler/strategies/spt_pack.py
from __future__ import annotations
from typing import Deque, List, Optional
from collections import defaultdict, deque

from ..models import Lot
from ..config import AppConfig
from ..rules import changeover_hours

class SptPack:
    """Cluster by type frequency, then Shortest-Processing-Time within type. Greedy fit inside window."""
    def name(self) -> str:
        return "spt-pack"

    def preorder(self, lots: List[Lot], cfg: AppConfig) -> Deque[Lot]:
        by_type = defaultdict(list)
        for lot in lots:
            by_type[lot.lot_type].append(lot)
        for t in by_type:
            by_type[t].sort(key=lambda x: x.fill_hours)  # SPT within type
        type_sizes = {t: len(g) for t, g in by_type.items()}
        pool: List[Lot] = []
        for t, group in by_type.items():
            pool.extend(group)
        pool.sort(key=lambda x: (-type_sizes[x.lot_type], x.fill_hours))
        return deque(pool)

    def pick_next(self, remaining: Deque[Lot], prev_type: Optional[str], window_used: float, cfg: AppConfig) -> Optional[int]:
        # First try same-type fits
        for i, cand in enumerate(remaining):
            chg = changeover_hours(prev_type, cand.lot_type, cfg)
            need = chg + cand.fill_hours
            if window_used + need <= cfg.WINDOW_HOURS + 1e-9:
                if prev_type is None or cand.lot_type == prev_type:
                    return i
        # Then any that fits
        for i, cand in enumerate(remaining):
            chg = changeover_hours(prev_type, cand.lot_type, cfg)
            need = chg + cand.fill_hours
            if window_used + need <= cfg.WINDOW_HOURS + 1e-9:
                return i
        return None
