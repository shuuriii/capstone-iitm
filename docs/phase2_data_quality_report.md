# Phase 2 Data Quality Report

## Scope

This report profiles the combined patient, visit, and billing dataset used for Phase 2 exploratory analysis and feature engineering.

## Modeling Table

- Rows: 25,000
- Columns: 44
- Grain: one row per hospital visit with patient and billing attributes.
- Output file: `data_outputs/model_table.csv`

## Missing Value Assessment

| field                |   missing_count |   missing_pct |
|:---------------------|----------------:|--------------:|
| approved_amount      |            1318 |          5.27 |
| payment_days         |             790 |          3.16 |
| length_of_stay_hours |               0 |          0    |

Business interpretation:

- `approved_amount` is missing for 1,318 records, creating revenue-realization uncertainty.
- `payment_days` is missing for 790 records, limiting payment-delay reliability.
- `length_of_stay_hours` has 0 missing records, so operations analysis is complete for this field.

## Outlier Detection

Outliers are classified using IQR fences: mild outliers beyond 1.5 times IQR and extreme outliers beyond 3.0 times IQR.

| field                |   normal |   mild_low |   mild_high |   extreme_low |   extreme_high |   missing |
|:---------------------|---------:|-----------:|------------:|--------------:|---------------:|----------:|
| billed_amount        |    24627 |          0 |         369 |             0 |              4 |         0 |
| payment_days         |    23701 |          0 |         490 |             0 |             19 |       790 |
| length_of_stay_hours |    24744 |          0 |         256 |             0 |              0 |         0 |

Business interpretation:

- High billed-amount outliers should be reviewed with approval status because they can materially affect revenue leakage.
- Payment-day outliers identify slow-payer claims and possible follow-up opportunities.
- Length-of-stay outliers may reflect clinical complexity, discharge delays, or data-entry issues.

## Provider Reliability

| insurance_provider   |   claims |   rejection_rate |   avg_payment_days |   approval_ratio |
|:---------------------|---------:|-----------------:|-------------------:|-----------------:|
| SecureLife           |     5965 |           0.1569 |            13.0781 |           0.7735 |
| MediCareX            |     6532 |           0.1525 |            13.009  |           0.7741 |
| HealthPlus           |     6220 |           0.1497 |            13.0818 |           0.7756 |
| CareOne              |     6283 |           0.1487 |            13.0269 |           0.7763 |

## Department Operations

| department   |   visits |   avg_length_of_stay_hours |   avg_billed_amount |   high_risk_rate |
|:-------------|---------:|---------------------------:|--------------------:|-----------------:|
| General      |     4228 |                    19.4349 |             20608.2 |           0.1984 |
| ER           |     4220 |                    19.535  |             21015.9 |           0.2066 |
| Neurology    |     4165 |                    19.7181 |             20962.8 |           0.2031 |
| Orthopedics  |     4164 |                    19.6627 |             21088.2 |           0.2022 |
| Cardiology   |     4159 |                    19.601  |             20695.2 |           0.1899 |
| ICU          |     4064 |                    19.3552 |             20855.7 |           0.2079 |

## Drift Summary

The drift summary compares the first half and second half of visits by `visit_date`.

| feature                     |   early_period_mean |   late_period_mean |   pct_change |
|:----------------------------|--------------------:|-------------------:|-------------:|
| billed_amount               |          20704.2    |         21037.4    |         1.61 |
| approved_amount_filled      |          15963.3    |         16381.1    |         2.62 |
| payment_days_filled         |             13.0876 |            12.9706 |        -0.89 |
| length_of_stay_hours_filled |             19.6647 |            19.4384 |        -1.15 |
| approval_ratio              |              0.7626 |             0.7672 |         0.61 |
| provider_rejection_rate     |              0.1519 |             0.1519 |         0    |

## Modeling Readiness Notes

- Missing-value indicator columns were added for critical fields before imputation.
- Filled versions of approved amount, payment days, and length of stay preserve original values while creating model-ready numeric features.
- Provider rejection rate, visit frequency, average patient length of stay, days since registration, and time-based visit features were engineered.
- The dataset is ready for baseline modeling, with `risk_score` and `claim_status` available as candidate labels depending on the Phase 3 use case.
