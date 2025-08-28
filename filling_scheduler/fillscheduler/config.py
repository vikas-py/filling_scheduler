from dataclasses import dataclass
from pathlib import Path

@dataclass
class AppConfig:
    # ==== File & run options ====
    DATA_PATH: Path = Path("examples/lots.csv")
    OUTPUT_DIR: Path = Path("output")
    START_TIME_STR: str = "2025-01-01 08:00"

    # Scheduling strategy:
    # - "smart-pack" (new, recommended)
    # - "spt-pack"   (original heuristic)
    STRATEGY: str = "smart-pack"
    INTERACTIVE: bool = False

    # ==== Process constants ====
    FILL_RATE_VPH: float = 332.0 * 60.0  # 19,920 vials/h
    CLEAN_HOURS: float = 24.0
    WINDOW_HOURS: float = 120.0
    CHG_SAME_HOURS: float = 4.0
    CHG_DIFF_HOURS: float = 8.0

    # ==== Heuristic tuning (smart-pack) ====
    # Tiny slack to avoid floating point window overruns
    UTIL_PAD_HOURS: float = 0.0
    # Beam search width for short look-ahead (>=1)
    BEAM_WIDTH: int = 3
    # Penalty weights for changeover in scoring (diff > same)
    SCORE_ALPHA: float = 8.0   # diff-type penalty
    SCORE_BETA: float = 4.0    # same-type penalty

    # ==== Reporting ====
    HTML_REPORT: bool = True
    HTML_FILENAME: str = "report.html"
    DATETIME_FMT: str = "%Y-%m-%d %H:%M"
