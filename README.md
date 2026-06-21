# 🏥 Hospital Analytics Capstone

An end-to-end healthcare analytics project built with public IIT-M capstone data.

This project takes raw hospital records and turns them into a practical decision-support system: SQL reporting, data quality checks, machine learning predictions, an API, monitoring reports, and an executive business summary.

In simple terms: it helps a hospital understand **what is happening, what might happen next, and where teams should pay attention**.

## 🔗 Live Demo

- Live demo: https://capstone-iitm.onrender.com/
- Technical API docs: https://capstone-iitm.onrender.com/docs
- GitHub repo: https://github.com/shuuriii/capstone-iitm

The live demo lets you try:

- Dataset summary statistics
- Visit risk prediction
- Insurance claim outcome prediction
- A transparent rule-based visit risk explanation

## 🧠 What Problem Does This Solve?

Hospitals generate a lot of operational and billing data, but that data is often spread across different files and systems. Without a structured workflow, teams may struggle to answer basic but important questions:

- Which departments are seeing higher-risk visits?
- Which insurance claims are more likely to be rejected or delayed?
- Where are billing amounts unusually high?
- Which fields have missing or unreliable values?
- Can we build a repeatable workflow from raw data to insight, prediction, deployment, and monitoring?

This project simulates how a data team could build that workflow in a professional way.

## 💡 Common Problems Faced

The project is designed around realistic healthcare analytics issues:

- **Scattered data**: patient, visit, and billing data start as separate CSV files.
- **Data quality gaps**: important billing fields such as approved amount and payment days can be missing.
- **Operational blind spots**: departments, providers, and visit types need to be compared using consistent KPIs.
- **Claim uncertainty**: teams need early signals about whether claims may be paid, pending, or rejected.
- **Model trust**: predictions need evaluation, explanation, and monitoring before they can be used responsibly.
- **Deployment gap**: a model is not very useful if it only lives inside a notebook.

## 🤖 Where Does AI Come In?

The AI/ML layer is used for prediction, not for replacing human judgment.

This project trains classification models for:

- **Visit risk prediction**: predicts whether a visit is Low, Medium, or High risk.
- **Claim outcome prediction**: predicts whether a claim is likely to be Paid, Pending, or Rejected.

The models are packaged into a FastAPI service so predictions can be tested through a live web demo or API endpoint.

## 🛡️ Guardrails and Responsible AI

The project includes practical guardrails to make the workflow safer and more explainable:

- **Data validation**: SQL constraints check IDs, dates, allowed categories, non-negative amounts, and billing relationships.
- **Leakage control**: model features are selected to avoid using future/outcome information in the wrong prediction task.
- **Time-based split**: models are trained on earlier visits and tested on later visits to better simulate real-world use.
- **Class imbalance handling**: macro F1 is used so smaller classes are not ignored.
- **Segment checks**: evaluation looks at performance across fields like gender, city, and insurance provider.
- **Explainability**: feature importance and model-card style documentation are included.
- **Monitoring**: drift and data validation reports help detect when future data may behave differently.
- **Human-in-the-loop framing**: predictions are presented as decision support, not final medical or billing decisions.

## 🧰 Tech Stack

- **SQL / SQLite** for relational modeling, constraints, views, and analytics queries
- **Python / pandas / NumPy** for EDA, cleaning, and feature engineering
- **scikit-learn** for classification models and preprocessing pipelines
- **FastAPI** for deployment-ready prediction endpoints
- **Render** for the live API demo
- **Jupyter notebooks** for readable phase-by-phase analysis

## 📌 Project Roadmap

The project is organized into seven completed phases:

- Phase 1: SQL Analytics Layer - Business Intelligence Foundation
- Phase 2: Python EDA, Data Quality, Feature Engineering, and API Package
- Phase 3: Classification Modeling for Visit Risk and Claim Outcomes
- Phase 4: Model Evaluation, Explainability, and Safety Checks
- Phase 5: Deployment and API Integration
- Phase 6: Monitoring, Drift Detection, and Governance
- Phase 7: Executive Business Report

## 🚀 Deploying the API

This repository includes `render.yaml` for deployment on Render.

