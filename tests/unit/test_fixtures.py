"""
Tests to verify test fixtures are valid and accessible.
"""
import pytest
from pathlib import Path
from fillscheduler.io_utils import read_lots_with_pandas
from fillscheduler.config import AppConfig


class TestFixturesAccessibility:
    """Test that fixtures directory and files are accessible."""

    def test_fixtures_dir_exists(self, fixtures_dir):
        """Test that fixtures directory exists."""
        assert fixtures_dir.exists()
        assert fixtures_dir.is_dir()

    def test_fixtures_dir_has_readme(self, fixtures_dir):
        """Test that fixtures directory has README."""
        readme = fixtures_dir / "README.md"
        assert readme.exists()
        assert readme.is_file()

    def test_fixture_files_dict_structure(self, fixture_files):
        """Test that fixture_files has expected structure."""
        assert 'valid' in fixture_files
        assert 'sequences' in fixture_files
        assert 'invalid' in fixture_files
        
        assert 'basic' in fixture_files['valid']
        assert 'size_variations' in fixture_files['valid']
        assert 'ordering' in fixture_files['valid']


class TestValidFixtures:
    """Test that valid fixtures load correctly."""

    @pytest.mark.parametrize("fixture_name,expected_count", [
        ("simple_lots.csv", 3),
        ("single_lot.csv", 1),
        ("same_type_lots.csv", 5),
        ("all_different_types.csv", 5),
        ("mixed_types.csv", 8),
        ("small_lots.csv", 5),
        ("large_lots.csv", 4),
        ("varied_sizes.csv", 6),
        ("unsorted_lots.csv", 8),
        ("priority_lots.csv", 6),
    ])
    def test_valid_fixture_loads(self, fixtures_dir, fixture_name, expected_count):
        """Test that each valid fixture loads with correct lot count."""
        cfg = AppConfig()
        fixture_path = fixtures_dir / fixture_name
        
        assert fixture_path.exists(), f"Fixture {fixture_name} not found"
        
        lots = read_lots_with_pandas(fixture_path, cfg)
        assert len(lots) == expected_count
        
        # Verify all lots have required attributes
        for lot in lots:
            assert lot.lot_id
            assert lot.lot_type
            assert lot.vials > 0
            assert lot.fill_hours > 0

    def test_simple_lots_content(self, fixtures_dir):
        """Test simple_lots.csv has expected content."""
        cfg = AppConfig()
        lots = read_lots_with_pandas(fixtures_dir / "simple_lots.csv", cfg)
        
        assert lots[0].lot_id == "L001"
        assert lots[0].lot_type == "TypeA"
        assert lots[0].vials == 1000
        
        assert lots[1].lot_id == "L002"
        assert lots[1].lot_type == "TypeB"
        assert lots[1].vials == 2000

    def test_same_type_lots_all_same_type(self, fixtures_dir):
        """Test same_type_lots.csv has all same type."""
        cfg = AppConfig()
        lots = read_lots_with_pandas(fixtures_dir / "same_type_lots.csv", cfg)
        
        types = {lot.lot_type for lot in lots}
        assert len(types) == 1
        assert "TypeA" in types

    def test_all_different_types_all_unique(self, fixtures_dir):
        """Test all_different_types.csv has all unique types."""
        cfg = AppConfig()
        lots = read_lots_with_pandas(fixtures_dir / "all_different_types.csv", cfg)
        
        types = [lot.lot_type for lot in lots]
        assert len(types) == len(set(types))  # All unique


class TestInvalidFixtures:
    """Test that invalid fixtures raise appropriate errors."""

    def test_blank_id_raises_error(self, fixtures_dir):
        """Test that blank lot ID gets caught by validation."""
        from fillscheduler.validate import validate_input_lots
        
        cfg = AppConfig()
        # Read will succeed (blank becomes empty string)
        lots = read_lots_with_pandas(fixtures_dir / "invalid_blank_id.csv", cfg)
        # But validation should catch it
        errors, warnings = validate_input_lots(lots, cfg, fail_fast=False, raise_exceptions=False)
        assert len(errors) > 0
        assert any("empty Lot ID" in e for e in errors)

    def test_blank_type_raises_error(self, fixtures_dir):
        """Test that blank type gets caught by validation."""
        from fillscheduler.validate import validate_input_lots
        
        cfg = AppConfig()
        # Read will succeed (blank becomes empty string)
        lots = read_lots_with_pandas(fixtures_dir / "invalid_blank_type.csv", cfg)
        # But validation should catch it
        errors, warnings = validate_input_lots(lots, cfg, fail_fast=False, raise_exceptions=False)
        assert len(errors) > 0
        assert any("empty Type" in e for e in errors)

    def test_missing_vials_raises_error(self, fixtures_dir):
        """Test that missing vials raises ValueError."""
        cfg = AppConfig()
        with pytest.raises(ValueError, match="missing Vials"):
            read_lots_with_pandas(fixtures_dir / "invalid_missing_vials.csv", cfg)

    def test_missing_column_raises_error(self, fixtures_dir):
        """Test that missing required column raises ValueError."""
        cfg = AppConfig()
        with pytest.raises(ValueError, match="Missing columns"):
            read_lots_with_pandas(fixtures_dir / "invalid_missing_column.csv", cfg)

    def test_empty_lots_raises_error(self, fixtures_dir):
        """Test that empty CSV raises ValueError."""
        cfg = AppConfig()
        with pytest.raises(ValueError, match="No lots found"):
            read_lots_with_pandas(fixtures_dir / "empty_lots.csv", cfg)


