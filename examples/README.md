# Examples

This directory contains example datasets and utilities for Filling Scheduler.

## Files

### Example Datasets

- **`lots.csv`** - Small dataset with 15 lots
  - Mix of VialE and VialH types
  - Good for testing and learning
  - Various lot sizes (10K to 1.2M vials)

- **`lots_large.csv`** - Large dataset with 500 lots
  - 4 vial types (VialE, VialH, VialF, VialX)
  - For performance testing and benchmarking
  - Generated with `gen_lots.py`

### Utilities

- **`gen_lots.py`** - Dataset generator
  - Creates random but realistic lot data
  - Customizable parameters (size, types, vial range)
  - Reproducible with seed parameter

## Usage

### Running with Example Data

```bash
# Default (uses lots.csv)
python main.py

# Specify different dataset
python main.py  # (edit config.py to change DATA_PATH)
```

### Generating Custom Datasets

```bash
cd examples
python gen_lots.py
```

Customize by editing `gen_lots.py`:

```python
generate_dataset(
    out_path=Path("my_custom_lots.csv"),
    n_lots=100,              # Number of lots
    vial_types=["A", "B"],   # Vial types
    min_vials=10000,         # Minimum vials per lot
    max_vials=1000000,       # Maximum vials per lot
    seed=42                  # Random seed for reproducibility
)
```

## Dataset Format

All datasets follow this CSV format:

```csv
Lot ID,Type,Vials
L001,VialE,100000
L002,VialH,900000
L003,VialE,750000
```

### Required Columns

1. **Lot ID** - Unique identifier (string)
2. **Type** - Vial type (string)
3. **Vials** - Number of vials (positive integer)

### Constraints

- Lot IDs must be unique
- Types must be non-empty strings
- Vials must be positive integers
- Each lot must fit within a single clean window (≤ 120 hours at default rate)

## Example Scenarios

### Small Production Run (15 lots)

Use `lots.csv` for:
- Learning the system
- Quick testing
- Strategy comparison
- Development

### Large Production Run (500 lots)

Use `lots_large.csv` for:
- Performance testing
- Scalability analysis
- Benchmark comparisons
- Production simulation

### Custom Scenarios

Create custom datasets for:
- Specific vial type mixes
- Particular lot size distributions
- Real-world production data
- Edge case testing

## Next Steps

- [Getting Started Guide](../docs/getting_started.md)
- [Strategy Comparison](../docs/strategies.md)
- [Full Documentation](../docs/index.md)
