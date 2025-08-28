# Filling Scheduler

Generates a filling line schedule under strict constraints:
- Clean before use (24h)
- Clean window <= 120h (fills + changeovers)
- Changeover: 4h (same type), 8h (different type)
- Fill rate: 332 vials/min (19,920 vials/h)
- No lot splitting
- Strict validation: impossible inputs fail early

## Run

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py