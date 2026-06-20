# Phase 6 Drift Detection Report

Generated at: 2026-06-20T07:03:46.583446+00:00

Current data source: `data_outputs/model_table.csv`

## Validation Summary

- Failed checks: 0
- Review checks: 2
- Total validation checks: 25

## Drift Summary

- High drift features: 0
- Moderate drift features: 0
- Total monitored features: 13

## Data Validation Details

| check_type        | field                       | issue                  |   issue_count |   issue_pct | status   |   unseen_values |
|:------------------|:----------------------------|:-----------------------|--------------:|------------:|:---------|----------------:|
| missing_values    | approved_amount             | null_or_missing        |          1318 |       5.272 | review   |             nan |
| missing_values    | payment_days                | null_or_missing        |           790 |       3.16  | review   |             nan |
| missing_values    | length_of_stay_hours        | null_or_missing        |             0 |       0     | pass     |             nan |
| missing_values    | billed_amount               | null_or_missing        |             0 |       0     | pass     |             nan |
| missing_values    | risk_score                  | null_or_missing        |             0 |       0     | pass     |             nan |
| missing_values    | claim_status                | null_or_missing        |             0 |       0     | pass     |             nan |
| numeric_range     | age                         | outside_0_120          |             0 |       0     | pass     |             nan |
| numeric_range     | chronic_flag                | outside_0_1            |             0 |       0     | pass     |             nan |
| numeric_range     | billed_amount               | outside_0_None         |             0 |       0     | pass     |             nan |
| numeric_range     | approved_amount_filled      | outside_0_None         |             0 |       0     | pass     |             nan |
| numeric_range     | payment_days_filled         | outside_0_None         |             0 |       0     | pass     |             nan |
| numeric_range     | length_of_stay_hours_filled | outside_0_None         |             0 |       0     | pass     |             nan |
| numeric_range     | visit_frequency             | outside_1_None         |             0 |       0     | pass     |             nan |
| numeric_range     | provider_rejection_rate     | outside_0_1            |             0 |       0     | pass     |             nan |
| numeric_range     | visit_month                 | outside_1_12           |             0 |       0     | pass     |             nan |
| numeric_range     | visit_day_of_week           | outside_0_6            |             0 |       0     | pass     |             nan |
| numeric_range     | visit_quarter               | outside_1_4            |             0 |       0     | pass     |             nan |
| numeric_range     | billing_month               | outside_1_12           |             0 |       0     | pass     |             nan |
| numeric_range     | approval_ratio              | outside_0_None         |             0 |       0     | pass     |             nan |
| unseen_categories | department                  | unseen_category_values |             0 |       0     | pass     |                 |
| unseen_categories | visit_type                  | unseen_category_values |             0 |       0     | pass     |                 |
| unseen_categories | insurance_provider          | unseen_category_values |             0 |       0     | pass     |                 |
| unseen_categories | city                        | unseen_category_values |             0 |       0     | pass     |                 |
| unseen_categories | risk_score                  | unseen_category_values |             0 |       0     | pass     |                 |
| unseen_categories | claim_status                | unseen_category_values |             0 |       0     | pass     |                 |

## Feature Drift Details

| feature                     | feature_type   |   baseline_mean |   current_mean |   pct_change |   drift_metric | drift_metric_name       | status   |
|:----------------------------|:---------------|----------------:|---------------:|-------------:|---------------:|:------------------------|:---------|
| billed_amount               | numeric        |      20870.8    |     20870.8    |            0 |              0 | psi                     | stable   |
| approved_amount_filled      | numeric        |      16172.2    |     16172.2    |            0 |              0 | psi                     | stable   |
| payment_days_filled         | numeric        |         13.0291 |        13.0291 |            0 |              0 | psi                     | stable   |
| length_of_stay_hours_filled | numeric        |         19.5516 |        19.5516 |            0 |              0 | psi                     | stable   |
| visit_frequency             | numeric        |          5.9609 |         5.9609 |            0 |              0 | psi                     | stable   |
| provider_rejection_rate     | numeric        |          0.1519 |         0.1519 |            0 |              0 | psi                     | stable   |
| approval_ratio              | numeric        |          0.7649 |         0.7649 |            0 |              0 | psi                     | stable   |
| department                  | categorical    |        nan      |       nan      |          nan |              0 | max_category_share_diff | stable   |
| visit_type                  | categorical    |        nan      |       nan      |          nan |              0 | max_category_share_diff | stable   |
| insurance_provider          | categorical    |        nan      |       nan      |          nan |              0 | max_category_share_diff | stable   |
| city                        | categorical    |        nan      |       nan      |          nan |              0 | max_category_share_diff | stable   |
| risk_score                  | categorical    |        nan      |       nan      |          nan |              0 | max_category_share_diff | stable   |
| claim_status                | categorical    |        nan      |       nan      |          nan |              0 | max_category_share_diff | stable   |

## Prediction Drift and Audit Summary

Prediction mix:

| model_name               | prediction   |   count |   share |
|:-------------------------|:-------------|--------:|--------:|
| claim_outcome_classifier | Paid         |       2 |       1 |
| visit_risk_classifier    | Medium       |       2 |       1 |

Audit log summary:

|   records |   unique_model_versions |   unique_input_hashes | first_timestamp_utc              | last_timestamp_utc               |
|----------:|------------------------:|----------------------:|:---------------------------------|:---------------------------------|
|         4 |                       2 |                     2 | 2026-06-20T06:48:19.474378+00:00 | 2026-06-20T06:49:08.402222+00:00 |

## Interpretation

The first monitoring run uses the current modeling table as both baseline and current batch, so feature drift should be stable. In production, pass a new scored batch to `--current-data` and compare it against the Phase 2 baseline.
