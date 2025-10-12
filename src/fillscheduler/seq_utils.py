# fillscheduler/seq_utils.py
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .models import Lot


def read_sequence_csv(path: Path) -> list[str]:
    """
    Read a sequence CSV with a column 'Lot ID' (or 'LotID', 'lot_id') in the desired order.
    Returns a list of lot IDs in order.
    """
    if not path.exists():
        raise FileNotFoundError(f"Sequence file not found: {path}")

    df = pd.read_csv(path)
    col = None
    for c in ["Lot ID", "LotID", "lot_id", "lotid"]:
        if c in df.columns:
            col = c
            break
    if col is None:
        raise ValueError("Sequence CSV must have a 'Lot ID' column (or LotID/lot_id/lotid).")

    seq = [str(x).strip() for x in df[col].tolist()]
    # filter out blanks
    seq = [x for x in seq if x]
    if not seq:
        raise ValueError("Sequence CSV contained no Lot IDs.")
    return seq


def order_lots_by_sequence(lots: list[Lot], sequence: list[str]) -> list[Lot]:
    """
    Return the lots list ordered by 'sequence'. Any lots not in sequence
    are appended at the end in their original order (and noted by caller if desired).
    """
    by_id: dict[str, Lot] = {lt.lot_id: lt for lt in lots}
    ordered: list[Lot] = []
    missing: list[str] = []

    for lot_id in sequence:
        if lot_id in by_id:
            ordered.append(by_id[lot_id])
        else:
            missing.append(lot_id)

    # Remaining (not specified) lots:
    remaining = [lt for lt in lots if lt.lot_id not in set(sequence)]
    ordered.extend(remaining)

    return ordered
