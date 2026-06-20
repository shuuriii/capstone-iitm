# Phase 1 - SQL Analytics Layer

This folder builds a trusted SQLite analytics layer from:

- `patients.csv`
- `visits.csv`
- `billing.csv`

The phase notebook is available at:

- `notebooks/Phase1_SQL.ipynb`

## Build

Run:

```bash
python3 scripts/build_sqlite_db.py
```

This creates `hospital_analytics.db` with:

- Raw staging tables: `raw_patients`, `raw_visits`, `raw_billing`
- Constrained relational tables: `patients`, `visits`, `billing`
- Business views: `vw_visit_billing_detail`, `vw_department_kpis`, `vw_insurance_kpis`

## SQL Files

- `sql/01_schema.sql` defines raw tables, final tables, keys, constraints, and indexes.
- `sql/02_views.sql` defines reusable business views.
- `sql/03_analysis_queries.sql` contains operational and financial analysis queries.
- `sql/04_data_quality_checks.sql` contains data-quality and integrity checks.
- `docs/index_strategy.md` documents which queries benefit from each index.

## Design Notes

SQLite does not support named database schemas like PostgreSQL. In this deliverable, the database file `hospital_analytics.db` is the hospital analytics schema boundary.

Raw staging tables preserve source records so data-quality checks can detect source defects, including duplicates or orphan billing rows. Final relational tables enforce primary keys, foreign keys, categorical checks, and non-negative numeric checks for leadership-grade reporting.
