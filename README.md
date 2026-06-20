# Hospital Analytics Capstone

Portfolio capstone project for hospital operations, billing intelligence, and future health-tech analytics workflows.

This project is being built in phases. The current completed phase is:

- Phase 1: SQL Analytics Layer - Business Intelligence Foundation

## Project Phases

| Phase | Focus | Notebook | Status |
| --- | --- | --- | --- |
| Phase 1 | SQL analytics layer | [Phase1_SQL.ipynb](notebooks/Phase1_SQL.ipynb) | Complete |
| Phase 2 | Exploratory data analysis | Coming soon | Planned |
| Phase 3 | Predictive modeling / AI layer | Coming soon | Planned |
| Phase 4 | Dashboard or decision support interface | Coming soon | Planned |

To view a phase notebook, click the notebook link above. GitHub renders `.ipynb` files directly in the browser, so visitors can read the workflow, SQL, outputs, and conclusions without installing anything.

## Phase 1: SQL Analytics Layer

Phase 1 converts raw hospital CSV datasets into a structured SQLite analytics layer with enforced integrity, reusable business views, indexed query paths, and leadership-ready KPI analysis.

### Business Goal

Create a reliable, queryable hospital data layer that leadership can trust for operational and financial decision-making.

### Technical Scope

- Load raw CSV files into staging tables.
- Create relational tables: `patients`, `visits`, and `billing`.
- Enforce primary keys and foreign keys.
- Add indexes for frequent joins, filters, and aggregations.
- Create reusable SQL views for operational and billing analysis.
- Run operational, financial, and data-quality checks.
- Package the phase as a Jupyter notebook: `notebooks/Phase1_SQL.ipynb`.

## Repository Structure

```text
.
├── README_PHASE1.md
├── patients.csv
├── visits.csv
├── billing.csv
├── notebooks/
│   └── Phase1_SQL.ipynb
├── scripts/
│   └── build_sqlite_db.py
├── sql/
│   ├── 01_schema.sql
│   ├── 02_views.sql
│   ├── 03_analysis_queries.sql
│   └── 04_data_quality_checks.sql
└── docs/
    ├── analysis_results.md
    └── index_strategy.md
```

## How to Run Phase 1

Open the notebook on GitHub:

- [notebooks/Phase1_SQL.ipynb](notebooks/Phase1_SQL.ipynb)

Rebuild the SQLite database:

```bash
python3 scripts/build_sqlite_db.py
```

This generates `hospital_analytics.db` locally. The database file is intentionally excluded from Git because it can be reproduced from the source CSV files and SQL scripts.

## Phase 1 Highlights

- Loaded 5,000 patient records.
- Loaded 25,000 visit records.
- Loaded 25,000 billing records.
- Verified clean referential integrity between patients, visits, and billing.
- Found 790 billing records with missing or invalid `payment_days`.
- Flagged 72 high-billed visits where `approved_amount` is zero or missing.

## Roadmap

- Phase 1: SQL analytics foundation
- Phase 2: Exploratory data analysis
- Phase 3: Predictive modeling / AI layer
- Phase 4: Dashboard or health-tech decision support interface
