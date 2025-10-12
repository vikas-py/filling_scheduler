# filling_scheduler/fillscheduler/strategies/lpt_pack.py
from __future__ import annotations
from typing import Deque, List, Optional
from collections import deque

from ..models import Lot
from ..config import AppConfig
from ..rules import changeover_hours

class LptPack:
    """
    LPT = Longest Processing Time first.
    - Preorder: global sort by descending fill_hours (largest lots first).
    - Picker: prefer same-type that fits within the window; otherwise any that fits.
    This tends to improve window utilization; may increase changeovers.
    """
    def name(self) -> str:
        return "lpt-pack"

    def preorder(self, lots: List[Lot], cfg: AppConfig) -> Deque[Lot]:
        ordered = sorted(lots, key=lambda x: (-x.fill_hours, x.lot_type, x.lot_id))
        return deque(ordered)

    def pick_next(self, remaining: Deque[Lot], prev_type: Optional[str], window_used: float, cfg: AppConfig) -> Optional[int]:
        # 1) try same-type candidates that fit
        for i, cand in enumerate(remaining):
            chg = changeover_hours(prev_type, cand.lot_type, cfg)
            need = chg + cand.fill_hours
            if window_used + need <= cfg.WINDOW_HOURS + 1e-9:
                if prev_type is None or cand.lot_type == prev_type:
                    return i
        # 2) otherwise any candidate that fits
        for i, cand in enumerate(remaining):
            chg = changeover_hours(prev_type, cand.lot_type, cfg)
            need = chg + cand.fill_hours
            if window_used + need <= cfg.WINDOW_HOURS + 1e-9:
                return i
        return None
