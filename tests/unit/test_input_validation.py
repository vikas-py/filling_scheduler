# tests/test_input_validation.py
import pytest

from fillscheduler.config import AppConfig
from fillscheduler.validate import validate_input_lots


def test_blank_lot_id_is_error(load_lots, cfg: AppConfig):
    # Lot ID is blank → becomes "" via fillna/astype(str), must error
    lots = load_lots(
        [
            ["", "VialE", 1000],
            ["A2", "VialH", 5000],
        ]
    )
    # Do not exit the test process: collect errors via raise_exceptions + fail_fast=False
    errors, warnings = validate_input_lots(lots, cfg, fail_fast=False, raise_exceptions=False)
    assert any("empty Lot ID" in e for e in errors)


def test_nan_lot_id_is_error(load_lots, cfg: AppConfig):
    # NaN in Lot ID column → reader should convert to "" and validator should error
    import numpy as np

    lots = load_lots(
        [
            [np.nan, "VialE", 1000],
            ["A2", "VialH", 5000],
        ]
    )
    errors, warnings = validate_input_lots(lots, cfg, fail_fast=False, raise_exceptions=False)
    assert any("empty Lot ID" in e for e in errors)


def test_blank_type_is_error(load_lots, cfg: AppConfig):
    lots = load_lots(
        [
            ["A1", "", 1000],
        ]
    )
    errors, warnings = validate_input_lots(lots, cfg, fail_fast=False)
    assert any("empty Type" in e for e in errors)


def test_missing_vials_is_error(csv_writer, cfg: AppConfig):
    # Missing vials cell should be caught by io_utils read (raises ValueError)
    from fillscheduler.io_utils import read_lots_with_pandas

    path = csv_writer([["A1", "VialE", None]])
    with pytest.raises(ValueError):
        read_lots_with_pandas(path, cfg)


def test_zero_or_negative_vials(load_lots, cfg: AppConfig):
    lots = load_lots(
        [
            ["A1", "VialE", 0],
            ["A2", "VialH", -5],
        ]
    )
    errors, warnings = validate_input_lots(lots, cfg, fail_fast=False)
    assert any("Vials must be a positive integer" in e for e in errors)
    assert len(errors) >= 2  # both rows invalid


def test_duplicate_lot_ids_warn(load_lots, cfg: AppConfig):
    lots = load_lots(
        [
            ["A1", "VialE", 1000],
            ["A1", "VialH", 2000],
        ]
    )
    errors, warnings = validate_input_lots(lots, cfg, fail_fast=False)
    assert not errors
    assert any("Duplicate Lot ID" in w for w in warnings)


def test_oversize_lot_strict_error(load_lots, cfg: AppConfig):
    # Make a huge lot that exceeds 120h
    max_vials = int(cfg.WINDOW_HOURS * cfg.FILL_RATE_VPH)  # 2,390,400 default
    huge = max_vials * 10
    lots = load_lots(
        [
            ["HUGE", "VialH", huge],
        ]
    )
    errors, warnings = validate_input_lots(lots, cfg, fail_fast=False)
    assert any("exceeds the 120 h clean window" in e for e in errors)


def test_config_sanity_errors(cfg: AppConfig, load_lots):
    # Bad config values should trigger input validation errors
    bad = AppConfig(
        DATA_PATH=cfg.DATA_PATH,
        OUTPUT_DIR=cfg.OUTPUT_DIR,
        START_TIME_STR=cfg.START_TIME_STR,
        STRATEGY=cfg.STRATEGY,
        INTERACTIVE=False,
        FILL_RATE_VPH=0.0,  # invalid
        CLEAN_HOURS=-1.0,  # invalid
        WINDOW_HOURS=0.0,  # invalid
    )
    lots = load_lots([["A1", "VialE", 1000]])
    errors, warnings = validate_input_lots(lots, bad, fail_fast=False)
    assert any("FILL_RATE_VPH must be > 0" in e for e in errors)
    assert any("CLEAN_HOURS must be > 0" in e for e in errors)
    assert any("WINDOW_HOURS must be > 0" in e for e in errors)
