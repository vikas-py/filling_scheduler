from __future__ import annotations
from typing import Deque, List, Optional, Dict, Tuple
from collections import deque

from ..models import Lot
from ..config import AppConfig
from ..rules import changeover_hours

# PuLP
import pulp


class MilpOpt:
    """
    MILP exact optimizer (small/medium N).
    - Assigns lots to blocks and orders them inside each block.
    - Capacity per block: sum(fill) + sum(changeovers within block) <= WINDOW_HOURS.
    - Objective: minimize CLEAN_HOURS * #blocks + total changeovers (fill time is constant).
    - Rebuilds a global order (block-by-block) and returns it via preorder().
    - pick_next(): follow the exact order (start a new block when needed).
    """

    def name(self) -> str:
        return "milp-opt"

    # ---- public Strategy API ----
    def preorder(self, lots: List[Lot], cfg: AppConfig) -> Deque[Lot]:
        n = len(lots)
        max_n = getattr(cfg, "MILP_MAX_LOTS", 30)
        if n > max_n:
            raise RuntimeError(
                f"MILP disabled: {n} lots > MILP_MAX_LOTS={max_n}. "
                "Use a smaller dataset (e.g., sample 20–30 lots) for benchmarking."
            )

        # Build the MILP
        order = self._solve_milp(lots, cfg)
        return deque(order)

    def pick_next(self, remaining: Deque[Lot], prev_type: Optional[str], window_used: float, cfg: AppConfig) -> Optional[int]:
        # Follow exact order: if next in line fits current window, take it; else start new block.
        if not remaining:
            return None
        lot = remaining[0]
        chg = changeover_hours(prev_type, lot.lot_type, cfg)
        need = chg + lot.fill_hours
        return 0 if (window_used + need <= cfg.WINDOW_HOURS + 1e-9) else None

    # ---- MILP model ----
    def _solve_milp(self, lots: List[Lot], cfg: AppConfig) -> List[Lot]:
        n = len(lots)
        idx = list(range(n))

        # Precompute processing and setup times
        t = {i: lots[i].fill_hours for i in idx}
        setup = {(i, j): (0.0 if i == j else (4.0 if lots[i].lot_type == lots[j].lot_type else 8.0))
                 for i in idx for j in idx}

        # Upper bound on number of blocks
        # Safe upper bound: each lot can be alone => B_max = n
        B = min(n, max(1, getattr(cfg, "MILP_MAX_BLOCKS", n)))

        # ----- Variables -----
        # y[b,i] = 1 if lot i assigned to block b
        y = pulp.LpVariable.dicts("y", (range(B), idx), lowBound=0, upBound=1, cat="Binary")
        # u[b] = 1 if block b is used
        u = pulp.LpVariable.dicts("u", range(B), lowBound=0, upBound=1, cat="Binary")
        # s[b,i] = 1 if i is start lot in block b
        s = pulp.LpVariable.dicts("s", (range(B), idx), lowBound=0, upBound=1, cat="Binary")
        # e[b,i] = 1 if i is end lot in block b
        e = pulp.LpVariable.dicts("e", (range(B), idx), lowBound=0, upBound=1, cat="Binary")
        # z[b,i,j] = 1 if in block b, j immediately follows i (i != j)
        z = pulp.LpVariable.dicts("z", (range(B), idx, idx), lowBound=0, upBound=1, cat="Binary")
        # MTZ positions to break subtours (1..n) for nodes in block
        p = pulp.LpVariable.dicts("pos", (range(B), idx), lowBound=0, upBound=n, cat="Integer")

        # ----- Model -----
        prob = pulp.LpProblem("FillingLineMILP", pulp.LpMinimize)

        CLEAN = float(cfg.CLEAN_HOURS)
        WINDOW = float(cfg.WINDOW_HOURS)

        # Objective: Clean cost + changeover cost (fill time is constant -> drop)
        prob += pulp.lpSum(CLEAN * u[b] for b in range(B)) + \
                pulp.lpSum(setup[i, j] * z[b][i][j] for b in range(B) for i in idx for j in idx if i != j)

        # ----- Constraints -----

        # Each lot in exactly one block
        for i in idx:
            prob += pulp.lpSum(y[b][i] for b in range(B)) == 1, f"assign_once_{i}"

        # Block used if any lot assigned; and at most n*y bounds
        for b in range(B):
            prob += pulp.lpSum(y[b][i] for i in idx) >= u[b], f"used_lb_{b}"
            prob += pulp.lpSum(y[b][i] for i in idx) <= n * u[b], f"used_ub_{b}"

        # For each block: exactly one start and one end if used
        for b in range(B):
            prob += pulp.lpSum(s[b][i] for i in idx) == u[b], f"one_start_{b}"
            prob += pulp.lpSum(e[b][i] for i in idx) == u[b], f"one_end_{b}"

        # Degree constraints inside each block (path)
        for b in range(B):
            for i in idx:
                # Outgoing arcs: 1 if in block and not end; 0 if not in block
                prob += pulp.lpSum(z[b][i][j] for j in idx if j != i) == y[b][i] - e[b][i], f"outdeg_{b}_{i}"
                # Incoming arcs: 1 if in block and not start
                prob += pulp.lpSum(z[b][j][i] for j in idx if j != i) == y[b][i] - s[b][i], f"indeg_{b}_{i}"

        # MTZ subtour elimination for each block
        M = n  # big-M for positions
        for b in range(B):
            for i in idx:
                # position bounds tie to assignment
                prob += p[b][i] >= 1 * y[b][i], f"pos_lb_{b}_{i}"
                prob += p[b][i] <= n * y[b][i], f"pos_ub_{b}_{i}"
            for i in idx:
                for j in idx:
                    if i == j:
                        continue
                    # if z[b,i,j] == 1 then p[j] >= p[i] + 1
                    prob += p[b][j] >= p[b][i] + 1 - M * (1 - z[b][i][j]), f"mtz_{b}_{i}_{j}"

        # Capacity per block: sum(fill) + sum(setup on arcs) <= WINDOW
        for b in range(B):
            prob += (
                pulp.lpSum(t[i] * y[b][i] for i in idx) +
                pulp.lpSum(setup[i, j] * z[b][i][j] for i in idx for j in idx if i != j)
            ) <= WINDOW + (1 - u[b]) * WINDOW, f"cap_{b}"
            # The + (1-u[b])*WINDOW lets empty blocks trivially satisfy capacity.

        # ----- Solve -----
        # Solver config
        time_limit = int(getattr(cfg, "MILP_TIME_LIMIT", 60))
        try:
            solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit)
        except TypeError:
            # Older PuLP versions have 'maxSeconds'
            solver = pulp.PULP_CBC_CMD(msg=False, maxSeconds=time_limit)

        status = prob.solve(solver)
        if pulp.LpStatus[status] not in ("Optimal", "Not Solved", "Integer Feasible", "Optimal Infeasible"):
            raise RuntimeError(f"MILP solver status: {pulp.LpStatus[status]}")

        # ----- Build order from solution -----
        # Collect block sequences in increasing block index
        sequences: List[List[int]] = []
        for b in range(B):
            if pulp.value(u[b]) < 0.5:
                continue
            # find start
            start = None
            for i in idx:
                if pulp.value(s[b][i]) > 0.5:
                    start = i
                    break
            if start is None:
                continue
            seq = [start]
            current = start
            # follow successors
            while True:
                nxt = None
                for j in idx:
                    if current != j and pulp.value(z[b][current][j]) > 0.5:
                        nxt = j
                        break
                if nxt is None:
                    break
                seq.append(nxt)
                current = nxt
            sequences.append(seq)

        # Flatten blocks in order b=0..B-1
        order_ids = [i for seq in sequences for i in seq]
        if len(order_ids) != n:
            # Fallback: if for any reason we missed some, append remaining by SPT
            remaining = set(idx) - set(order_ids)
            order_ids.extend(sorted(list(remaining), key=lambda i: t[i]))

        # Return actual Lot objects in the found order
        return [lots[i] for i in order_ids]
