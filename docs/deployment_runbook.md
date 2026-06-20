# Deployment and Operations Runbook

## Purpose

This runbook describes how to build the modeling dataset, train model artifacts, and run the Phase 5 FastAPI prediction service locally.

## Prerequisites

- Python 3.10 or newer
- Source files in the repository root: `patients.csv`, `visits.csv`, and `billing.csv`

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Build Data and Models

Build Phase 2 features:

```bash
python3 scripts/build_features.py
```

Train Phase 3 models:

```bash
python3 scripts/train_phase3_models.py
```

Run Phase 4 governance evaluation:

```bash
python3 scripts/evaluate_phase4_models.py
```

Expected inputs for the API:

- `data_outputs/model_table.csv`
- `data_outputs/feature_schema.json`
- `model_artifacts/risk_best_model.joblib`
- `model_artifacts/claim_best_model.joblib`
- `model_artifacts/feature_schema.json`

## Run API Locally

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Open interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

Expected response includes:

```json
{
  "status": "ok",
  "api_version": "1.0.0",
  "risk_model_available": true,
  "claim_model_available": true
}
```

## Prediction Endpoints

- `POST /predict/risk`: predicts visit risk as `High`, `Low`, or `Medium`.
- `POST /predict/claim`: predicts claim outcome as `Paid`, `Pending`, or `Rejected`.
- `POST /score/visit`: legacy transparent heuristic endpoint retained for Phase 2 compatibility.

Each model-backed response includes:

- `prediction`
- `probabilities`
- `model_name`
- `model_version`
- `timestamp_utc`
- `input_feature_hash`
- `audit_log_id`

## Audit Logging

Model-backed predictions are appended to:

```text
logs/predictions.jsonl
```

Each line stores timestamp, model name, model version, input feature hash, prediction, probabilities, and audit log ID. Raw input features are intentionally not logged; the hash supports traceability without storing full request payloads.

## Operations Checklist

- Rebuild features when source CSV files change.
- Retrain model artifacts after feature changes.
- Rerun Phase 4 evaluation before deploying newly trained artifacts.
- Confirm `/health` shows both model artifacts as available.
- Monitor `logs/predictions.jsonl` volume and rotate the file if it grows large.
- Review `docs/phase4/model_card.md` and segment metrics before production use.
- Use these predictions for workflow prioritization and human review, not autonomous clinical or financial action.
