# Risk Model Evaluation Report

## Scope

This report evaluates the saved Phase 3 best model artifact `model_artifacts/risk_best_model.joblib` using the same time-based split used during training.

## Core Metrics

| split | accuracy | macro_f1 | weighted_f1 | high_risk_recall |
| --- | ---: | ---: | ---: | ---: |
| train | 0.8023 | 0.8037 | 0.8019 | 0.8295 |
| test | 0.4092 | 0.3485 | 0.4013 | 0.1261 |

## Test Set Per-Class Metrics

| class   |   precision |   recall |     f1 |   support |
|:--------|------------:|---------:|-------:|----------:|
| High    |      0.2213 |   0.1261 | 0.1606 |      1023 |
| Low     |      0.5316 |   0.5218 | 0.5267 |      2480 |
| Medium  |      0.3142 |   0.4162 | 0.358  |      1497 |

## Test Set Confusion Matrix

|               |   predicted_High |   predicted_Low |   predicted_Medium |
|:--------------|-----------------:|----------------:|-------------------:|
| actual_High   |              129 |             457 |                437 |
| actual_Low    |              263 |            1294 |                923 |
| actual_Medium |              191 |             683 |                623 |

## Fairness and Segment Review

Segment performance is computed by `gender`, `city`, and `insurance_provider`. The critical safety metric is recall for `High`.

| segment            |   min_critical_recall |   max_critical_recall |   critical_recall_gap | lowest_recall_group   |
|:-------------------|----------------------:|----------------------:|----------------------:|:----------------------|
| city               |                0.0599 |                0.2364 |                0.1765 | Mumbai                |
| gender             |                0.1136 |                0.1394 |                0.0258 | F                     |
| insurance_provider |                0.0887 |                0.1606 |                0.0719 | CareOne               |

Lowest-performing segment rows by critical-class recall:

| segment            | value      |   rows |   accuracy |   macro_f1 | critical_class   |   critical_class_support |   critical_class_recall |
|:-------------------|:-----------|-------:|-----------:|-----------:|:-----------------|-------------------------:|------------------------:|
| city               | Mumbai     |    816 |     0.4044 |     0.3229 | High             |                      167 |                  0.0599 |
| city               | Chennai    |    824 |     0.426  |     0.3418 | High             |                      167 |                  0.0599 |
| city               | Bangalore  |    829 |     0.4499 |     0.3445 | High             |                      151 |                  0.0728 |
| city               | Hyderabad  |    893 |     0.3785 |     0.3315 | High             |                      189 |                  0.127  |
| city               | Delhi      |    849 |     0.404  |     0.362  | High             |                      184 |                  0.1902 |
| city               | Pune       |    789 |     0.3942 |     0.3596 | High             |                      165 |                  0.2364 |
| gender             | F          |   2530 |     0.4099 |     0.3456 | High             |                      528 |                  0.1136 |
| gender             | M          |   2470 |     0.4085 |     0.3513 | High             |                      495 |                  0.1394 |
| insurance_provider | CareOne    |   1235 |     0.4405 |     0.3536 | High             |                      248 |                  0.0887 |
| insurance_provider | SecureLife |   1200 |     0.4033 |     0.3395 | High             |                      236 |                  0.1186 |

## Explainability Summary

Top model drivers:

| feature                                    |   importance | source_feature                |
|:-------------------------------------------|-------------:|:------------------------------|
| numeric__length_of_stay_hours_filled       |     0.165998 | length_of_stay_hours_filled   |
| numeric__days_since_registration           |     0.122919 | days_since_registration       |
| numeric__doctor_id                         |     0.115506 | doctor_id                     |
| numeric__age                               |     0.109824 | age                           |
| numeric__visit_frequency                   |     0.064177 | visit_frequency               |
| numeric__visit_month                       |     0.060147 | visit_month                   |
| numeric__visit_day_of_week                 |     0.056127 | visit_day_of_week             |
| numeric__visit_quarter                     |     0.029522 | visit_quarter                 |
| numeric__chronic_flag                      |     0.021069 | chronic_flag                  |
| categorical__gender_M                      |     0.016373 | gender_M                      |
| categorical__visit_type_ICU                |     0.016229 | visit_type_ICU                |
| categorical__gender_F                      |     0.016179 | gender_F                      |
| categorical__visit_type_ER                 |     0.016132 | visit_type_ER                 |
| categorical__visit_type_OPD                |     0.015797 | visit_type_OPD                |
| categorical__insurance_provider_MediCareX  |     0.014053 | insurance_provider_MediCareX  |
| categorical__insurance_provider_SecureLife |     0.013525 | insurance_provider_SecureLife |
| categorical__insurance_provider_CareOne    |     0.013516 | insurance_provider_CareOne    |
| categorical__insurance_provider_HealthPlus |     0.013394 | insurance_provider_HealthPlus |
| categorical__department_Orthopedics        |     0.01082  | department_Orthopedics        |
| categorical__department_Neurology          |     0.010177 | department_Neurology          |

## Governance Notes

- This model is suitable for decision support and prioritization, not autonomous clinical or financial action.
- Segment-level recall gaps should be reviewed before production deployment.
- Thresholding, calibration, richer history features, and imbalance strategies such as class-weight tuning, undersampling, or SMOTE should be evaluated in the next iteration.
