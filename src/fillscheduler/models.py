from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

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
    kind: str                 # "CLEAN" | "CHANGEOVER" | "FILL"
    lot_id: Optional[str] = None
    lot_type: Optional[str] = None
    note: Optional[str] = None
