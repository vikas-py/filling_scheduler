# tests/conftest.py
import pandas as pd
import pytest
from pathlib import Path

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


@pytest.fixture
def load_lots(csv_writer, cfg):
    """Helper to (write → read) lots using the project reader, so we test the NaN handling too."""
    def _load(rows, columns=("Lot ID", "Type", "Vials")):
        path = csv_writer(rows, columns)
        return read_lots_with_pandas(path, cfg)
    return _load
