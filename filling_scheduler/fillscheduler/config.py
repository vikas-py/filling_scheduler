# fillscheduler/config.py
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AppConfig:
    # ==== File & run options ====
    DATA_PATH: Path = Path("examples/lots.csv")     # input CSV
    OUTPUT_DIR: Path = Path("output")               # folder for outputs
    START_TIME_STR: str = "2025-01-01 08:00"        # schedule start (local)
    STRATEGY: str = "spt-pack"                      # heuristic name
    INTERACTIVE: bool = False                       # set True if you want prompts

    # ==== Process constants ====
    FILL_RATE_VPH: float = 332.0 * 60.0   # 332 vials/min
    CLEAN_HOURS: float = 24.0
    WINDOW_HOURS: float = 120.0
    CHG_SAME_HOURS: float = 4.0
    CHG_DIFF_HOURS: float = 8.0

