"""
Unit tests for reporting module.
Tests HTML report generation and console output.
"""
from pathlib import Path
from datetime import datetime
import pytest
from fillscheduler.reporting import print_summary, write_html_report
from fillscheduler.models import Activity
from fillscheduler.config import AppConfig


@pytest.fixture
def sample_activities():
    """Create sample activities for reporting."""
    cfg = AppConfig()
    start = datetime.strptime(cfg.START_TIME_STR, "%Y-%m-%d %H:%M")
    return [
        Activity(
            start=start,
            end=datetime(2025, 1, 1, 2, 0),
            kind="CLEAN",
            lot_id=None,
            lot_type=None,
            note="Initial clean"
        ),
        Activity(
            start=datetime(2025, 1, 1, 2, 0),
            end=datetime(2025, 1, 1, 4, 0),
            kind="CHANGEOVER",
            lot_id=None,
            lot_type=None,
            note="TypeA to TypeB"
        ),
        Activity(
            start=datetime(2025, 1, 1, 4, 0),
            end=datetime(2025, 1, 1, 6, 0),
            kind="FILL",
            lot_id="L001",
            lot_type="TypeA",
            note=None
        ),
    ]


@pytest.fixture
def sample_kpis():
    """Create sample KPIs."""
    return {
        "Makespan (h)": "24.5",
        "Total Clean (h)": "2.0",
        "Total Changeover (h)": "1.5",
        "Total Fill (h)": "21.0",
        "Lots Scheduled": "10",
        "Clean Blocks": "2",
    }


class TestPrintSummary:
    """Tests for print_summary function."""

    def test_print_summary_with_all_data(self, capsys, sample_kpis, tmp_path):
        """Test printing summary with KPIs, errors, and warnings."""
        schedule_csv = tmp_path / "schedule.csv"
        summary_txt = tmp_path / "summary.txt"
        errors = ["Error 1", "Error 2"]
        warnings = ["Warning 1"]
        
        print_summary(sample_kpis, errors, warnings, schedule_csv, summary_txt)
        
        captured = capsys.readouterr()
        assert "=== Schedule KPIs ===" in captured.out
        assert "Makespan (h): 24.5" in captured.out
        assert "=== ERRORS ===" in captured.out
        assert "- Error 1" in captured.out
        assert "=== WARNINGS ===" in captured.out
        assert "- Warning 1" in captured.out
        assert "Saved schedule to:" in captured.out
        assert "Saved summary to :" in captured.out

    def test_print_summary_without_errors_warnings(self, capsys, sample_kpis, tmp_path):
        """Test printing summary with only KPIs."""
        schedule_csv = tmp_path / "schedule.csv"
        summary_txt = tmp_path / "summary.txt"
        
        print_summary(sample_kpis, [], [], schedule_csv, summary_txt)
        
        captured = capsys.readouterr()
        assert "=== Schedule KPIs ===" in captured.out
        assert "=== ERRORS ===" not in captured.out
        assert "=== WARNINGS ===" not in captured.out

    def test_print_summary_with_empty_kpis(self, capsys, tmp_path):
        """Test printing summary with empty KPIs."""
        schedule_csv = tmp_path / "schedule.csv"
        summary_txt = tmp_path / "summary.txt"
        
        print_summary({}, [], [], schedule_csv, summary_txt)
        
        captured = capsys.readouterr()
        assert "=== Schedule KPIs ===" in captured.out


