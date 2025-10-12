# Test Fixtures

This directory contains sample CSV files used for testing the filling scheduler.

## Valid Test Data

### Basic Scenarios

| File | Description | Lots | Types | Use Case |
|:-----|:------------|:----:|:-----:|:---------|
| `simple_lots.csv` | Simple 3-lot dataset | 3 | 2 | Basic functionality testing |
| `single_lot.csv` | Single lot scenario | 1 | 1 | Edge case: minimal input |
| `same_type_lots.csv` | All lots same type | 5 | 1 | Testing no-changeover scenarios |
| `all_different_types.csv` | All lots different types | 5 | 5 | Maximum changeover scenarios |
| `mixed_types.csv` | Mixed type distribution | 8 | 3 | Realistic mixed workload |

### Size Variations

| File | Description | Lots | Vials Range | Use Case |
|:-----|:------------|:----:|:------------|:---------|
| `small_lots.csv` | Small batch sizes | 5 | 1K - 2.5K | Quick processing scenarios |
| `large_lots.csv` | Large batch sizes | 4 | 500K - 1M | Long processing times |
| `varied_sizes.csv` | Mixed small and large | 6 | 10K - 1M | Realistic size distribution |

### Ordering Scenarios

| File | Description | Lots | Use Case |
|:-----|:------------|:----:|:---------|
| `unsorted_lots.csv` | Random lot order | 8 | Testing strategy optimization |
| `priority_lots.csv` | Priority + regular lots | 6 | Testing scheduling preferences |

## Sequence Files

| File | Description | Column Name | Use Case |
|:-----|:------------|:------------|:---------|
| `sequence.csv` | Standard sequence format | `Lot ID` | Basic sequence ordering |
| `sequence_alternate_column.csv` | Alternate column name | `LotID` | Testing column name flexibility |
| `partial_sequence.csv` | Partial sequence (3/6 lots) | `Lot ID` | Testing incomplete sequences |

## Invalid/Error Test Data

| File | Error Type | Expected Behavior |
|:-----|:-----------|:------------------|
| `invalid_blank_id.csv` | Blank Lot ID | Should raise ValueError |
| `invalid_blank_type.csv` | Blank Type | Should raise ValueError |
| `invalid_missing_vials.csv` | Missing Vials value | Should raise ValueError |
| `invalid_missing_column.csv` | Missing required column | Should raise ValueError |
| `empty_lots.csv` | No data rows | Should raise ValueError |
| `duplicate_ids.csv` | Duplicate Lot IDs | Should generate warning |
| `invalid_negative_vials.csv` | Negative vials | Should raise ValueError |

## Usage in Tests

### Loading Fixtures

```python
import pytest
from pathlib import Path

@pytest.fixture
def fixtures_dir():
    """Get the fixtures directory path."""
    return Path(__file__).parent.parent / "fixtures"

def test_with_fixture(fixtures_dir):
    """Example test using a fixture file."""
    from fillscheduler.io_utils import read_lots_with_pandas
    from fillscheduler.config import AppConfig

    cfg = AppConfig()
    lots = read_lots_with_pandas(fixtures_dir / "simple_lots.csv", cfg)
    assert len(lots) == 3
```

### Common Test Patterns

#### Testing Valid Input
```python
def test_simple_schedule(fixtures_dir):
    lots_path = fixtures_dir / "simple_lots.csv"
    # Test logic here...
```

#### Testing Error Handling
```python
def test_invalid_input(fixtures_dir):
    with pytest.raises(ValueError, match="Blank Lot ID"):
        lots_path = fixtures_dir / "invalid_blank_id.csv"
        # Test logic here...
```

#### Testing Strategies
```python
@pytest.mark.parametrize("fixture,expected_lots", [
    ("simple_lots.csv", 3),
    ("mixed_types.csv", 8),
    ("large_lots.csv", 4),
])
def test_strategy_with_fixtures(fixtures_dir, fixture, expected_lots):
    lots_path = fixtures_dir / fixture
    # Test logic here...
```

## Fixture Design Principles

1. **Minimal**: Each fixture tests one specific scenario
2. **Realistic**: Data represents real-world pharmaceutical batches
3. **Documented**: Clear naming and documentation of purpose
4. **Isolated**: Fixtures don't depend on each other
5. **Complete**: Cover both valid and invalid cases

## Adding New Fixtures

When adding new fixture files:

1. **Name clearly**: Use descriptive names (e.g., `edge_case_description.csv`)
2. **Document**: Add entry to this README with description and use case
3. **Keep simple**: Minimize data to what's needed for the test
4. **Follow format**: Use standard CSV format with required columns
5. **Test both paths**: Add both valid and invalid examples when relevant

## CSV Format Reference

### Lots CSV Format
```csv
Lot ID,Type,Vials
<string>,<string>,<integer>
```

**Required Columns:**
- `Lot ID`: Unique identifier for the lot (non-blank string)
- `Type`: Product type/variant (non-blank string)
- `Vials`: Number of vials to fill (positive integer)

### Sequence CSV Format
```csv
Lot ID
<string>
```

**Required Column (flexible naming):**
- `Lot ID` (or `LotID`, `lot_id`, `lotid`): Order of lots to schedule

**Notes:**
- Blank rows are filtered out
- Lots not in sequence are appended at end
- Non-existent lot IDs are skipped with no error
