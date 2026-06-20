# Healthcare Insights Report

Executive Summary for Hospital Operations, Revenue Cycle, AI Deployment, and Governance

## Executive Overview

This capstone converts hospital patient, visit, and billing data into an end-to-end analytics and AI decision-support system. The project starts with a governed SQL analytics layer, advances through Python EDA and feature engineering, trains visit-risk and claim-outcome classifiers, validates safety and fairness, deploys models through FastAPI, and adds monitoring for drift and audit traceability.

- Dataset scale: 5,000 patients, 25,000 visits, 25,000 billing records, and 25,000 model-ready visit rows.
- Primary data reliability risks: 1,318 missing approved amounts and 790 missing payment-day values; length of stay has 0 missing records.
- Highest payer rejection rate: SecureLife at 15.69%.
- Deployment readiness: FastAPI endpoints provide real-time risk and claim predictions with model versioning, input feature hashing, and audit logging.
- Governance readiness: Phase 6 monitoring reports show 0 failed validation checks, 2 review checks, 0 high-drift features, and 0 moderate-drift features in the baseline run.

## Key Operational and Financial Findings

Operational activity is broadly distributed across departments, which supports cross-department modeling rather than a narrow single-service-line pilot. ICU and ER have the highest high-risk visit rates and should be prioritized for monitoring and workflow review. Billing quality issues are concentrated in approval and payment-delay fields, which directly affects revenue realization and payer follow-up reliability.

| department | visits | avg_los | high_risk_rate |
| --- | ---: | ---: | ---: |
| General | 4,228 | 19.43 | 19.84% |
| ER | 4,220 | 19.54 | 20.66% |
| Neurology | 4,165 | 19.72 | 20.31% |
| Orthopedics | 4,164 | 19.66 | 20.22% |
| Cardiology | 4,159 | 19.60 | 18.99% |
| ICU | 4,064 | 19.36 | 20.79% |

Payer reliability summary:

| insurance_provider | claims | rejection_rate | avg_payment_days |
| --- | ---: | ---: | ---: |
| SecureLife | 5,965 | 15.69% | 13.08 |
| MediCareX | 6,532 | 15.25% | 13.01 |
| HealthPlus | 6,220 | 14.97% | 13.08 |
| CareOne | 6,283 | 14.87% | 13.03 |

## Model Impact Summary

Two model families were built for operational and financial decision support. The visit-risk model predicts Low, Medium, or High visit risk. The claim-outcome model predicts Paid, Pending, or Rejected claims. Models are evaluated with a time-based split to better reflect production use, where historical visits are used to score future activity.

| model | test_accuracy | test_macro_f1 | critical_class | critical_class_recall |
| --- | ---: | ---: | --- | ---: |
| risk_model | 0.4092 | 0.3485 | High | 0.1261 |
| claim_model | 0.4444 | 0.3743 | Rejected | 0.6044 |

- Visit-risk model: High Risk recall is 0.1261; this model should be treated as an early triage signal, not a standalone safety screen.
- Claim-outcome model: Rejected claim recall is 0.6044; this is the stronger near-term candidate for revenue-cycle prioritization.
- Random Forest models outperform Logistic Regression baselines, but current macro F1 values show that richer diagnosis, procedure, prior authorization, workload, and payer-history features would be needed for production-grade performance.

## Deployment, Monitoring, and Governance

The deployment layer exposes model predictions through FastAPI endpoints for hospital dashboards and internal workflow systems. Requests and responses are validated with Pydantic schemas. Each prediction is logged with timestamp, model version, prediction class, probabilities, audit ID, and input feature hash. Phase 6 adds monitoring for missing values, numeric ranges, unseen categories, feature drift, prediction drift, and audit-log completeness.

- Architecture: source CSVs -> SQLite analytics layer -> Python feature pipeline -> model artifacts -> FastAPI prediction service -> monitoring and governance reports.
- Core endpoints: `/health`, `/predict/risk`, `/predict/claim`, `/schema`, and `/summary`.
- Monitoring outputs: data validation report, feature drift report, prediction drift report, audit log summary, drift detection report, and governance compliance document.
- Governance position: model outputs should support prioritization and human review, not autonomous clinical or financial decisions.

## Business Recommendations for Hospital Leadership

- Sponsor a controlled pilot for claim-outcome prediction in the billing team, focused on pre-submission review and rejected-claim prevention.
- Use visit-risk predictions only as a secondary triage indicator until High Risk recall improves through richer clinical and operational features.
- Create a billing data-quality policy requiring approved amount and payment days to be completed or reason-coded before monthly close.
- Prioritize payer review for SecureLife due to the highest rejection rate in the current dataset.
- Adopt monthly monitoring using Phase 6 reports and trigger retraining when drift, payer behavior, or critical-class recall changes materially.
- Before production rollout, add authentication, log retention rules, dashboard monitoring, model approval workflow, and periodic governance review.

## Submission Artifacts

- EDA and modeling notebooks: `Phase2_EDA.ipynb`, `Phase3_Modeling.ipynb`, `Phase4_Evaluation.ipynb`.
- Deployment package: `api/main.py`, `docs/phase5_deployment_guide.md`, `docs/api_examples.md`.
- Monitoring package: `scripts/monitor_phase6.py`, `docs/phase6/drift_detection_report.md`, `docs/phase6/governance_compliance.md`.
- Final business report: `docs/Healthcare_Insights_Report.docx`, `docs/exported/Healthcare_Insights_Report.pdf`, and `docs/Healthcare_Insights_Report.md`.
