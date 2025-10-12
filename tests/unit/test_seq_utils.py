"""
Unit tests for seq_utils module.
Tests sequence reading and lot ordering operations.
"""

import pytest

from fillscheduler.models import Lot
from fillscheduler.seq_utils import order_lots_by_sequence, read_sequence_csv


@pytest.fixture
def sample_sequence_csv(tmp_path):
    """Create a sample sequence CSV file."""
    csv_path = tmp_path / "sequence.csv"
    csv_content = """Lot ID
L003
L001
L002"""
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def sequence_with_alternate_column(tmp_path):
    """Create sequence CSV with alternate column name."""
    csv_path = tmp_path / "sequence_alt.csv"
    csv_content = """LotID
L002
L003"""
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def sequence_with_blanks(tmp_path):
    """Create sequence CSV with blank entries."""
    csv_path = tmp_path / "sequence_blanks.csv"
    csv_content = """Lot ID
L001

L002
"""
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def sample_lots():
    """Create sample lots for ordering tests."""
    return [
        Lot("L001", "TypeA", 1000, 2.0),
        Lot("L002", "TypeB", 2000, 4.0),
        Lot("L003", "TypeA", 1500, 3.0),
        Lot("L004", "TypeC", 500, 1.0),
    ]


class TestReadSequenceCsv:
    """Tests for read_sequence_csv function."""

    def test_read_valid_sequence(self, sample_sequence_csv):
        """Test reading a valid sequence CSV."""
        sequence = read_sequence_csv(sample_sequence_csv)

        assert len(sequence) == 3
        assert sequence == ["L003", "L001", "L002"]

    def test_read_sequence_with_alternate_column_names(self, sequence_with_alternate_column):
        """Test reading sequence with alternate column names (LotID, lot_id, lotid)."""
        sequence = read_sequence_csv(sequence_with_alternate_column)

        assert len(sequence) == 2
        assert sequence == ["L002", "L003"]

    def test_read_sequence_filters_blanks(self, sequence_with_blanks):
        """Test that blank entries are filtered out."""
        sequence = read_sequence_csv(sequence_with_blanks)

        assert len(sequence) == 2
        assert sequence == ["L001", "L002"]

    def test_read_nonexistent_file(self, tmp_path):
        """Test that nonexistent file raises FileNotFoundError."""
        nonexistent = tmp_path / "nonexistent.csv"

        with pytest.raises(FileNotFoundError, match="Sequence file not found"):
            read_sequence_csv(nonexistent)

    def test_read_sequence_missing_column(self, tmp_path):
        """Test that missing Lot ID column raises ValueError."""
        csv_path = tmp_path / "no_column.csv"
        csv_content = """Name
L001"""
        csv_path.write_text(csv_content)

        with pytest.raises(ValueError, match="must have a 'Lot ID' column"):
            read_sequence_csv(csv_path)

    def test_read_empty_sequence(self, tmp_path):
        """Test that empty sequence raises ValueError."""
        csv_path = tmp_path / "empty_sequence.csv"
        csv_content = """Lot ID"""
        csv_path.write_text(csv_content)

        with pytest.raises(ValueError, match="contained no Lot IDs"):
            read_sequence_csv(csv_path)

    def test_read_sequence_strips_whitespace(self, tmp_path):
        """Test that whitespace is stripped from lot IDs."""
        csv_path = tmp_path / "whitespace_sequence.csv"
        csv_content = """Lot ID
  L001
 L002 """
        csv_path.write_text(csv_content)

        sequence = read_sequence_csv(csv_path)
        assert sequence == ["L001", "L002"]


class TestOrderLotsBySequence:
    """Tests for order_lots_by_sequence function."""

    def test_order_lots_by_sequence(self, sample_lots):
        """Test ordering lots according to sequence."""
        sequence = ["L003", "L001", "L002", "L004"]

        ordered = order_lots_by_sequence(sample_lots, sequence)

        assert len(ordered) == 4
        assert [lot.lot_id for lot in ordered] == ["L003", "L001", "L002", "L004"]

    def test_order_partial_sequence(self, sample_lots):
        """Test ordering with partial sequence - unspecified lots appended."""
        sequence = ["L003", "L001"]  # Missing L002 and L004

        ordered = order_lots_by_sequence(sample_lots, sequence)

        assert len(ordered) == 4
        # First two are specified in sequence
        assert ordered[0].lot_id == "L003"
        assert ordered[1].lot_id == "L001"
        # Remaining lots appended in original order
        remaining_ids = {ordered[2].lot_id, ordered[3].lot_id}
        assert remaining_ids == {"L002", "L004"}

    def test_order_with_extra_ids_in_sequence(self, sample_lots):
        """Test ordering when sequence contains IDs not in lots."""
        sequence = ["L003", "L999", "L001", "L888"]  # L999 and L888 don't exist

        ordered = order_lots_by_sequence(sample_lots, sequence)

        # Non-existent IDs are silently skipped
        assert len(ordered) == 4
        assert ordered[0].lot_id == "L003"
        assert ordered[1].lot_id == "L001"

    def test_order_empty_sequence(self, sample_lots):
        """Test ordering with empty sequence."""
        ordered = order_lots_by_sequence(sample_lots, [])

        # All lots returned in original order
        assert len(ordered) == 4
        assert [lot.lot_id for lot in ordered] == ["L001", "L002", "L003", "L004"]

    def test_order_empty_lots(self):
        """Test ordering empty lots list."""
        ordered = order_lots_by_sequence([], ["L001", "L002"])

        assert len(ordered) == 0

    def test_order_preserves_lot_attributes(self, sample_lots):
        """Test that ordering preserves all lot attributes."""
        sequence = ["L002", "L001"]

        ordered = order_lots_by_sequence(sample_lots, sequence)

        # Check first ordered lot retains all attributes
        assert ordered[0].lot_id == "L002"
        assert ordered[0].lot_type == "TypeB"
        assert ordered[0].vials == 2000
        assert ordered[0].fill_hours == 4.0

    def test_order_with_duplicate_ids_in_sequence(self, sample_lots):
        """Test ordering when sequence has duplicate IDs.

        The function will add the same Lot object twice if its ID appears
        twice in the sequence, since it uses by_id dictionary lookup for each
        sequence entry.
        """
        sequence = ["L001", "L001", "L002"]  # L001 appears twice

        ordered = order_lots_by_sequence(sample_lots, sequence)

        # The function appends the same Lot for each occurrence in sequence
        lot_ids = [lot.lot_id for lot in ordered]
        # L001 twice, then L002, then remaining (L003, L004)
        assert len(ordered) == 5  # 3 from sequence + 2 remaining
        assert lot_ids[:3] == ["L001", "L001", "L002"]
        assert lot_ids[0] is lot_ids[1]  # Same Lot object twice
