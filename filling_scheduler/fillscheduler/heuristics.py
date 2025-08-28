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

def _candidate_score(prev_type: Optional[str], lot: Lot, window_used: float, cfg: AppConfig) -> Tuple[float, float, float]:
    """
    Higher is better. Sort key:
      1) utilization gain in current window (higher better),
      2) changeover penalty (less negative better),
      3) tie-breaker: shorter fill first (pack more).
    """
    chg = changeover_hours(prev_type, lot.lot_type, cfg)
    need = chg + lot.fill_hours
    remaining = max(0.0, cfg.WINDOW_HOURS - window_used)
    util_gain = min(need, remaining) / max(remaining, 1e-9)  # [0..1]

    if prev_type is None:
        penalty = 0.0
    else:
        penalty = -(cfg.SCORE_ALPHA if prev_type != lot.lot_type else cfg.SCORE_BETA)

    return (util_gain, penalty, -lot.fill_hours)

def pick_next_scored(remaining: Deque[Lot],
                     prev_type: Optional[str],
                     window_used: float,
                     cfg: AppConfig) -> Optional[int]:
    candidates: List[Tuple[Tuple[float, float, float], int]] = []
    for i, cand in enumerate(remaining):
        chg = changeover_hours(prev_type, cand.lot_type, cfg)
        need = chg + cand.fill_hours
        if _fits(window_used, need, cfg):
            candidates.append((_candidate_score(prev_type, cand, window_used, cfg), i))
    if not candidates:
        return None
    candidates.sort(reverse=True, key=lambda x: x[0])
    return candidates[0][1]

def pick_next_scored_beam1(remaining: Deque[Lot],
                           prev_type: Optional[str],
                           window_used: float,
                           cfg: AppConfig) -> Optional[int]:
    """Beam width K: try top-K base candidates; project one extra step and choose best combined."""
    K = max(1, getattr(cfg, "BEAM_WIDTH", 3))
    base: List[Tuple[Tuple[float, float, float], int]] = []
    for i, cand in enumerate(remaining):
        chg = changeover_hours(prev_type, cand.lot_type, cfg)
        need = chg + cand.fill_hours
        if _fits(window_used, need, cfg):
            base.append((_candidate_score(prev_type, cand, window_used, cfg), i))
    if not base:
        return None
    base.sort(reverse=True, key=lambda x: x[0])
    top = base[:K]

    def project(idx: int) -> Tuple[float, float]:
        cand = remaining[idx]
        chg = changeover_hours(prev_type, cand.lot_type, cfg)
        need = chg + cand.fill_hours
        if not _fits(window_used, need, cfg):
            return (-1.0, -1e9)
        new_used = window_used + need
        new_prev = cand.lot_type

        best_util2 = 0.0
        best_pen2 = -1e9
        for j, nxt in enumerate(remaining):
            if j == idx:
                continue
            chg2 = changeover_hours(new_prev, nxt.lot_type, cfg)
            need2 = chg2 + nxt.fill_hours
            if _fits(new_used, need2, cfg):
                rem = max(0.0, cfg.WINDOW_HOURS - new_used)
                util2 = min(need2, rem) / max(rem, 1e-9)
                pen2 = 0.0 if new_prev is None else (-(cfg.SCORE_ALPHA if new_prev != nxt.lot_type else cfg.SCORE_BETA))
                if util2 > best_util2 or (abs(util2 - best_util2) < 1e-9 and pen2 > best_pen2):
                    best_util2, best_pen2 = util2, pen2
        return (best_util2, best_pen2)

    best_idx = None
    best_key: Optional[Tuple[float, float]] = None
    for score, idx in top:
        util2, pen2 = project(idx)
        key = (score[0] + util2, score[1] + pen2)
        if best_key is None or key > best_key:
            best_key = key
            best_idx = idx
    return best_idx
