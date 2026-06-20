# Deployment Runbook

## Purpose

This runbook describes how to build the Phase 2 modeling dataset and run the FastAPI package locally.

## Prerequisites

- Python 3.10 or newer
- Source files in the repository root: `patients.csv`, `visits.csv`, and `billing.csv`

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Build Data Outputs

```bash
python3 scripts/build_features.py
```

Expected outputs:

- `data_outputs/model_table.csv`
- `data_outputs/feature_schema.json`
- `data_outputs/drift_summary.csv`
- `docs/phase2_data_quality_report.md`

## Run API Locally

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Open the interactive docs:

```text
http://127.0.0.1:8000/docs
```

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "model_table_available": true,
  "schema_available": true
}
```

## Operational Checks

- Re-run `python3 scripts/build_features.py` whenever source CSV files change.
- Confirm `/health` returns `model_table_available: true` before exposing `/score/visit`.
- Monitor unexpected changes in `data_outputs/drift_summary.csv` before model deployment.
- Treat `/score/visit` as a transparent heuristic baseline until Phase 3 predictive modeling is implemented.
