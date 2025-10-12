# filling_scheduler/fillscheduler/strategies/cfs_pack.py
from __future__ import annotations

from collections import defaultdict, deque

from ..config import AppConfig
from ..models import Lot
from ..rules import changeover_hours


class CFSPack:
    """
    CFS = Cluster-first, sequence-second.
    - Cluster by Type.
    - Order clusters (by total fill hours or by lot count).
    - Sequence within each cluster by SPT (default) or LPT.

    Preorder creates a big deque like: [typeA..., typeB..., typeC...]
    Picker tries to stay within the current cluster (same type) to minimize switches.
    """

    def name(self) -> str:
        return "cfs-pack"

    def _cluster_order(self, by_type: dict[str, list[Lot]], cfg: AppConfig) -> list[str]:
        mode = getattr(cfg, "CFS_CLUSTER_ORDER", "by_total_hours").lower()
        if mode not in {"by_total_hours", "by_count"}:
            mode = "by_total_hours"

        if mode == "by_total_hours":
            totals = {t: sum(lot.fill_hours for lot in lots) for t, lots in by_type.items()}
            return sorted(by_type.keys(), key=lambda t: (-totals[t], t))
        else:  # by_count
            counts = {t: len(lots) for t, lots in by_type.items()}
            return sorted(by_type.keys(), key=lambda t: (-counts[t], t))

    def _sequence_within(self, lots: list[Lot], cfg: AppConfig) -> list[Lot]:
        mode = getattr(cfg, "CFS_WITHIN", "SPT").upper()
        if mode == "LPT":
            return sorted(lots, key=lambda x: (-x.fill_hours, x.lot_id))
        # default SPT
        return sorted(lots, key=lambda x: (x.fill_hours, x.lot_id))

    def preorder(self, lots: list[Lot], cfg: AppConfig) -> deque[Lot]:
        # 1) cluster by type
        by_type: dict[str, list[Lot]] = defaultdict(list)
        for lot in lots:
            by_type[lot.lot_type].append(lot)

        # 2) order clusters
        cluster_order = self._cluster_order(by_type, cfg)

        # 3) sequence within each cluster
        ordered: list[Lot] = []
        for t in cluster_order:
            ordered.extend(self._sequence_within(by_type[t], cfg))

        return deque(ordered)

    def pick_next(
        self, remaining: deque[Lot], prev_type: str | None, window_used: float, cfg: AppConfig
    ) -> int | None:
        """
        Greedy fit with strong preference to stay in current cluster (same type).
        Then fall back to any lot that fits.
        """
        # 1) same-type first
        for i, cand in enumerate(remaining):
            chg = changeover_hours(prev_type, cand.lot_type, cfg)
            need = chg + cand.fill_hours
            if window_used + need <= cfg.WINDOW_HOURS + 1e-9:
                if prev_type is None or cand.lot_type == prev_type:
                    return i

        # 2) any type that fits
        for i, cand in enumerate(remaining):
            chg = changeover_hours(prev_type, cand.lot_type, cfg)
            need = chg + cand.fill_hours
            if window_used + need <= cfg.WINDOW_HOURS + 1e-9:
                return i

        return None
