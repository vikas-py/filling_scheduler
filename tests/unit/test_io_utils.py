"""
Unit tests for io_utils module.
Tests CSV reading, dataframe conversion, and file writing operations.
"""

from datetime import datetime

import pandas as pd
import pytest

from fillscheduler.config import AppConfig
from fillscheduler.io_utils import (
    activities_to_dataframe,
    read_lots_with_pandas,
    write_schedule_with_pandas,
    write_summary_txt,
)
from fillscheduler.models import Activity


@pytest.fixture
def sample_lots_csv(tmp_path):
    """Create a sample lots CSV file."""
    csv_path = tmp_path / "lots.csv"
    csv_content = """Lot ID,Type,Vials
L001,TypeA,1000
L002,TypeB,2000
L003,TypeA,1500"""
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def invalid_lots_csv(tmp_path):
    """Create an invalid lots CSV file missing required columns."""
    csv_path = tmp_path / "invalid_lots.csv"
    csv_content = """Lot ID,Vials
L001,1000"""
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def lots_csv_with_nulls(tmp_path):
    """Create a lots CSV with null vials."""
    csv_path = tmp_path / "lots_nulls.csv"
    csv_content = """Lot ID,Type,Vials
L001,TypeA,1000
L002,TypeB,"""
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def empty_lots_csv(tmp_path):
    """Create an empty lots CSV file."""
    csv_path = tmp_path / "empty_lots.csv"
    csv_content = """Lot ID,Type,Vials"""
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def sample_activities():
    """Create sample activities."""
    cfg = AppConfig()
    start = datetime.strptime(cfg.START_TIME_STR, "%Y-%m-%d %H:%M")  # 2025-01-01 08:00
    return [
        Activity(
            start=start,
            end=datetime(2025, 1, 1, 10, 0),  # 08:00 to 10:00 = 2 hours
            kind="CLEAN",
            lot_id=None,
            lot_type=None,
            note="Initial clean",
        ),
        Activity(
            start=datetime(2025, 1, 1, 10, 0),
            end=datetime(2025, 1, 1, 12, 0),  # 10:00 to 12:00 = 2 hours
            kind="FILL",
            lot_id="L001",
            lot_type="TypeA",
            note=None,
        ),
    ]


class TestReadLotsWithPandas:
    """Tests for read_lots_with_pandas function."""

    def test_read_valid_csv(self, sample_lots_csv):
        """Test reading a valid lots CSV file."""
        cfg = AppConfig()
        lots = read_lots_with_pandas(sample_lots_csv, cfg)

        assert len(lots) == 3
        assert lots[0].lot_id == "L001"
        assert lots[0].lot_type == "TypeA"
        assert lots[0].vials == 1000
        assert lots[1].lot_id == "L002"
        assert lots[2].lot_id == "L003"

    def test_read_csv_calculates_fill_hours(self, sample_lots_csv):
        """Test that fill hours are calculated correctly."""
        cfg = AppConfig()
        lots = read_lots_with_pandas(sample_lots_csv, cfg)

        # With default FILL_RATE_VPH = 332 * 60 = 19920
        assert lots[0].fill_hours == pytest.approx(1000 / 19920)
        assert lots[1].fill_hours == pytest.approx(2000 / 19920)

    def test_read_csv_missing_columns(self, invalid_lots_csv):
        """Test that missing columns raise ValueError."""
        cfg = AppConfig()
        with pytest.raises(ValueError, match="Missing columns in CSV"):
            read_lots_with_pandas(invalid_lots_csv, cfg)

    def test_read_csv_with_null_vials(self, lots_csv_with_nulls):
        """Test that null vials raise ValueError."""
        cfg = AppConfig()
        with pytest.raises(ValueError, match="missing Vials values"):
            read_lots_with_pandas(lots_csv_with_nulls, cfg)

    def test_read_empty_csv(self, empty_lots_csv):
        """Test that empty CSV raises ValueError."""
        cfg = AppConfig()
        with pytest.raises(ValueError, match="No lots found"):
            read_lots_with_pandas(empty_lots_csv, cfg)

    def test_read_csv_strips_whitespace(self, tmp_path):
        """Test that whitespace is stripped from text fields."""
        csv_path = tmp_path / "lots_whitespace.csv"
        csv_content = """Lot ID,Type,Vials
  L001  ,  TypeA  ,1000"""
        csv_path.write_text(csv_content)

        cfg = AppConfig()
        lots = read_lots_with_pandas(csv_path, cfg)

        assert lots[0].lot_id == "L001"
        assert lots[0].lot_type == "TypeA"


