"""Integration tests for scheduling strategies.

Tests each strategy's end-to-end behavior through the full scheduling pipeline.
"""

from datetime import datetime

import pytest

from fillscheduler.config import AppConfig
from fillscheduler.models import Lot
from fillscheduler.scheduler import plan_schedule

# ============================================================================
# Helper fixtures
# ============================================================================


@pytest.fixture
def cfg():
    """Standard configuration for testing."""
    return AppConfig(
        FILL_RATE_VPH=19920.0,
        CLEAN_HOURS=24.0,
        WINDOW_HOURS=120.0,
        CHG_SAME_HOURS=4.0,
        CHG_DIFF_HOURS=8.0,
        START_TIME_STR="2025-01-01 08:00",
    )


@pytest.fixture
def simple_lots(cfg):
    """Simple test dataset with 3 lots."""
    fill_rate = cfg.FILL_RATE_VPH
    return [
        Lot(lot_id="A1", lot_type="VialE", vials=100000, fill_hours=100000 / fill_rate),
        Lot(lot_id="A2", lot_type="VialH", vials=900000, fill_hours=900000 / fill_rate),
        Lot(lot_id="A3", lot_type="VialE", vials=750000, fill_hours=750000 / fill_rate),
    ]


@pytest.fixture
def varied_lots(cfg):
    """Dataset with varied sizes and types."""
    fill_rate = cfg.FILL_RATE_VPH
    return [
        Lot(lot_id="S1", lot_type="TypeA", vials=50000, fill_hours=50000 / fill_rate),  # Small
        Lot(lot_id="M1", lot_type="TypeB", vials=500000, fill_hours=500000 / fill_rate),  # Medium
        Lot(lot_id="L1", lot_type="TypeA", vials=1500000, fill_hours=1500000 / fill_rate),  # Large
        Lot(lot_id="S2", lot_type="TypeA", vials=75000, fill_hours=75000 / fill_rate),  # Small
        Lot(lot_id="M2", lot_type="TypeC", vials=400000, fill_hours=400000 / fill_rate),  # Medium
    ]


# ============================================================================
# All Strategies - Basic Functionality
# ============================================================================


@pytest.mark.parametrize(
    "strategy", ["smart-pack", "spt-pack", "lpt-pack", "cfs-pack", "hybrid-pack"]
)
def test_strategy_schedules_all_lots(simple_lots, cfg, strategy):
    """Test that each strategy schedules all input lots."""
    start_time = datetime.fromisoformat(cfg.START_TIME_STR)
    activities, _, _ = plan_schedule(simple_lots, start_time, cfg, strategy=strategy)

    # Extract fill activities
    fill_activities = [a for a in activities if a.kind == "FILL"]

    # Should have one fill per input lot
    assert len(fill_activities) == len(simple_lots), f"{strategy} didn't schedule all lots"

    # All lot IDs should be present
    filled_ids = {a.lot_id for a in fill_activities}
    input_ids = {lot.lot_id for lot in simple_lots}
    assert filled_ids == input_ids, f"{strategy} missing lots: {input_ids - filled_ids}"


@pytest.mark.parametrize(
    "strategy", ["smart-pack", "spt-pack", "lpt-pack", "cfs-pack", "hybrid-pack"]
)
def test_strategy_produces_valid_schedule(simple_lots, cfg, strategy):
    """Test that each strategy produces a valid schedule structure."""
    start_time = datetime.fromisoformat(cfg.START_TIME_STR)
    activities, makespan, kpis = plan_schedule(simple_lots, start_time, cfg, strategy=strategy)

    # Should have activities
    assert len(activities) > 0, f"{strategy} produced empty schedule"

    # First activity should be CLEAN
    assert activities[0].kind == "CLEAN", f"{strategy} didn't start with CLEAN"

    # Makespan should be positive
    assert makespan > 0, f"{strategy} produced invalid makespan"

    # KPIs should have expected keys (check for common KPI keys)
    assert len(kpis) > 0, f"{strategy} produced empty KPIs"
    # The actual keys may vary, but we should have some metrics
    assert "Makespan (h)" in kpis or "makespan" in kpis.get("Makespan (h)", "")


# ============================================================================
# SPT Strategy Tests
# ============================================================================


def test_spt_orders_by_ascending_vials(simple_lots, cfg):
    """Test that SPT processes lots in ascending vial order."""
    start_time = datetime.fromisoformat(cfg.START_TIME_STR)
    activities, _, _ = plan_schedule(simple_lots, start_time, cfg, strategy="spt-pack")

    fill_activities = [a for a in activities if a.kind == "FILL"]

    # SPT should fill A1 (100k), then A3 (750k), then A2 (900k)
    assert fill_activities[0].lot_id == "A1", "SPT should start with smallest lot"
    assert fill_activities[1].lot_id == "A3"
    assert fill_activities[2].lot_id == "A2", "SPT should end with largest lot"


# ============================================================================
# LPT Strategy Tests
# ============================================================================


def test_lpt_orders_by_descending_vials(simple_lots, cfg):
    """Test that LPT processes lots in descending vial order."""
    start_time = datetime.fromisoformat(cfg.START_TIME_STR)
    activities, _, _ = plan_schedule(simple_lots, start_time, cfg, strategy="lpt-pack")

    fill_activities = [a for a in activities if a.kind == "FILL"]

    # LPT should fill A2 (900k), then A3 (750k), then A1 (100k)
    assert fill_activities[0].lot_id == "A2", "LPT should start with largest lot"
    assert fill_activities[1].lot_id == "A3"
    assert fill_activities[2].lot_id == "A1", "LPT should end with smallest lot"