class TestWriteHtmlReport:
    """Tests for write_html_report function."""

    def test_write_html_report_basic(self, sample_activities, sample_kpis, tmp_path):
        """Test writing basic HTML report."""
        cfg = AppConfig()
        html_path = tmp_path / "report.html"
        
        write_html_report(sample_activities, sample_kpis, [], [], html_path, cfg)
        
        assert html_path.exists()
        content = html_path.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "Filling Schedule Report" in content
        assert "Summary KPIs" in content
        assert "Schedule" in content

    def test_html_report_contains_kpis(self, sample_activities, sample_kpis, tmp_path):
        """Test that HTML report contains all KPIs."""
        cfg = AppConfig()
        html_path = tmp_path / "report.html"
        
        write_html_report(sample_activities, sample_kpis, [], [], html_path, cfg)
        
        content = html_path.read_text(encoding="utf-8")
        assert "Makespan (h)" in content
        assert "24.5" in content
        assert "Lots Scheduled" in content
        assert "10" in content

    def test_html_report_contains_schedule(self, sample_activities, sample_kpis, tmp_path):
        """Test that HTML report contains schedule activities."""
        cfg = AppConfig()
        html_path = tmp_path / "report.html"
        
        write_html_report(sample_activities, sample_kpis, [], [], html_path, cfg)
        
        content = html_path.read_text(encoding="utf-8")
        # Check for activity badges
        assert 'class="badge' in content
        assert "L001" in content  # Lot ID from FILL activity

    def test_html_report_with_errors(self, sample_activities, sample_kpis, tmp_path):
        """Test HTML report with errors."""
        cfg = AppConfig()
        html_path = tmp_path / "report.html"
        errors = ["Critical error 1", "Critical error 2"]
        
        write_html_report(sample_activities, sample_kpis, errors, [], html_path, cfg)
        
        content = html_path.read_text(encoding="utf-8")
        assert "Critical error 1" in content
        assert "Critical error 2" in content
        assert "class='errors'" in content

    def test_html_report_with_warnings(self, sample_activities, sample_kpis, tmp_path):
        """Test HTML report with warnings."""
        cfg = AppConfig()
        html_path = tmp_path / "report.html"
        warnings = ["Warning 1", "Warning 2"]
        
        write_html_report(sample_activities, sample_kpis, [], warnings, html_path, cfg)
        
        content = html_path.read_text(encoding="utf-8")
        assert "Warning 1" in content
        assert "Warning 2" in content
        assert "class='warnings'" in content

    def test_html_report_without_errors_warnings(self, sample_activities, sample_kpis, tmp_path):
        """Test HTML report with no errors or warnings."""
        cfg = AppConfig()
        html_path = tmp_path / "report.html"
        
        write_html_report(sample_activities, sample_kpis, [], [], html_path, cfg)
        
        content = html_path.read_text(encoding="utf-8")
        assert "No errors." in content
        assert "No warnings." in content

    def test_html_report_activity_badges(self, sample_activities, sample_kpis, tmp_path):
        """Test that HTML report uses badges for different activity types."""
        cfg = AppConfig()
        html_path = tmp_path / "report.html"
        
        write_html_report(sample_activities, sample_kpis, [], [], html_path, cfg)
        
        content = html_path.read_text(encoding="utf-8")
        # Check for badge CSS classes
        assert "b-clean" in content  # CLEAN badge
        assert "b-chg" in content    # CHANGEOVER badge
        assert "b-fill" in content   # FILL badge

    def test_html_report_css_styling(self, sample_activities, sample_kpis, tmp_path):
        """Test that HTML report includes CSS styling."""
        cfg = AppConfig()
        html_path = tmp_path / "report.html"
        
        write_html_report(sample_activities, sample_kpis, [], [], html_path, cfg)
        
        content = html_path.read_text(encoding="utf-8")
        assert "<style>" in content
        assert "font-family:" in content
        assert "table {" in content

    def test_html_report_with_empty_activities(self, sample_kpis, tmp_path):
        """Test HTML report with empty activities list."""
        cfg = AppConfig()
        html_path = tmp_path / "report.html"
        
        write_html_report([], sample_kpis, [], [], html_path, cfg)
        
        assert html_path.exists()
        content = html_path.read_text(encoding="utf-8")
        assert "Filling Schedule Report" in content

    def test_html_report_encoding(self, sample_activities, sample_kpis, tmp_path):
        """Test that HTML report is written with UTF-8 encoding."""
        cfg = AppConfig()
        html_path = tmp_path / "report.html"
        
        write_html_report(sample_activities, sample_kpis, [], [], html_path, cfg)
        
        # Read with UTF-8 encoding should work
        content = html_path.read_text(encoding="utf-8")
        assert '<meta charset="utf-8"' in content
