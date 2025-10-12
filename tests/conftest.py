# tests/conftest.py
from pathlib import Path

import pandas as pd
import pytest

from fillscheduler.config import AppConfig
from fillscheduler.io_utils import read_lots_with_pandas


@pytest.fixture
def cfg() -> AppConfig:
    # Default config
    return AppConfig()


def write_csv(tmp_path: Path, rows, columns=("Lot ID", "Type", "Vials")) -> Path:
    df = pd.DataFrame(rows, columns=columns)
    p = tmp_path / "lots.csv"
    df.to_csv(p, index=False)
    return p


@pytest.fixture
def csv_writer(tmp_path):
    """Helper to quickly create CSVs in tests."""

    def _writer(rows, columns=("Lot ID", "Type", "Vials")) -> Path:
        return write_csv(tmp_path, rows, columns)

    return _writer


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Path to the test fixtures directory containing sample CSV files.

    Returns:
        Path: Absolute path to tests/fixtures/ directory

    Example:
        def test_with_fixture(fixtures_dir):
            lots_path = fixtures_dir / "simple_lots.csv"
            lots = read_lots_with_pandas(lots_path, cfg)
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def fixture_files(fixtures_dir) -> dict:
    """Dictionary of all available fixture files categorized by type.

    Returns:
        dict: Nested dictionary with categories and file paths

    Example:
        def test_all_valid_fixtures(fixture_files):
            for fixture_path in fixture_files['valid']['basic']:
                # Test with fixture...
    """
    return {
        "valid": {
            "basic": [
                fixtures_dir / "simple_lots.csv",
                fixtures_dir / "single_lot.csv",
                fixtures_dir / "same_type_lots.csv",
                fixtures_dir / "all_different_types.csv",
                fixtures_dir / "mixed_types.csv",
            ],
            "size_variations": [
                fixtures_dir / "small_lots.csv",
                fixtures_dir / "large_lots.csv",
                fixtures_dir / "varied_sizes.csv",
            ],
            "ordering": [
                fixtures_dir / "unsorted_lots.csv",
                fixtures_dir / "priority_lots.csv",
            ],
        },
        "sequences": [
            fixtures_dir / "sequence.csv",
            fixtures_dir / "sequence_alternate_column.csv",
            fixtures_dir / "partial_sequence.csv",
        ],
        "invalid": {
            "blank_fields": [
                fixtures_dir / "invalid_blank_id.csv",
                fixtures_dir / "invalid_blank_type.csv",
            ],
            "missing_data": [
                fixtures_dir / "invalid_missing_vials.csv",
                fixtures_dir / "invalid_missing_column.csv",
                fixtures_dir / "empty_lots.csv",
            ],
            "invalid_values": [
                fixtures_dir / "invalid_negative_vials.csv",
                fixtures_dir / "duplicate_ids.csv",
            ],
        },
    }


@pytest.fixture
def load_lots(csv_writer, cfg):
    """Helper to (write → read) lots using the project reader, so we test the NaN handling too."""

    def _load(rows, columns=("Lot ID", "Type", "Vials")):
        path = csv_writer(rows, columns)
        return read_lots_with_pandas(path, cfg)

    return _load
