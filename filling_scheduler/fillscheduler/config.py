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
    UTIL_PAD_HOURS: float = 0.0        # tiny slack to avoid float rounding
    BEAM_WIDTH: int = 3                # small look-ahead
    # Base penalties (hours). Think of these as "cost in hours" we want to avoid.
    SCORE_ALPHA: float = 8.0           # diff-type changeover penalty (baseline)
    SCORE_BETA: float = 4.0            # same-type changeover penalty (baseline)

    # NEW: balance knobs
    SLACK_WASTE_WEIGHT: float = 3.0    # penalty per hour of unusable slack left in window
    STREAK_BONUS: float = 1.0          # bonus (hours) for staying on same type
    # Optional: increase diff-type penalty when the window is still relatively empty
    DYNAMIC_SWITCH_MULT_MIN: float = 1.0   # multiplier at 0% window used
    DYNAMIC_SWITCH_MULT_MAX: float = 1.5   # multiplier at 100% window used

    # CFS tuning
    CFS_CLUSTER_ORDER: str = "by_count"  # or "by_count"
    CFS_WITHIN: str = "LPT"                    # or "LPT"

    # Hybrid tuning
    HYBRID_SAME_TYPE_BONUS: float = 2.0     # extra push to keep type streaks
    HYBRID_SPT_WEIGHT: float = 0.5          # SPT bias when staying on same type
    HYBRID_SWITCH_PENALTY_MULT: float = 1.1 # >1 makes switches a bit costlier than smart-pack base


    # ==== Reporting ====
    HTML_REPORT: bool = True
    HTML_FILENAME: str = "report.html"
    DATETIME_FMT: str = "%Y-%m-%d %H:%M"