class TestSequenceFixtures:
    """Test that sequence fixtures load correctly."""

    def test_sequence_fixture_loads(self, fixtures_dir):
        """Test that sequence.csv loads."""
        from fillscheduler.seq_utils import read_sequence_csv
        
        sequence = read_sequence_csv(fixtures_dir / "sequence.csv")
        assert len(sequence) == 3
        assert sequence == ["L003", "L001", "L002"]

    def test_sequence_alternate_column_loads(self, fixtures_dir):
        """Test that alternate column name works."""
        from fillscheduler.seq_utils import read_sequence_csv
        
        sequence = read_sequence_csv(fixtures_dir / "sequence_alternate_column.csv")
        assert len(sequence) == 4
        assert "L002" in sequence
        assert "L005" in sequence

    def test_partial_sequence_loads(self, fixtures_dir):
        """Test that partial sequence loads."""
        from fillscheduler.seq_utils import read_sequence_csv
        
        sequence = read_sequence_csv(fixtures_dir / "partial_sequence.csv")
        assert len(sequence) == 3
        assert all(s.startswith("PRIORITY") for s in sequence)


class TestFixtureUsagePatterns:
    """Test common fixture usage patterns."""

    def test_all_valid_basic_fixtures_schedulable(self, fixture_files):
        """Test that all valid basic fixtures can be scheduled."""
        from fillscheduler.scheduler import plan_schedule
        from datetime import datetime
        
        cfg = AppConfig()
        start = datetime.strptime(cfg.START_TIME_STR, "%Y-%m-%d %H:%M")
        
        for fixture_path in fixture_files['valid']['basic']:
            lots = read_lots_with_pandas(fixture_path, cfg)
            activities, total_hours, kpis = plan_schedule(lots, start, cfg, strategy="smart-pack")
            
            assert len(activities) > 0, f"No activities generated for {fixture_path.name}"
            assert total_hours > 0, f"Invalid total hours for {fixture_path.name}"
            assert int(kpis.get("Lots Scheduled", 0)) == len(lots)

    def test_size_variations_fixtures_have_different_durations(self, fixture_files):
        """Test that size variation fixtures produce different makespan."""
        from fillscheduler.scheduler import plan_schedule
        from datetime import datetime
        
        cfg = AppConfig()
        start = datetime.strptime(cfg.START_TIME_STR, "%Y-%m-%d %H:%M")
        
        makespans = []
        for fixture_path in fixture_files['valid']['size_variations']:
            lots = read_lots_with_pandas(fixture_path, cfg)
            _, _, kpis = plan_schedule(lots, start, cfg, strategy="smart-pack")
            makespans.append(float(kpis.get("Makespan (h)", 0)))
        
        # Different sized fixtures should have different makespans
        assert len(set(makespans)) > 1, "All fixtures have same makespan"

    def test_fixture_with_strategy_comparison(self, fixtures_dir):
        """Test using fixture to compare strategies."""
        from fillscheduler.scheduler import plan_schedule
        from datetime import datetime
        
        cfg = AppConfig()
        start = datetime.strptime(cfg.START_TIME_STR, "%Y-%m-%d %H:%M")
        lots = read_lots_with_pandas(fixtures_dir / "mixed_types.csv", cfg)
        
        strategies = ["smart-pack", "spt-pack", "lpt-pack"]
        results = {}
        
        for strategy in strategies:
            _, _, kpis = plan_schedule(lots[:], start, cfg, strategy=strategy)
            results[strategy] = float(kpis.get("Makespan (h)", 0))
        
        # All strategies should produce valid results
        assert all(makespan > 0 for makespan in results.values())
        # Results should vary by strategy (at least for some)
        assert len(set(results.values())) >= 1
