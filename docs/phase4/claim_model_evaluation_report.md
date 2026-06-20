# Claim Model Evaluation Report

## Scope

This report evaluates the saved Phase 3 best model artifact `model_artifacts/claim_best_model.joblib` using the same time-based split used during training.

## Core Metrics

| split | accuracy | macro_f1 | weighted_f1 | rejected_claim_recall |
| --- | ---: | ---: | ---: | ---: |
| train | 0.6669 | 0.6545 | 0.6956 | 0.8954 |
| test | 0.4444 | 0.3743 | 0.4525 | 0.6044 |

## Test Set Per-Class Metrics

| class    |   precision |   recall |     f1 |   support |
|:---------|------------:|---------:|-------:|----------:|
| Paid     |      0.6622 |   0.5279 | 0.5874 |      2997 |
| Pending  |      0.2941 |   0.1569 | 0.2046 |      1275 |
| Rejected |      0.2279 |   0.6044 | 0.331  |       728 |

## Test Set Confusion Matrix

|                 |   predicted_Paid |   predicted_Pending |   predicted_Rejected |
|:----------------|-----------------:|--------------------:|---------------------:|
| actual_Paid     |             1582 |                 374 |                 1041 |
| actual_Pending  |              625 |                 200 |                  450 |
| actual_Rejected |              182 |                 106 |                  440 |

## Fairness and Segment Review

Segment performance is computed by `gender`, `city`, and `insurance_provider`. The critical safety metric is recall for `Rejected`.

| segment            |   min_critical_recall |   max_critical_recall |   critical_recall_gap | lowest_recall_group   |
|:-------------------|----------------------:|----------------------:|----------------------:|:----------------------|
| city               |                0.5448 |                0.6667 |                0.1219 | Chennai               |
| gender             |                0.603  |                0.6056 |                0.0026 | M                     |
| insurance_provider |                0.5698 |                0.6453 |                0.0755 | SecureLife            |

Lowest-performing segment rows by critical-class recall:

| segment            | value      |   rows |   accuracy |   macro_f1 | critical_class   |   critical_class_support |   critical_class_recall |
|:-------------------|:-----------|-------:|-----------:|-----------:|:-----------------|-------------------------:|------------------------:|
| city               | Chennai    |    824 |     0.443  |     0.3851 | Rejected         |                      134 |                  0.5448 |
| city               | Mumbai     |    816 |     0.4461 |     0.3713 | Rejected         |                      127 |                  0.5591 |
| city               | Hyderabad  |    893 |     0.4726 |     0.3916 | Rejected         |                      142 |                  0.6056 |
| city               | Bangalore  |    829 |     0.4427 |     0.3813 | Rejected         |                      126 |                  0.627  |
| city               | Pune       |    789 |     0.4094 |     0.3396 | Rejected         |                       94 |                  0.6489 |
| city               | Delhi      |    849 |     0.4488 |     0.3737 | Rejected         |                      105 |                  0.6667 |
| gender             | M          |   2470 |     0.4348 |     0.3677 | Rejected         |                      335 |                  0.603  |
| gender             | F          |   2530 |     0.4538 |     0.3805 | Rejected         |                      393 |                  0.6056 |
| insurance_provider | SecureLife |   1200 |     0.45   |     0.3633 | Rejected         |                      179 |                  0.5698 |
| insurance_provider | MediCareX  |   1368 |     0.4364 |     0.3709 | Rejected         |                      198 |                  0.5707 |

## Explainability Summary

Top model drivers:

| feature                                 |   importance | source_feature              |
|:----------------------------------------|-------------:|:----------------------------|
| numeric__billed_amount                  |     0.279473 | billed_amount               |
| numeric__length_of_stay_hours_filled    |     0.078779 | length_of_stay_hours_filled |
| numeric__billing_lag_days               |     0.077019 | billing_lag_days            |
| numeric__days_since_registration        |     0.076857 | days_since_registration     |
| numeric__doctor_id                      |     0.071197 | doctor_id                   |
| numeric__age                            |     0.070415 | age                         |
| numeric__billing_month                  |     0.038511 | billing_month               |
| numeric__visit_frequency                |     0.037579 | visit_frequency             |
| numeric__visit_month                    |     0.035661 | visit_month                 |
| numeric__visit_day_of_week              |     0.03352  | visit_day_of_week           |
| numeric__visit_quarter                  |     0.015339 | visit_quarter               |
| numeric__chronic_flag                   |     0.012417 | chronic_flag                |
| categorical__risk_score_Low             |     0.010263 | risk_score_Low              |
| categorical__gender_F                   |     0.009471 | gender_F                    |
| categorical__gender_M                   |     0.009414 | gender_M                    |
| categorical__visit_type_OPD             |     0.009049 | visit_type_OPD              |
| categorical__visit_type_ICU             |     0.008853 | visit_type_ICU              |
| categorical__visit_type_ER              |     0.008706 | visit_type_ER               |
| categorical__risk_score_Medium          |     0.008195 | risk_score_Medium           |
| categorical__insurance_provider_CareOne |     0.00804  | insurance_provider_CareOne  |

## Governance Notes

- This model is suitable for decision support and prioritization, not autonomous clinical or financial action.
- Segment-level recall gaps should be reviewed before production deployment.
- Thresholding, calibration, richer history features, and imbalance strategies such as class-weight tuning, undersampling, or SMOTE should be evaluated in the next iteration.
