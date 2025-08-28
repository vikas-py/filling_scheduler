import csv
import random
from pathlib import Path

def generate_dataset(
    out_path: Path,
    n_lots: int = 100,
    vial_types: list[str] = None,
    min_vials: int = 20_000,
    max_vials: int = 2_300_000,
    seed: int = 42,
):
    """
    Generate a synthetic dataset of lots.

    - out_path: output CSV file
    - n_lots: number of lots
    - vial_types: list of vial types (default: ["VialE","VialH","VialF","VialX"])
    - min_vials, max_vials: vial count range per lot
    - seed: RNG seed for reproducibility
    """
    random.seed(seed)
    vial_types = vial_types or ["VialE", "VialH", "VialF", "VialX"]

    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Lot ID", "Type", "Vials"])
        for i in range(1, n_lots + 1):
            lot_id = f"L{i:03d}"
            lot_type = random.choice(vial_types)
            vials = random.randint(min_vials, max_vials)
            writer.writerow([lot_id, lot_type, vials])

    print(f"✅ Generated dataset: {out_path} ({n_lots} lots, types={vial_types})")

if __name__ == "__main__":
    out_path = Path(__file__).parent / "lots_large.csv"
    generate_dataset(out_path, n_lots=200)  # change size here
