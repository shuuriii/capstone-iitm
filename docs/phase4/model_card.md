# Consolidated Model Card

## Intended Use

The Phase 4 models are intended for hospital decision support: visit-risk triage and claim-outcome prioritization. They should support human review rather than replace clinical or finance judgment.

## Data and Split

- Source: `data_outputs/model_table.csv`
- Split: earliest 80% of visits for training, latest 20% for testing by `visit_date`.
- Protected or sensitive review segments: `gender`, `city`, and `insurance_provider`.

## Performance Summary

| model | test_accuracy | test_macro_f1 | critical_class | critical_class_recall |
| --- | ---: | ---: | --- | ---: |
| risk_model | 0.4092 | 0.3485 | High | 0.1261 |
| claim_model | 0.4444 | 0.3743 | Rejected | 0.6044 |

## Key Limitations

- Current features are structured operational and billing fields; diagnosis, procedure, prior-authorization, and longitudinal payer-history features are not yet available.
- Models show modest macro F1, so outputs should be treated as triage signals.
- Segment recall gaps require governance review before external or high-stakes use.

## Recommended Controls

- Monitor recall for High Risk visits and Rejected claims monthly.
- Review performance by gender, city, and insurance provider after every retraining.
- Use human-in-the-loop workflows for any action affecting clinical care or claim handling.
- Explore class-weight tuning, tree-depth tuning, interaction features, and resampling strategies for imbalance mitigation.