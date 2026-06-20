# Phase 5 Deployment Guide

## Overview

Phase 5 exposes the trained hospital prediction models through FastAPI so dashboards and internal systems can request real-time predictions.

## Service Capabilities

- Health checks with artifact availability.
- Visit-risk prediction using `model_artifacts/risk_best_model.joblib`.
- Claim-outcome prediction using `model_artifacts/claim_best_model.joblib`.
- Pydantic request and response validation.
- Prediction audit logging with timestamp, model version, and input feature hash.

## Local Startup

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_features.py
python3 scripts/train_phase3_models.py
python3 scripts/evaluate_phase4_models.py
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

## Governance Notes

- Predictions should be used for prioritization and human review.
- The API logs hashed inputs rather than raw features to reduce sensitive-data exposure.
- The model version combines artifact name, modification timestamp, and SHA-256 digest prefix.
- Phase 4 model card and segment metrics should be reviewed before replacing model artifacts.

## Production Considerations

- Put the API behind authenticated internal access.
- Rotate `logs/predictions.jsonl` using system log rotation or application log shipping.
- Pin dependency versions for production builds.
- Monitor prediction distributions and compare them with Phase 4 evaluation metrics.
- Retrain and redeploy only after a successful Phase 4 evaluation run.
