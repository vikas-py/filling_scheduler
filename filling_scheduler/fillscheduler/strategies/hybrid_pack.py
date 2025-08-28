# filling_scheduler/fillscheduler/strategies/hybrid_pack.py
from __future__ import annotations
from typing import Deque, List, Optional, Tuple
from collections import deque, defaultdict

from ..models import Lot
from ..config import AppConfig
from ..rules import changeover_hours

class HybridPack:
    """
    Hybrid = Smart-pack (utilization/slack/switch penalties + beam lookahead)
             + SPT type-streak control (favor staying on type; within same type prefer SPT).

    Notes:
    - Keeps current strategy interface (no scheduler changes).
    - Encourages staying on same type; when staying, prefers shorter fills (SPT) to squeeze the window.
    - When switching, softly prefers the next type whose near-term SPT queue is attractive.
    """

    def name(self) -> str:
        return "hybrid-pack"

    # ---------- helpers (mostly from smart-pack 2.0) ----------
    def _fits(self, window_used: float, need: float, cfg: AppConfig) -> bool:
        pad = getattr(cfg, "UTIL_PAD_HOURS", 0.0) or 0.0
        return window_used + need <= (cfg.WINDOW_HOURS - pad) + 1e-9

    def _dyn_mult(self, window_used: float, cfg: AppConfig) -> float:
        u = max(0.0, min(1.0, window_used / max(cfg.WINDOW_HOURS, 1e-9)))
        lo = getattr(cfg, "DYNAMIC_SWITCH_MULT_MIN", 1.0)
        hi = getattr(cfg, "DYNAMIC_SWITCH_MULT_MAX", 1.5)
        return lo + (hi - lo) * u

    def _min_need_after(self, prev_type: Optional[str], remaining: Deque[Lot], cfg: AppConfig) -> float:
        best = float("inf")
        for c in remaining:
            chg = changeover_hours(prev_type, c.lot_type, cfg)
            need = chg + c.fill_hours
            if need < best:
                best = need
        return best if best != float("inf") else 0.0

    def _unusable_slack(self, window_used_after: float, new_prev: Optional[str], remaining: Deque[Lot], cfg: AppConfig) -> float:
        cap = max(0.0, cfg.WINDOW_HOURS - window_used_after)
        if cap <= 1e-9:
            return 0.0
        min_need = self._min_need_after(new_prev, remaining, cfg)
        return cap if min_need > cap + 1e-9 else 0.0

    def _type_spt_hint(self, target_type: str, remaining: Deque[Lot]) -> float:
        """
        Return a small bonus if the target_type has short jobs available (SPT flavor).
        Smaller shortest fill -> larger bonus (we invert).
        """
        shortest = None
        for c in remaining:
            if c.lot_type == target_type:
                shortest = c.fill_hours if shortest is None or c.fill_hours < shortest else shortest
        if shortest is None:
            return 0.0
        # Map shortest fill to a modest positive bonus; tuned small to avoid dominating
        return max(0.0, 2.0 - 0.02 * shortest)  # ~2.0 bonus dwindles as shortest grows

    def _score(self, prev_type: Optional[str], lot: Lot, window_used: float, remaining: Deque[Lot], cfg: AppConfig) -> float:
        # Base feasibility & amounts
        chg = changeover_hours(prev_type, lot.lot_type, cfg)
        need = chg + lot.fill_hours
        if not self._fits(window_used, need, cfg):
            return -1e9

        # Smart-pack dynamic switch penalty
        mult = self._dyn_mult(window_used, cfg)
        if prev_type is None:
            switch_pen = 0.0
        else:
            base = cfg.SCORE_BETA if prev_type == lot.lot_type else cfg.SCORE_ALPHA
            # hybrid multiplier gives us headroom to make switching more/less costly
            switch_pen = base * mult * getattr(cfg, "HYBRID_SWITCH_PENALTY_MULT", 1.0)

        # Slack waste (avoid leaving unusable tail that forces a new CLEAN)
        w_used_after = window_used + need
        slack_waste = self._unusable_slack(w_used_after, lot.lot_type, remaining, cfg)

        # ---- SPT type-streak control ----
        same_type = (prev_type == lot.lot_type) if prev_type is not None else True
        same_type_bonus = getattr(cfg, "HYBRID_SAME_TYPE_BONUS", 2.0) if same_type else 0.0

        # Within same-type, prefer SPT: give a bonus to shorter fills
        spt_weight = getattr(cfg, "HYBRID_SPT_WEIGHT", 0.5)
        spt_bonus = 0.0
        if same_type:
            # Inverse proportional: shorter fills -> higher bonus (scaled small)
            spt_bonus = spt_weight * (1.0 / max(lot.fill_hours, 1e-6))

        # If switching, prefer a target type whose upcoming queue has short tasks (SPT hint)
        switch_spt_hint = 0.0 if same_type else self._type_spt_hint(lot.lot_type, remaining)

        # Combine (hours-equivalent scoring)
        score = (
            need
            - switch_pen
            - getattr(cfg, "SLACK_WASTE_WEIGHT", 0.0) * slack_waste
            + getattr(cfg, "STREAK_BONUS", 0.0) * (1.0 if same_type else 0.0)
            + same_type_bonus
            + switch_spt_hint
            + spt_bonus
            - 0.005 * lot.fill_hours  # tiny bias to let more pieces fit
        )
        return score

    # ---------- Strategy API ----------
    def preorder(self, lots: List[Lot], cfg: AppConfig) -> Deque[Lot]:
        # No heavy global reorder; we rely on scored picking
        return deque(lots)

    def pick_next(self, remaining: Deque[Lot], prev_type: Optional[str], window_used: float, cfg: AppConfig) -> Optional[int]:
        # Beam search over top-K base scores + one-step look-ahead (lightweight)
        K = max(1, getattr(cfg, "BEAM_WIDTH", 3))

        base: List[Tuple[float, int]] = []
        for i, cand in enumerate(remaining):
            s = self._score(prev_type, cand, window_used, remaining, cfg)
            if s > -1e-9:
                base.append((s, i))
        if not base:
            return None

        base.sort(reverse=True, key=lambda x: x[0])
        top = base[:K]

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

            combo = base_score + 0.25 * follow_best  # modest look-ahead weight
            if best_combo is None or combo > best_combo:
                best_combo = combo
                best_idx = idx

        return best_idx if best_idx is not None else top[0][1]