# ============================================================================
# Smart-Pack Strategy Tests
# ============================================================================


def test_smart_pack_produces_valid_schedule(simple_lots, cfg):
    """Test that smart-pack produces a valid schedule."""
    start_time = datetime.fromisoformat(cfg.START_TIME_STR)
    activities, makespan, kpis = plan_schedule(simple_lots, start_time, cfg, strategy="smart-pack")

    assert len(activities) > 0
    assert makespan > 0

    fill_activities = [a for a in activities if a.kind == "FILL"]
    assert len(fill_activities) == len(simple_lots)


def test_smart_pack_groups_same_types(cfg):
    """Test that smart-pack tends to group same types to minimize changeovers."""
    fill_rate = cfg.FILL_RATE_VPH
    lots = [
        Lot(lot_id="A1", lot_type="TypeX", vials=500000, fill_hours=500000 / fill_rate),
        Lot(lot_id="A2", lot_type="TypeX", vials=500000, fill_hours=500000 / fill_rate),
        Lot(lot_id="B1", lot_type="TypeY", vials=500000, fill_hours=500000 / fill_rate),
        Lot(lot_id="B2", lot_type="TypeY", vials=500000, fill_hours=500000 / fill_rate),
    ]

    start_time = datetime.fromisoformat(cfg.START_TIME_STR)
    activities, _, _ = plan_schedule(lots, start_time, cfg, strategy="smart-pack")

    fill_activities = [a for a in activities if a.kind == "FILL"]
    types_in_order = [a.lot_type for a in fill_activities]

    # Count type transitions
    transitions = sum(
        1 for i in range(1, len(types_in_order)) if types_in_order[i] != types_in_order[i - 1]
    )

    # Smart-pack should minimize transitions (ideally ≤ 1)
    assert transitions <= 1, f"Smart-pack should group types, got {transitions} transitions"


# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.parametrize(
    "strategy", ["smart-pack", "spt-pack", "lpt-pack", "cfs-pack", "hybrid-pack"]
)
def test_single_lot(cfg, strategy):
    """Test that all strategies handle single-lot case."""
    fill_rate = cfg.FILL_RATE_VPH
    lots = [Lot(lot_id="ONLY", lot_type="TypeA", vials=500000, fill_hours=500000 / fill_rate)]
    start_time = datetime.fromisoformat(cfg.START_TIME_STR)

    activities, _, _ = plan_schedule(lots, start_time, cfg, strategy=strategy)
    fills = [a for a in activities if a.kind == "FILL"]

    assert len(fills) == 1, f"{strategy} failed single-lot test"
    assert fills[0].lot_id == "ONLY"


@pytest.mark.parametrize("strategy", ["smart-pack", "spt-pack", "lpt-pack"])
def test_empty_lots_list(cfg, strategy):
    """Test handling of empty lots list."""
    lots = []
    start_time = datetime.fromisoformat(cfg.START_TIME_STR)

    activities, _, _ = plan_schedule(lots, start_time, cfg, strategy=strategy)
    fills = [a for a in activities if a.kind == "FILL"]

    # Should have no fill activities
    assert len(fills) == 0, f"{strategy} should produce no fills for empty input"


# ============================================================================
# Determinism Tests
# ============================================================================


@pytest.mark.parametrize("strategy", ["smart-pack", "spt-pack", "lpt-pack"])
def test_strategies_are_deterministic(simple_lots, cfg, strategy):
    """Test that strategies produce deterministic results."""
    start_time = datetime.fromisoformat(cfg.START_TIME_STR)

    # Run twice
    activities1, _, _ = plan_schedule(simple_lots, start_time, cfg, strategy=strategy)
    activities2, _, _ = plan_schedule(simple_lots, start_time, cfg, strategy=strategy)

    # Should be identical
    assert len(activities1) == len(activities2), f"{strategy} not deterministic (length)"

    for a1, a2 in zip(activities1, activities2, strict=False):
        assert a1.kind == a2.kind, f"{strategy} not deterministic (type)"
        assert a1.lot_id == a2.lot_id, f"{strategy} not deterministic (lot_id)"
        assert a1.lot_type == a2.lot_type, f"{strategy} not deterministic (lot_type)"


# ============================================================================
# Performance Comparison
# ============================================================================


def test_strategies_produce_different_schedules(varied_lots, cfg):
    """Test that different strategies produce different orderings."""
    start_time = datetime.fromisoformat(cfg.START_TIME_STR)

    spt_acts, _, _ = plan_schedule(varied_lots, start_time, cfg, strategy="spt-pack")
    lpt_acts, _, _ = plan_schedule(varied_lots, start_time, cfg, strategy="lpt-pack")

    spt_fills = [a for a in spt_acts if a.kind == "FILL"]
    lpt_fills = [a for a in lpt_acts if a.kind == "FILL"]

    spt_order = [a.lot_id for a in spt_fills]
    lpt_order = [a.lot_id for a in lpt_fills]

    # SPT and LPT should produce different orderings
    assert spt_order != lpt_order, "SPT and LPT should differ"

    # SPT first lot should be smallest
    # LPT first lot should be largest
    assert spt_order[0] == "S1", "SPT should start with smallest"
    assert lpt_order[0] == "L1", "LPT should start with largest"
