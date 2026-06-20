# Hospital Analytics Capstone

Portfolio capstone project for hospital operations, billing intelligence, and future health-tech analytics workflows.

This project is being built in phases. The current completed phase is:

- Phase 1: SQL Analytics Layer - Business Intelligence Foundation
- Phase 2: Python EDA, Data Quality, Feature Engineering, and API Package
- Phase 3: Classification Modeling for Visit Risk and Claim Outcomes

## Project Phases

| Phase | Focus | Notebook | Status |
| --- | --- | --- | --- |
| Phase 1 | SQL analytics layer | [Phase1_SQL.ipynb](notebooks/Phase1_SQL.ipynb) | Complete |
| Phase 2 | Exploratory data analysis | [Phase2_EDA.ipynb](notebooks/Phase2_EDA.ipynb) | Complete |
| Phase 3 | Predictive modeling / AI layer | [Phase3_Modeling.ipynb](notebooks/Phase3_Modeling.ipynb) | Complete |
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
│   ├── Phase1_SQL.ipynb
│   ├── Phase2_EDA.ipynb
│   └── Phase3_Modeling.ipynb
├── scripts/
│   ├── build_sqlite_db.py
│   ├── build_features.py
│   └── train_phase3_models.py
├── api/
│   └── main.py
├── data_outputs/
│   ├── model_table.csv
│   ├── feature_schema.json
│   └── drift_summary.csv
├── reports/
│   └── figures/
├── model_artifacts/
│   ├── risk_best_model.joblib
│   ├── claim_best_model.joblib
│   ├── feature_schema.json
│   ├── metrics.json
│   └── metrics_summary.csv
├── sql/
│   ├── 01_schema.sql
│   ├── 02_views.sql
│   ├── 03_analysis_queries.sql
│   └── 04_data_quality_checks.sql
└── docs/
    ├── analysis_results.md
    ├── api_examples.md
    ├── deployment_runbook.md
    ├── Healthcare_Insights_Report.docx
    ├── healthcare_insights_report_summary.md
    ├── index_strategy.md
    └── phase2_data_quality_report.md
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

## Phase 2: Python EDA and Feature Engineering

Phase 2 combines the patient, visit, and billing files in Python, profiles reliability risks in critical fields, classifies outliers, engineers modeling features, and packages a baseline FastAPI scoring service.

### How to Run Phase 2

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Build the modeling dataset and data quality report:

```bash
python3 scripts/build_features.py
```

Run the API locally:

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Phase 2 outputs:

- `notebooks/Phase2_EDA.ipynb`
- `data_outputs/model_table.csv`
- `data_outputs/feature_schema.json`
- `data_outputs/drift_summary.csv`
- `docs/phase2_data_quality_report.md`
- `docs/deployment_runbook.md`
- `docs/api_examples.md`

### Phase 2 Highlights

- Built a 25,000-row visit-level modeling table with 44 columns.
- Identified 1,318 missing `approved_amount` values and 790 missing `payment_days` values.
- Confirmed `length_of_stay_hours` is complete.
- Added visit frequency, patient average length of stay, provider rejection rate, days since registration, calendar features, approval ratio, missingness flags, and outlier classifications.
- Added a FastAPI package with health, schema, summary, and visit-risk scoring endpoints.

## Phase 3: Classification Modeling

Phase 3 trains two leakage-safe classification systems using the Phase 2 modeling table.

- Model A predicts visit risk: `risk_score` as Low, Medium, or High.
- Model B predicts insurance claim outcome: `claim_status` as Paid, Pending, or Rejected.

Both models use a time-based split: earliest 80% of visits for training and latest 20% for testing.

### How to Run Phase 3

Build Phase 2 features first:

```bash
python3 scripts/build_features.py
```

Train and save Phase 3 models:

```bash
python3 scripts/train_phase3_models.py
```

Open the modeling notebook:

- [notebooks/Phase3_Modeling.ipynb](notebooks/Phase3_Modeling.ipynb)

Phase 3 outputs:

- `notebooks/Phase3_Modeling.ipynb`
- `scripts/train_phase3_models.py`
- `model_artifacts/risk_logistic_regression.joblib`
- `model_artifacts/risk_random_forest.joblib`
- `model_artifacts/risk_best_model.joblib`
- `model_artifacts/claim_logistic_regression.joblib`
- `model_artifacts/claim_random_forest.joblib`
- `model_artifacts/claim_best_model.joblib`
- `model_artifacts/feature_schema.json`
- `model_artifacts/metrics.json`
- `model_artifacts/metrics_summary.csv`

Final business report:

- `docs/Healthcare_Insights_Report.docx`
- `docs/healthcare_insights_report_summary.md`

### Phase 3 Highlights

- Trained Logistic Regression baselines and Random Forest advanced models for both targets.
- Used macro F1 as the main comparison metric to account for class imbalance.
- Saved deployable `.joblib` pipelines that include preprocessing and model steps.
- Documented leakage-safe feature sets and production feature schema.

## Roadmap

- Phase 1: SQL analytics foundation
- Phase 2: Exploratory data analysis and API package
- Phase 3: Predictive modeling / AI layer
- Phase 4: Dashboard or health-tech decision support interface
