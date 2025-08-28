# fillscheduler/strategies/__init__.py
from __future__ import annotations
from typing import Protocol, Deque, Optional, List
from collections import deque

from ..models import Lot
from ..config import AppConfig

class Strategy(Protocol):
    def name(self) -> str: ...
    def preorder(self, lots: List[Lot], cfg: AppConfig) -> Deque[Lot]: ...
    def pick_next(self, remaining: Deque[Lot], prev_type: Optional[str], window_used: float, cfg: AppConfig) -> Optional[int]: ...

def get_strategy(strategy_name: str) -> Strategy:
    sn = (strategy_name or "").replace("-", "_").strip().lower()
    if sn in ("smart_pack", "smartpack", "smart"):
        from .smart_pack import SmartPack
        return SmartPack()
    if sn in ("spt_pack", "sptpack", "spt"):
        from .spt_pack import SptPack
        return SptPack()
    # default fallback
    from .smart_pack import SmartPack
    return SmartPack()