class TestActivitiesToDataframe:
    """Tests for activities_to_dataframe function."""

    def test_convert_activities_to_dataframe(self, sample_activities):
        """Test converting activities to dataframe."""
        cfg = AppConfig()
        df = activities_to_dataframe(sample_activities, cfg)

        assert len(df) == 2
        assert list(df.columns) == ["Start", "End", "Hours", "Activity", "Lot ID", "Type", "Note"]
        assert df.iloc[0]["Activity"] == "CLEAN"
        assert df.iloc[1]["Activity"] == "FILL"
        assert df.iloc[1]["Lot ID"] == "L001"

    def test_dataframe_calculates_hours(self, sample_activities):
        """Test that hours are calculated correctly."""
        cfg = AppConfig()
        df = activities_to_dataframe(sample_activities, cfg)

        assert df.iloc[0]["Hours"] == 2.0  # 2 hours for CLEAN
        assert df.iloc[1]["Hours"] == 2.0  # 2 hours for FILL

    def test_dataframe_formats_datetime(self, sample_activities):
        """Test that datetime is formatted according to config."""
        cfg = AppConfig()
        df = activities_to_dataframe(sample_activities, cfg)

        # Check format matches DATETIME_FMT
        assert "2025-01-01" in df.iloc[0]["Start"]
        assert "08:00" in df.iloc[0]["Start"]  # Start time from config is 08:00

    def test_empty_activities_list(self):
        """Test converting empty activities list."""
        cfg = AppConfig()
        df = activities_to_dataframe([], cfg)

        assert len(df) == 0
        assert list(df.columns) == ["Start", "End", "Hours", "Activity", "Lot ID", "Type", "Note"]


class TestWriteScheduleWithPandas:
    """Tests for write_schedule_with_pandas function."""

    def test_write_schedule_csv(self, sample_activities, tmp_path):
        """Test writing schedule to CSV file."""
        cfg = AppConfig()
        output_path = tmp_path / "schedule.csv"

        write_schedule_with_pandas(sample_activities, output_path, cfg)

        assert output_path.exists()
        df = pd.read_csv(output_path)
        assert len(df) == 2
        assert "Activity" in df.columns
        assert df.iloc[0]["Activity"] == "CLEAN"

    def test_write_schedule_with_default_config(self, sample_activities, tmp_path):
        """Test writing schedule with default config when None provided."""
        output_path = tmp_path / "schedule.csv"

        write_schedule_with_pandas(sample_activities, output_path, None)

        assert output_path.exists()

    def test_write_empty_schedule(self, tmp_path):
        """Test writing empty schedule."""
        cfg = AppConfig()
        output_path = tmp_path / "empty_schedule.csv"

        write_schedule_with_pandas([], output_path, cfg)

        assert output_path.exists()
        df = pd.read_csv(output_path)
        assert len(df) == 0


class TestWriteSummaryTxt:
    """Tests for write_summary_txt function."""

    def test_write_summary_with_all_sections(self, tmp_path):
        """Test writing summary with KPIs, errors, and warnings."""
        summary_path = tmp_path / "summary.txt"
        kpis = {"Makespan (h)": "24.5", "Lots Scheduled": "10"}
        errors = ["Error 1", "Error 2"]
        warnings = ["Warning 1"]

        write_summary_txt(kpis, errors, warnings, summary_path)

        assert summary_path.exists()
        content = summary_path.read_text()
        assert "=== Schedule Summary ===" in content
        assert "Makespan (h): 24.5" in content
        assert "=== Errors ===" in content
        assert "- Error 1" in content
        assert "=== Warnings ===" in content
        assert "- Warning 1" in content

    def test_write_summary_without_errors_warnings(self, tmp_path):
        """Test writing summary with only KPIs."""
        summary_path = tmp_path / "summary.txt"
        kpis = {"Makespan (h)": "24.5"}

        write_summary_txt(kpis, [], [], summary_path)

        content = summary_path.read_text()
        assert "=== Schedule Summary ===" in content
        assert "Makespan (h): 24.5" in content
        assert "=== Errors ===" not in content
        assert "=== Warnings ===" not in content

    def test_write_empty_summary(self, tmp_path):
        """Test writing summary with no data."""
        summary_path = tmp_path / "summary.txt"

        write_summary_txt({}, [], [], summary_path)

        assert summary_path.exists()
        content = summary_path.read_text()
        assert "=== Schedule Summary ===" in content
