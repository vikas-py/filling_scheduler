# filling_scheduler/fillscheduler/strategies/__init__.py
from __future__ import annotations

from collections import deque
from typing import Optional, Protocol

from ..config import AppConfig
from ..models import Lot


class Strategy(Protocol):
    def name(self) -> str: ...
    def preorder(self, lots: list[Lot], cfg: AppConfig) -> deque[Lot]: ...
    def pick_next(
        self,
        remaining: deque[Lot],
        prev_type: str | None,
        window_used: float,
        cfg: AppConfig,
    ) -> int | None: ...


def get_strategy(strategy_name: str) -> Strategy:
    sn = (strategy_name or "").replace("-", "_").strip().lower()
    if sn in ("smart_pack", "smartpack", "smart"):
        from .smart_pack import SmartPack

        return SmartPack()
    if sn in ("spt_pack", "sptpack", "spt"):
        from .spt_pack import SptPack

        return SptPack()
    if sn in ("lpt_pack", "lptpack", "lpt"):
        from .lpt_pack import LptPack

        return LptPack()
    if sn in ("cfs_pack", "cfspack", "cfs"):
        from .cfs_pack import CFSPack

        return CFSPack()
    if sn in ("hybrid_pack", "hybrid"):
        from .hybrid_pack import HybridPack

        return HybridPack()
    if sn in ("milp_opt", "milpopt", "milp"):
        from .milp_opt import MilpOpt

        return MilpOpt()
    # default
    from .smart_pack import SmartPack

    return SmartPack()
