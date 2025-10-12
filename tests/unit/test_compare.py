"""
Unit tests for compare module.
Tests multi-strategy comparison functionality.
"""

import pandas as pd
import pytest

from fillscheduler.compare import (
    _delta_to_given_df,
    _kpi_float,
    _kpis_to_row,
    compare_multi_strategies,
)
from fillscheduler.config import AppConfig


@pytest.fixture
def sample_lots_csv(tmp_path):
    """Create a sample lots CSV file for comparison tests."""
    csv_path = tmp_path / "lots.csv"
    csv_content = """Lot ID,Type,Vials
L001,TypeA,1000
L002,TypeB,2000
L003,TypeA,1500
L004,TypeB,1000"""
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def sample_kpis():
    """Create sample KPIs dictionary."""
    return {
        "Makespan (h)": "24.5",
        "Total Clean (h)": "2.0",
        "Total Changeover (h)": "1.5",
        "Total Fill (h)": "21.0",
        "Lots Scheduled": "4",
        "Clean Blocks": "2",
    }


@pytest.fixture
def sample_kpis_optimized():
    """Create sample optimized KPIs dictionary."""
    return {
        "Makespan (h)": "22.0",
        "Total Clean (h)": "2.0",
        "Total Changeover (h)": "1.0",
        "Total Fill (h)": "19.0",
        "Lots Scheduled": "4",
        "Clean Blocks": "2",
    }


class TestKpiFloat:
    """Tests for _kpi_float helper function."""

    def test_convert_valid_float_string(self):
        """Test converting valid float string."""
        assert _kpi_float("24.5") == 24.5
        assert _kpi_float("0") == 0.0
        assert _kpi_float("100.123") == 100.123

    def test_convert_invalid_string(self):
        """Test converting invalid string returns nan."""
        import math

        result = _kpi_float("not a number")
        assert math.isnan(result)

    def test_convert_empty_string(self):
        """Test converting empty string returns nan."""
        import math

        result = _kpi_float("")
        assert math.isnan(result)


class TestKpisToRow:
    """Tests for _kpis_to_row helper function."""

    def test_convert_kpis_to_row(self, sample_kpis):
        """Test converting KPIs dict to row dict."""
        row = _kpis_to_row("Test Run", sample_kpis)

        assert row["Run"] == "Test Run"
        assert row["Makespan (h)"] == "24.5"
        assert row["Total Clean (h)"] == "2.0"
        assert row["Lots Scheduled"] == "4"

    def test_convert_kpis_with_missing_keys(self):
        """Test converting KPIs with missing keys."""
        kpis = {"Makespan (h)": "24.5"}  # Missing other keys
        row = _kpis_to_row("Test Run", kpis)

        assert row["Run"] == "Test Run"
        assert row["Makespan (h)"] == "24.5"
        assert row["Total Clean (h)"] == ""  # Missing keys get empty string

    def test_convert_empty_kpis(self):
        """Test converting empty KPIs dict."""
        row = _kpis_to_row("Empty Run", {})

        assert row["Run"] == "Empty Run"
        # All KPI keys should be present with empty strings
        assert all(
            key in row
            for key in [
                "Makespan (h)",
                "Total Clean (h)",
                "Total Changeover (h)",
                "Total Fill (h)",
                "Lots Scheduled",
                "Clean Blocks",
            ]
        )


class TestDeltaToGivenDf:
    """Tests for _delta_to_given_df helper function."""

    def test_calculate_deltas(self, sample_kpis, sample_kpis_optimized):
        """Test calculating deltas between given and optimized."""
        df = _delta_to_given_df(sample_kpis, sample_kpis_optimized, "Optimized")

        assert len(df) == 6  # Number of KPI keys
        assert list(df.columns) == ["Metric", "Given", "Optimized", "Delta (Optimized - Given)"]

    def test_delta_calculation_for_hours(self, sample_kpis, sample_kpis_optimized):
        """Test that deltas are calculated for hour metrics."""
        df = _delta_to_given_df(sample_kpis, sample_kpis_optimized, "Optimized")

        # Find Makespan row
        makespan_row = df[df["Metric"] == "Makespan (h)"].iloc[0]
        assert makespan_row["Given"] == "24.5"
        assert makespan_row["Optimized"] == "22.0"
        assert makespan_row["Delta (Optimized - Given)"] == "-2.50"  # 22.0 - 24.5

    def test_no_delta_for_non_hour_metrics(self, sample_kpis, sample_kpis_optimized):
        """Test that non-hour metrics don't get delta calculation."""
        df = _delta_to_given_df(sample_kpis, sample_kpis_optimized, "Optimized")

        # Find Lots Scheduled row (not an hour metric)
        lots_row = df[df["Metric"] == "Lots Scheduled"].iloc[0]
        assert lots_row["Given"] == "4"
        assert lots_row["Optimized"] == "4"
        assert lots_row["Delta (Optimized - Given)"] == ""  # No delta for non-hour metrics

    def test_delta_with_missing_values(self):
        """Test delta calculation with missing KPI values."""
        given = {"Makespan (h)": "24.5"}
        other = {"Makespan (h)": ""}  # Missing value

        df = _delta_to_given_df(given, other, "Test")

        # Should handle missing values gracefully
        assert len(df) == 6


