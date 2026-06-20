# Phase 6 Governance and Compliance Document

## Intended Use

The monitoring layer supports hospital operations and finance governance by checking data quality, feature drift, prediction drift, and prediction audit traceability.

## System Assumptions

- `data_outputs/model_table.csv` is the baseline training/reference dataset.
- Incoming production batches follow the same feature schema.
- Predictions are generated through the Phase 5 FastAPI service.
- Prediction logs are written to `logs/predictions.jsonl`.

## Controls Implemented

- Missing-value checks for critical operational and billing fields.
- Numeric range checks for age, utilization, billing, calendar, and ratio fields.
- Unseen-category checks for department, visit type, city, payer, risk score, and claim status.
- Numeric feature drift using population stability index.
- Categorical drift using maximum category share difference.
- Prediction audit summaries by model version, prediction class, timestamp, and input feature hash.

## Limitations

- PSI and category-share drift are monitoring indicators, not causal explanations.
- Drift thresholds should be tuned with real production history.
- Logs store input hashes rather than raw features to reduce sensitive-data exposure.
- Current models remain decision-support tools and require human review.

## Retraining Strategy

- Review monitoring reports monthly.
- Trigger retraining if any feature has high drift, if multiple features show moderate drift, or if business-critical recall degrades in Phase 4 evaluation.
- Retrain after major payer contract changes, department workflow changes, or data collection process changes.
- Rerun Phase 4 evaluation and update the model card before promoting new model artifacts.

## Compliance Notes

- Preserve `logs/predictions.jsonl` according to internal audit retention policy.
- Restrict API and log access to authorized hospital analytics, operations, and finance users.
- Use model outputs for triage and prioritization, not autonomous clinical or claim decisions.
