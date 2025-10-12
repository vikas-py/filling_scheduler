from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Lot:
    lot_id: str
    lot_type: str
    vials: int
    fill_hours: float


@dataclass
class Activity:
    start: datetime
    end: datetime
    kind: str  # "CLEAN" | "CHANGEOVER" | "FILL"
    lot_id: str | None = None
    lot_type: str | None = None
    note: str | None = None
