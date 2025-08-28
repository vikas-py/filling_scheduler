from __future__ import annotations
from collections import defaultdict, deque
from typing import Deque, List, Optional, Tuple

from .models import Lot
from .config import AppConfig

# ==== Original helpers (kept) ====

def base_pool_order(lots: List[Lot]) -> List[Lot]:
    """Cluster by type count (desc) then inside by SPT (fill_hours asc)."""
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
        return 0.0  # setup for first lot is covered by CLEAN
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

# ==== New: smart-pack scoring heuristic ====

def _fits(window_used: float, add_hours: float, cfg: AppConfig) -> bool:
    pad = getattr(cfg, "UTIL_PAD_HOURS", 0.0) or 0.0
    return window_used + add_hours <= (cfg.WINDOW_HOURS - pad) + 1e-9

def _dynamic_switch_multiplier(window_used: float, cfg: AppConfig) -> float:
    """Scale switch penalties mildly as we near the window end."""
    u = max(0.0, min(1.0, window_used / max(cfg.WINDOW_HOURS, 1e-9)))
    lo = getattr(cfg, "DYNAMIC_SWITCH_MULT_MIN", 1.0)
    hi = getattr(cfg, "DYNAMIC_SWITCH_MULT_MAX", 1.5)
    return lo + (hi - lo) * u

def _min_need_after(prev_type: Optional[str], remaining: Deque[Lot], cfg: AppConfig) -> float:
    """Compute the minimum (chg + fill) needed by any remaining lot if we start from prev_type."""
    best = float("inf")
    for cand in remaining:
        chg = changeover_hours(prev_type, cand.lot_type, cfg)
        need = chg + cand.fill_hours
        if need < best:
            best = need
    return best if best != float("inf") else 0.0

def _unusable_slack(window_used_after: float, new_prev: Optional[str], remaining: Deque[Lot], cfg: AppConfig) -> float:
    """If the remaining capacity cannot fit even the smallest next job, we count all of it as 'wasted' slack."""
    remaining_cap = max(0.0, cfg.WINDOW_HOURS - window_used_after)
    if remaining_cap <= 1e-9:
        return 0.0
    min_need = _min_need_after(new_prev, remaining, cfg)
    return remaining_cap if min_need > remaining_cap + 1e-9 else 0.0

def _candidate_score2(
    prev_type: Optional[str],
    lot: Lot,
    window_used: float,
    remaining: Deque[Lot],
    cfg: AppConfig,
) -> float:
    """
    Score in hour-equivalents (higher is better):
      + utilization added (chg + fill)
      - dynamic changeover penalty
      - slack waste penalty
      + streak bonus for keeping same type
      - tiny tie-breaker for very long fills (we prefer squeezing more)
    """
    chg = changeover_hours(prev_type, lot.lot_type, cfg)
    need = chg + lot.fill_hours
    if not _fits(window_used, need, cfg):
        return -1e9  # invalid

    # dynamic switch penalty (prefer same type, penalize diff more; scale with window utilization)
    mult = _dynamic_switch_multiplier(window_used, cfg)
    if prev_type is None:
        switch_penalty = 0.0
    else:
        base_pen = cfg.SCORE_BETA if prev_type == lot.lot_type else cfg.SCORE_ALPHA
        switch_penalty = base_pen * mult

    # projected unusable slack after picking this lot
    window_used_after = window_used + need
    slack_waste = _unusable_slack(window_used_after, lot.lot_type, remaining, cfg)

    # streak bonus
    streak_bonus = getattr(cfg, "STREAK_BONUS", 0.0) if prev_type == lot.lot_type else 0.0

    # combine (hours-equivalent)
    score = need                 \
            - switch_penalty     \
            - getattr(cfg, "SLACK_WASTE_WEIGHT", 0.0) * slack_waste \
            + streak_bonus       \
            - 0.01 * lot.fill_hours   # gentle preference to shorter fills for packability

    return score

def pick_next_scored_beam1(
    remaining: Deque[Lot],
    prev_type: Optional[str],
    window_used: float,
    cfg: AppConfig,
) -> Optional[int]:
    """
    Beam width K: pick top-K by base score, then one-step look-ahead:
    choose the candidate whose (base + best-next) combined score is highest.
    """
    K = max(1, getattr(cfg, "BEAM_WIDTH", 3))

    # base scores
    base: List[Tuple[float, int]] = []
    for i, cand in enumerate(remaining):
        s = _candidate_score2(prev_type, cand, window_used, remaining, cfg)
        if s > -1e9:
            base.append((s, i))
    if not base:
        return None

    base.sort(reverse=True, key=lambda x: x[0])
    top = base[:K]

    # project a single next step greedily
    best_idx = None
    best_combo = None

    for base_score, idx in top:
        cand = remaining[idx]
        chg = changeover_hours(prev_type, cand.lot_type, cfg)
        need = chg + cand.fill_hours
        if not _fits(window_used, need, cfg):
            continue

        new_used = window_used + need
        new_prev = cand.lot_type

        # best follow-up choice
        follow_best = 0.0
        for j, nxt in enumerate(remaining):
            if j == idx:
                continue
            s2 = _candidate_score2(new_prev, nxt, new_used, remaining, cfg)
            if s2 > follow_best:
                follow_best = s2

        combo = base_score + 0.25 * follow_best   # modest look-ahead weight
        if best_combo is None or combo > best_combo:
            best_combo = combo
            best_idx = idx

    return best_idx if best_idx is not None else top[0][1]