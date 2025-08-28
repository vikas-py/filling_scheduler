# Filling Scheduler

A Python tool to generate a filling line schedule with **strict pharma constraints**:
- Clean before use (24h)
- Clean window max 120h
- Same-type changeover: 4h
- Different-type changeover: 8h
- Lots must run fully without split

## Features
- Reads lots from CSV (`Lot ID, Type, Vials`)
- Computes fill times (332 vials/min)
- Groups lots heuristically to reduce changeovers
- Validates schedule (no window overrun, no split, no oversized lots)
- Outputs:
  - `schedule.csv` – actionable timeline
  - `summary.txt` – KPIs + validation
- Strict rules: impossible lots (>120h) trigger errors

## Quick start

```bash
# clone the repo
git clone https://github.com/<your-username>/filling_scheduler.git
cd filling_scheduler

# create virtual env
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# run
python main.py
