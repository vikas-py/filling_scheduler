from __future__ import annotations
from typing import List, Tuple, Optional
from .models import Activity, Lot
from .config import AppConfig

class ValidationError(Exception):
    """Raised when validation fails (used internally if you set raise_exceptions=True)."""
    pass

def _fmt_hours(x: float) -> str:
    return f"{x:g}"

def _maybe_fail_fast(
    title: str,
    errors: List[str],
    warnings: List[str],
    fail_fast: bool,
    raise_exceptions: bool,
) -> None:
    if warnings:
        print("\n⚠️  WARNINGS during", title)
        for w in warnings:
            print(f" - {w}")

    if errors:
        print(f"\n❌ {title} FAILED:")
        for e in errors:
            print(f" - {e}")
        print("\nFix the issues and run again. No schedule will be produced.")

        if raise_exceptions:
            raise ValidationError(f"{title} failed with {len(errors)} error(s).")
        if fail_fast:
            import sys
            sys.exit(1)

def validate_input_lots(
    lots: List[Lot],
    cfg: AppConfig,
    *,
    fail_fast: bool = True,
    raise_exceptions: bool = False,
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    # Config sanity
    if cfg.FILL_RATE_VPH <= 0:
        errors.append("Config: FILL_RATE_VPH must be > 0.")
    if cfg.WINDOW_HOURS <= 0:
        errors.append("Config: WINDOW_HOURS must be > 0.")
    if cfg.CLEAN_HOURS <= 0:
        errors.append("Config: CLEAN_HOURS must be > 0.")

    max_vials = int(max(0, cfg.WINDOW_HOURS) * max(0, cfg.FILL_RATE_VPH))
    window_str = _fmt_hours(cfg.WINDOW_HOURS)

    seen_ids = set()
    for lt in lots:
        if not lt.lot_id or not lt.lot_id.strip():
            errors.append("A lot has empty Lot ID.")
        if not lt.lot_type or not lt.lot_type.strip():
            errors.append(f"Lot {lt.lot_id or '(unknown)'} has empty Type.")
        if lt.vials is None or lt.vials <= 0:
            errors.append(f"Lot {lt.lot_id}: Vials must be a positive integer (got {lt.vials}).")

        if lt.lot_id in seen_ids:
            warnings.append(f"Duplicate Lot ID detected: {lt.lot_id}")
        seen_ids.add(lt.lot_id)

        if lt.fill_hours > cfg.WINDOW_HOURS + 1e-6:
            errors.append(
                f"Lot {lt.lot_id}: {lt.vials:,} vials (~{lt.fill_hours:.2f} h) "
                f"exceeds the {window_str} h clean window. "
                f"Max vials per lot at current rate: {max_vials:,}."
            )

    _maybe_fail_fast("INPUT VALIDATION", errors, warnings, fail_fast, raise_exceptions)
    return errors, warnings

def validate_schedule(
    activities: List[Activity],
    cfg: AppConfig,
    *,
    fail_fast: bool = True,
    raise_exceptions: bool = False,
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    window_str = _fmt_hours(cfg.WINDOW_HOURS)
    window_sum = 0.0
    in_block = False
    seen_fill_ids = set()

    for a in activities:
        if a.kind == "CLEAN":
            if in_block and window_sum > cfg.WINDOW_HOURS + 1e-6:
                errors.append(f"Window overrun: {window_sum:.2f} h > {window_str} h.")
            window_sum = 0.0
            in_block = True
            continue

        dur_h = (a.end - a.start).total_seconds() / 3600.0
        window_sum += dur_h

        if a.kind == "FILL":
            if dur_h > cfg.WINDOW_HOURS + 1e-6:
                errors.append(
                    f"Lot {a.lot_id} FILL duration {dur_h:.2f} h exceeds {window_str} h limit."
                )
            if a.lot_id:
                if a.lot_id in seen_fill_ids:
                    errors.append(f"Lot split detected: {a.lot_id}")
                seen_fill_ids.add(a.lot_id)

    if in_block and window_sum > cfg.WINDOW_HOURS + 1e-6:
        errors.append(f"Window overrun: {window_sum:.2f} h > {window_str} h.")

    _maybe_fail_fast("SCHEDULE VALIDATION", errors, warnings, fail_fast, raise_exceptions)
    return errors, warnings
