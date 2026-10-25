# Project IRIS: Historical PRTR Emissions Time-Series ETL & Signals

## Overview
A lightweight, reproducible ETL pipeline and signal generator built for historical Pollutant Release and Transfer Register (PRTR) data. It ingests facility-level emissions records, normalizes mixed reporting units (e.g., converting tonnes to kilograms while blocking invalid units), explicitly preserves missing reporting years without converting them to zero, computes baseline-to-latest percentage trends, and flags indicative $\ge 70\%$ emission declines.

## Prerequisites
- **Required Language/Runtime:** Python 3.10+ (via Anaconda / Conda or standard Python venv)
- **Required Dependencies:** `pandas`, `pytest`

## Setup
1. Clone the repository and navigate into the project directory:
   ```bash
   git clone <your-repository-url>
   cd iris-sample
   ```
2. Create and activate a clean environment:
   ```bash
   conda create -n iris-env python=3.10 -y
   conda activate iris-env
   ```
3. Install required dependencies:
   ```bash
   pip install pandas pytest
   ```

## Run
Execute the pipeline commands sequentially in your terminal:

1. **Generate the self-contained synthetic PRTR fixture:**
   ```bash
   python generate_fixture.py
   ```
   *Generates `data/prtr_fixture.csv` containing multi-year facility emissions, mixed units, and missing reporting years.*

2. **Run the core ETL pipeline and generate audit-ready trend reports:**
   ```bash
   python src/etl.py
   ```
   *Processes input data and writes outputs to `data/facility_year_normalized.csv`, `data/audit_ready_trends.csv`, and `data/audit_ready_trends.json`.*

## Tests
Execute the automated test suite using `pytest` to verify unit conversions, missing-year handling, and idempotency:

```bash
python -m pytest tests/
```

**Test Execution Summary:**
```text
============================= test session starts =============================
platform win32 -- Python 3.10.12, pytest-8.x.x, pluggy-1.5.0
rootdir: iris-sample
collected 3 items

tests/test_etl.py ...                                                    [100%]

============================== 3 passed in 0.74s ==============================
```

- `test_unit_conversion`: Verifies `t` to `kg` conversion (factor 1000.0) and verifies that unrecognized units are blocked with descriptive audit notes.
- `test_trend_calculations_and_missing_years`: Validates that a 100 to 20 drop correctly reports an 80% decline (`decline_gte_70_pct = True`) and confirms missing years (e.g., 2020) are preserved as missing rather than coerced to zero.
- `test_idempotency`: Confirms repeated ETL executions yield identical DataFrame outputs and trend reports.

## Assumptions and Notes
- **Unit Normalization & Safety:** Mass units reported in tonnes (`t`) are converted to kilograms (`kg`) using a fixed multiplier of `1000.0`. Unrecognized or ambiguous units are safely blocked with descriptive audit notes (`unit_note`) rather than falsely assumed or defaulted.
- **Missing-Year Preservation:** Gaps in reporting year sequences (e.g., missing year 2020 for `FAC_001`) are explicitly captured in a `missing_years_in_range` array and are **not** coerced into zero emissions, maintaining data integrity for auditing.
- **Idempotency & Reproducibility:** Pipeline operations are fully deterministic and stateless. Repeated runs on the same input dataset produce identical output files and trend calculations.
- **Source & Licence Limitations:** Built using self-contained synthetic fixtures (`data/prtr_fixture.csv`) to comply with licensing boundaries and data privacy limits without requiring bulk web scraping or live production credentials.
- **Safe Integration into IRIS:** Implemented as a clean, modular vertical slice with decoupled transformation functions (`normalize_units`, `run_etl`) that can be safely imported or integrated into the broader Project IRIS framework.