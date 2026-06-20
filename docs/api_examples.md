# API Request and Response Examples

## Score Visit Risk

Endpoint:

```text
POST /score/visit
```

Sample request:

```json
{
  "department": "ICU",
  "visit_type": "ER",
  "insurance_provider": "SecureLife",
  "billed_amount": 65000.0,
  "approved_amount": 0.0,
  "payment_days": 29.0,
  "length_of_stay_hours": 46.0,
  "visit_frequency": 9,
  "chronic_flag": 1
}
```

Sample response:

```json
{
  "risk_score": 100.0,
  "risk_level": "high",
  "signals": [
    "billed_amount_top_5_percent",
    "payment_delay_top_10_percent",
    "length_of_stay_top_10_percent",
    "provider_high_rejection_rate",
    "low_approval_ratio",
    "frequent_patient_visits",
    "chronic_patient"
  ]
}
```

## Dataset Summary

Endpoint:

```text
GET /summary
```

Sample response:

```json
{
  "rows": 25000,
  "departments": ["Cardiology", "ER", "General", "ICU", "Neurology", "Orthopedics"],
  "visit_types": ["ER", "ICU", "OPD"],
  "insurance_providers": ["CareOne", "HealthPlus", "MediCareX", "SecureLife"],
  "avg_billed_amount": 20870.76,
  "avg_payment_days": 13.03,
  "avg_length_of_stay_hours": 19.55
}
```
