# Explainability Summary

## Risk Model

Top feature importances:

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

Interpretation:

- Higher importance means the model relied more on that transformed feature for splits.
- One-hot encoded categorical values appear as specific category indicators.
- Importance does not prove causality; it indicates predictive contribution in this trained model.

## Claim Model

Top feature importances:

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

Interpretation:

- Higher importance means the model relied more on that transformed feature for splits.
- One-hot encoded categorical values appear as specific category indicators.
- Importance does not prove causality; it indicates predictive contribution in this trained model.
