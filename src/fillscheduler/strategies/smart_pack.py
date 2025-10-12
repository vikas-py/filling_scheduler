# fillscheduler/strategies/smart_pack.py
from __future__ import annotations

from collections import deque

from ..config import AppConfig
from ..models import Lot
from ..rules import changeover_hours


class SmartPack:
    """Scored packing with short look-ahead, slack-waste penalty, and dynamic switch penalties."""

    def name(self) -> str:
        return "smart-pack"

    def preorder(self, lots: list[Lot], cfg: AppConfig) -> deque[Lot]:
        # No global reorder; we pick by scores as we go
        return deque(lots)

    # ---- scoring helpers ----
    def _fits(self, window_used: float, need: float, cfg: AppConfig) -> bool:
        pad = getattr(cfg, "UTIL_PAD_HOURS", 0.0) or 0.0
        return window_used + need <= (cfg.WINDOW_HOURS - pad) + 1e-9

    def _dyn_mult(self, window_used: float, cfg: AppConfig) -> float:
        u = max(0.0, min(1.0, window_used / max(cfg.WINDOW_HOURS, 1e-9)))
        lo = getattr(cfg, "DYNAMIC_SWITCH_MULT_MIN", 1.0)
        hi = getattr(cfg, "DYNAMIC_SWITCH_MULT_MAX", 1.5)
        return lo + (hi - lo) * u

    def _min_need_after(
        self, prev_type: str | None, remaining: deque[Lot], cfg: AppConfig
    ) -> float:
        best = float("inf")
        for c in remaining:
            chg = changeover_hours(prev_type, c.lot_type, cfg)
            need = chg + c.fill_hours
            if need < best:
                best = need
        return best if best != float("inf") else 0.0

    def _unusable_slack(
        self,
        window_used_after: float,
        new_prev: str | None,
        remaining: deque[Lot],
        cfg: AppConfig,
    ) -> float:
        cap = max(0.0, cfg.WINDOW_HOURS - window_used_after)
        if cap <= 1e-9:
            return 0.0
        min_need = self._min_need_after(new_prev, remaining, cfg)
        return cap if min_need > cap + 1e-9 else 0.0

    def _score(
        self,
        prev_type: str | None,
        lot: Lot,
        window_used: float,
        remaining: deque[Lot],
        cfg: AppConfig,
    ) -> float:
        chg = changeover_hours(prev_type, lot.lot_type, cfg)
        need = chg + lot.fill_hours
        if not self._fits(window_used, need, cfg):
            return -1e9

        mult = self._dyn_mult(window_used, cfg)
        if prev_type is None:
            switch_pen = 0.0
        else:
            base = cfg.SCORE_BETA if prev_type == lot.lot_type else cfg.SCORE_ALPHA
            switch_pen = base * mult

        w_used_after = window_used + need
        slack_waste = self._unusable_slack(w_used_after, lot.lot_type, remaining, cfg)
        streak_bonus = getattr(cfg, "STREAK_BONUS", 0.0) if prev_type == lot.lot_type else 0.0

        score = (
            need
            - switch_pen
            - getattr(cfg, "SLACK_WASTE_WEIGHT", 0.0) * slack_waste
            + streak_bonus
            - 0.01 * lot.fill_hours  # mild preference for shorter fills
        )
        return score

    def pick_next(
        self, remaining: deque[Lot], prev_type: str | None, window_used: float, cfg: AppConfig
    ) -> int | None:
        K = max(1, getattr(cfg, "BEAM_WIDTH", 3))

        base: list[tuple[float, int]] = []
        for i, cand in enumerate(remaining):
            s = self._score(prev_type, cand, window_used, remaining, cfg)
            if s > -1e9:
                base.append((s, i))
        if not base:
            return None

        base.sort(reverse=True, key=lambda x: x[0])
        top = base[:K]

        # one-step look-ahead with modest weight
        best_idx = None
        best_combo = None
        for base_score, idx in top:
            cand = remaining[idx]
            chg = changeover_hours(prev_type, cand.lot_type, cfg)
            need = chg + cand.fill_hours
            if not self._fits(window_used, need, cfg):
                continue

            new_used = window_used + need
            new_prev = cand.lot_type

            follow_best = 0.0
            for j, nxt in enumerate(remaining):
                if j == idx:
                    continue
                s2 = self._score(new_prev, nxt, new_used, remaining, cfg)
                if s2 > follow_best:
                    follow_best = s2

            combo = base_score + 0.25 * follow_best
            if best_combo is None or combo > best_combo:
                best_combo = combo
                best_idx = idx

        return best_idx if best_idx is not None else top[0][1]
