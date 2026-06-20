# API Request and Response Examples

## Health Check

Endpoint:

```text
GET /health
```

Sample response:

```json
{
  "status": "ok",
  "api_version": "1.0.0",
  "model_table_available": true,
  "data_schema_available": true,
  "model_schema_available": true,
  "risk_model_available": true,
  "claim_model_available": true,
  "prediction_log_path": "logs/predictions.jsonl"
}
```

## Predict Visit Risk

Endpoint:

```text
POST /predict/risk
```

Sample request:

```json
{
  "age": 67,
  "gender": "F",
  "city": "Mumbai",
  "insurance_provider": "SecureLife",
  "chronic_flag": 1,
  "department": "ICU",
  "visit_type": "ER",
  "doctor_id": 174,
  "length_of_stay_hours_filled": 42.5,
  "visit_frequency": 8,
  "days_since_registration": 310,
  "visit_month": 10,
  "visit_day_of_week": 2,
  "visit_quarter": 4
}
```

Sample response:

```json
{
  "prediction": "Medium",
  "probabilities": {
    "High": 0.322086,
    "Low": 0.313494,
    "Medium": 0.364421
  },
  "model_name": "visit_risk_classifier",
  "model_version": "risk_best_model:20260620064112:3cbf6ff4052f",
  "timestamp_utc": "2026-06-20T12:35:02.123456+00:00",
  "input_feature_hash": "64f1979131292514afd32f058b3f89d41022e6acc11533eae5f8d283829e6f26",
  "audit_log_id": "6e2f1af0-8d4a-4f24-badc-6cf4e0f4d19a"
}
```

## Predict Claim Outcome

Endpoint:

```text
POST /predict/claim
```

Sample request:

```json
{
  "age": 67,
  "gender": "F",
  "city": "Mumbai",
  "insurance_provider": "SecureLife",
  "chronic_flag": 1,
  "department": "ICU",
  "visit_type": "ER",
  "risk_score": "High",
  "doctor_id": 174,
  "billed_amount": 65000.0,
  "length_of_stay_hours_filled": 42.5,
  "visit_frequency": 8,
  "days_since_registration": 310,
  "visit_month": 10,
  "visit_day_of_week": 2,
  "visit_quarter": 4,
  "billing_month": 10,
  "billing_lag_days": 4
}
```

Sample response:

```json
{
  "prediction": "Paid",
  "probabilities": {
    "Paid": 0.553824,
    "Pending": 0.323724,
    "Rejected": 0.122452
  },
  "model_name": "claim_outcome_classifier",
  "model_version": "claim_best_model:20260620064114:2756c16ae79f",
  "timestamp_utc": "2026-06-20T12:36:11.123456+00:00",
  "input_feature_hash": "35019ba73f2d0ad086f5977fdaeec574c03a88372d12e65bf5c5a9ae81d83be7",
  "audit_log_id": "60fca1a5-f1b3-4d10-8b31-0d8752e70ef6"
}
```

## Legacy Heuristic Visit Score

Endpoint:

```text
POST /score/visit
```

This endpoint is retained for Phase 2 compatibility. New integrations should use `/predict/risk`.