class TestCompareMultiStrategies:
    """Tests for compare_multi_strategies function."""

    def test_compare_single_strategy(self, sample_lots_csv, tmp_path):
        """Test comparison with single strategy."""
        cfg = AppConfig()
        outdir = tmp_path / "output"
        strategies = ["smart-pack"]

        kpis_csv, multi_html = compare_multi_strategies(sample_lots_csv, outdir, cfg, strategies)

        assert kpis_csv.exists()
        assert multi_html.exists()
        assert kpis_csv.name == "kpis_all_runs.csv"
        assert multi_html.name == "comparison_all_in_one.html"

    def test_compare_multiple_strategies(self, sample_lots_csv, tmp_path):
        """Test comparison with multiple strategies."""
        cfg = AppConfig()
        outdir = tmp_path / "output"
        strategies = ["smart-pack", "spt-pack", "lpt-pack"]

        kpis_csv, multi_html = compare_multi_strategies(sample_lots_csv, outdir, cfg, strategies)

        # Check KPIs CSV contains all runs
        df = pd.read_csv(kpis_csv)
        assert len(df) == 4  # Given + 3 strategies
        assert df["Run"].iloc[0] == "Given (CSV Order)"
        assert "Optimized (smart-pack)" in df["Run"].values
        assert "Optimized (spt-pack)" in df["Run"].values
        assert "Optimized (lpt-pack)" in df["Run"].values

    def test_compare_creates_output_directory(self, sample_lots_csv, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        cfg = AppConfig()
        outdir = tmp_path / "nonexistent" / "output"
        strategies = ["smart-pack"]

        assert not outdir.exists()

        compare_multi_strategies(sample_lots_csv, outdir, cfg, strategies)

        assert outdir.exists()

    def test_compare_generates_individual_schedules(self, sample_lots_csv, tmp_path):
        """Test that individual schedule CSVs are generated per strategy."""
        cfg = AppConfig()
        outdir = tmp_path / "output"
        strategies = ["smart-pack", "spt-pack"]

        compare_multi_strategies(sample_lots_csv, outdir, cfg, strategies)

        # Check individual schedule files
        assert (outdir / "optimized_schedule_smart_pack.csv").exists()
        assert (outdir / "optimized_schedule_spt_pack.csv").exists()

    def test_html_report_contains_all_sections(self, sample_lots_csv, tmp_path):
        """Test that HTML report contains all required sections."""
        cfg = AppConfig()
        outdir = tmp_path / "output"
        strategies = ["smart-pack"]

        _, multi_html = compare_multi_strategies(sample_lots_csv, outdir, cfg, strategies)

        content = multi_html.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "Consolidated Comparison" in content
        assert "KPIs — All Runs" in content
        assert "Delta to Given" in content
        assert "Schedules" in content
        assert "Given Schedule (CSV order)" in content

    def test_html_report_collapsible_sections(self, sample_lots_csv, tmp_path):
        """Test that HTML report uses collapsible details sections."""
        cfg = AppConfig()
        outdir = tmp_path / "output"
        strategies = ["smart-pack", "spt-pack"]

        _, multi_html = compare_multi_strategies(sample_lots_csv, outdir, cfg, strategies)

        content = multi_html.read_text(encoding="utf-8")
        assert "<details" in content
        assert "<summary>" in content
        # Given schedule should be open by default
        assert "<details open>" in content

    def test_html_report_includes_delta_tables(self, sample_lots_csv, tmp_path):
        """Test that HTML report includes delta comparison tables."""
        cfg = AppConfig()
        outdir = tmp_path / "output"
        strategies = ["smart-pack"]

        _, multi_html = compare_multi_strategies(sample_lots_csv, outdir, cfg, strategies)

        content = multi_html.read_text(encoding="utf-8")
        assert "Delta to Given" in content
        assert "smart-pack" in content

    def test_kpis_csv_structure(self, sample_lots_csv, tmp_path):
        """Test that KPIs CSV has correct structure."""
        cfg = AppConfig()
        outdir = tmp_path / "output"
        strategies = ["smart-pack"]

        kpis_csv, _ = compare_multi_strategies(sample_lots_csv, outdir, cfg, strategies)

        df = pd.read_csv(kpis_csv)
        expected_columns = [
            "Run",
            "Makespan (h)",
            "Total Clean (h)",
            "Total Changeover (h)",
            "Total Fill (h)",
            "Lots Scheduled",
            "Clean Blocks",
        ]
        assert list(df.columns) == expected_columns

    def test_compare_with_empty_strategies_list(self, sample_lots_csv, tmp_path):
        """Test comparison with empty strategies list (only given schedule)."""
        cfg = AppConfig()
        outdir = tmp_path / "output"

        kpis_csv, multi_html = compare_multi_strategies(sample_lots_csv, outdir, cfg, [])

        # Should still generate reports with just the given schedule
        assert kpis_csv.exists()
        assert multi_html.exists()

        df = pd.read_csv(kpis_csv)
        assert len(df) == 1  # Only Given schedule
        assert df["Run"].iloc[0] == "Given (CSV Order)"