Render settings:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`
- Python version: `3.12.3`

## Project Phases

| Phase | Focus | Notebook | Status |
| --- | --- | --- | --- |
| Phase 1 | SQL analytics layer | [Phase1_SQL.ipynb](notebooks/Phase1_SQL.ipynb) | Complete |
| Phase 2 | Exploratory data analysis | [Phase2_EDA.ipynb](notebooks/Phase2_EDA.ipynb) | Complete |
| Phase 3 | Predictive modeling / AI layer | [Phase3_Modeling.ipynb](notebooks/Phase3_Modeling.ipynb) | Complete |
| Phase 4 | Model evaluation and governance | [Phase4_Evaluation.ipynb](notebooks/Phase4_Evaluation.ipynb) | Complete |
| Phase 5 | Deployment and API integration | FastAPI service | Complete |
| Phase 6 | Monitoring and governance | Monitoring scripts and reports | Complete |
| Phase 7 | Executive business report | [Phase7_Final_Report.ipynb](notebooks/Phase7_Final_Report.ipynb) | Complete |

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
│   ├── Phase3_Modeling.ipynb
│   ├── Phase4_Evaluation.ipynb
│   ├── Phase5_Deployment.ipynb
│   ├── Phase6_Monitoring_Governance.ipynb
│   └── Phase7_Final_Report.ipynb
├── scripts/
│   ├── build_sqlite_db.py
│   ├── build_features.py
│   ├── train_phase3_models.py
│   ├── evaluate_phase4_models.py
│   └── monitor_phase6.py
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
    ├── phase5_deployment_guide.md
    ├── phase2_data_quality_report.md
    ├── phase4/
    └── phase6/
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

## Phase 4: Evaluation, Explainability, and Safety

Phase 4 evaluates the saved Phase 3 models for governance readiness. It computes train/test metrics, business-critical recall, feature importance, demographic and regional segment performance, and consolidated model-card documentation.

### How to Run Phase 4

Train Phase 3 models first:

```bash
python3 scripts/train_phase3_models.py
```

Run Phase 4 evaluation:

```bash
python3 scripts/evaluate_phase4_models.py
```

Open the evaluation notebook:

- [notebooks/Phase4_Evaluation.ipynb](notebooks/Phase4_Evaluation.ipynb)

Phase 4 outputs:

- `notebooks/Phase4_Evaluation.ipynb`
- `scripts/evaluate_phase4_models.py`
- `docs/phase4/risk_model_evaluation_report.md`
- `docs/phase4/claim_model_evaluation_report.md`
- `docs/phase4/model_card.md`
- `docs/phase4/explainability_summary.md`
- `docs/phase4/phase4_metrics.json`
- `docs/phase4/phase4_evaluation_summary.csv`
- `docs/phase4/risk_model_segment_metrics.csv`
- `docs/phase4/claim_model_segment_metrics.csv`
- `docs/phase4/risk_model_feature_importance.csv`
- `docs/phase4/claim_model_feature_importance.csv`

### Phase 4 Highlights

- Test recall for High Risk visits: `0.1261`.
- Test recall for Rejected claims: `0.6044`.
- Claim outcome modeling is the stronger near-term operational candidate.
- Visit risk modeling needs improved features or imbalance handling before high-stakes use.
- Segment checks cover `gender`, `city`, and `insurance_provider`.
- Model card documents intended use, limitations, assumptions, and monitoring controls.

## Phase 5: Deployment and API Integration

Phase 5 converts the trained model artifacts into a real-time FastAPI service for hospital dashboards and internal systems.

### How to Run Phase 5

Prepare data, models, and evaluation outputs:

```bash
python3 scripts/build_features.py
python3 scripts/train_phase3_models.py
python3 scripts/evaluate_phase4_models.py
```

Start the prediction API:

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Open the interactive API docs:

```text
http://127.0.0.1:8000/docs
```

Phase 5 outputs:

- `api/main.py`
- `docs/deployment_runbook.md`
- `docs/api_examples.md`
- `docs/phase5_deployment_guide.md`
- Runtime audit log: `logs/predictions.jsonl`

### Phase 5 Highlights

- Health endpoint validates data, schema, and model artifact availability.
- `/predict/risk` returns visit-risk predictions from `risk_best_model.joblib`.
- `/predict/claim` returns claim-outcome predictions from `claim_best_model.joblib`.
- Requests and responses are validated with Pydantic schemas.
- Predictions are logged with timestamp, model version, input feature hash, prediction, probabilities, and audit log ID.

## Phase 6: Monitoring, Drift Detection, and Governance

Phase 6 adds automated monitoring for long-term model reliability and governance. It validates incoming data, tracks feature and prediction drift, summarizes audit logs, and documents limitations, assumptions, and retraining strategy.

### How to Run Phase 6

Run monitoring against the current model table:

```bash
python3 scripts/monitor_phase6.py
```

Run monitoring against a future scored batch:

```bash
python3 scripts/monitor_phase6.py --current-data path/to/new_batch.csv
```

Phase 6 outputs:

- `scripts/monitor_phase6.py`
- `docs/phase6/data_validation_report.csv`
- `docs/phase6/feature_drift_report.csv`
- `docs/phase6/prediction_drift_report.csv`
- `docs/phase6/audit_log_summary.csv`
- `docs/phase6/drift_detection_report.md`
- `docs/phase6/governance_compliance.md`

### Phase 6 Highlights

- Validates missing values in critical fields.
- Checks numeric ranges for billing, utilization, calendar, and ratio features.
- Detects unseen categories in key operational and payer fields.
- Tracks numeric feature drift using population stability index.
- Tracks categorical drift using maximum category share difference.
- Summarizes prediction audit logs by model version, input hash, prediction class, and timestamp range.

## Phase 7: Executive Business Report

Phase 7 packages the full project into an executive-ready business deliverable for hospital leadership.

Phase 7 outputs:

- `notebooks/Phase7_Final_Report.ipynb`
- `docs/Healthcare_Insights_Report.docx`
- `docs/exported/Healthcare_Insights_Report.pdf`
- `docs/Healthcare_Insights_Report.md`
- `docs/healthcare_insights_report_summary.md`

### Phase 7 Highlights

- Consolidates SQL, EDA, modeling, evaluation, deployment, monitoring, and governance outcomes.
- Translates technical outputs into operational and financial leadership value.
- Provides business recommendations for hospital deployment sponsorship and adoption.

## Roadmap

- Phase 1: SQL analytics foundation
- Phase 2: Exploratory data analysis and API package
- Phase 3: Predictive modeling / AI layer
- Phase 4: Model evaluation, explainability, and safety checks
- Phase 5: Deployment and API integration
- Phase 6: Monitoring, drift detection, and governance
- Phase 7: Executive business report
