# Phase 1 Analysis Results

Generated from `hospital_analytics.db` after running:

```bash
python3 scripts/build_sqlite_db.py
```

The SQL used for these results is stored in `sql/03_analysis_queries.sql` and `sql/04_data_quality_checks.sql`.

## Operational Analysis

### 1. Top 10 Departments by Total Visit Volume

The dataset contains 6 departments, so all available departments are shown.

| rank | department | total_visits |
| ---: | --- | ---: |
| 1 | General | 4,228 |
| 2 | ER | 4,220 |
| 3 | Neurology | 4,165 |
| 4 | Orthopedics | 4,164 |
| 5 | Cardiology | 4,159 |
| 6 | ICU | 4,064 |

Observation: Visit volume is evenly distributed across departments. General has the highest volume, while ICU has the lowest.

### 2. Top 5 Departments with Highest Average Length of Stay

| rank | department | avg_length_of_stay_hours |
| ---: | --- | ---: |
| 1 | Neurology | 19.72 |
| 2 | Orthopedics | 19.66 |
| 3 | Cardiology | 19.60 |
| 4 | ER | 19.53 |
| 5 | General | 19.43 |

Observation: Neurology has the highest average length of stay, which may indicate higher case complexity or slower patient throughput.

### 3. Percentage of High Risk Visits per Department

| department | total_visits | high_risk_visits | high_risk_visit_pct |
| --- | ---: | ---: | ---: |
| ICU | 4,064 | 845 | 20.79 |
| ER | 4,220 | 872 | 20.66 |
| Neurology | 4,165 | 846 | 20.31 |
| Orthopedics | 4,164 | 842 | 20.22 |
| General | 4,228 | 839 | 19.84 |
| Cardiology | 4,159 | 790 | 18.99 |

Observation: ICU has the highest High Risk visit percentage at 20.79%, followed closely by ER.

### 4. Average Number of Visits per Patient by City

| city | avg_visits_per_patient |
| --- | ---: |
| Pune | 5.08 |
| Hyderabad | 5.03 |
| Bangalore | 5.01 |
| Mumbai | 5.01 |
| Chennai | 4.96 |
| Delhi | 4.91 |

Observation: Pune patients average the most visits per patient. Delhi has the lowest average in this dataset.

### 5. Doctors Handling the Highest Number of High Risk Visits

| rank | doctor_id | high_risk_visits |
| ---: | ---: | ---: |
| 1 | 174 | 71 |
| 2 | 198 | 69 |
| 3 | 169 | 68 |
| 4 | 177 | 67 |
| 5 | 105 | 65 |
| 6 | 135 | 65 |
| 7 | 180 | 64 |
| 8 | 188 | 64 |
| 9 | 131 | 62 |
| 10 | 108 | 61 |

Observation: Doctor 174 handled the highest number of High Risk visits.

## Financial Analysis

### 1. Top 10 Insurance Providers by Total Billed Amount

The dataset contains 4 insurance providers, so all available providers are shown.

| rank | insurance_provider | total_billed_amount |
| ---: | --- | ---: |
| 1 | MediCareX | 134,591,163.08 |
| 2 | CareOne | 130,707,992.64 |
| 3 | HealthPlus | 130,180,740.75 |
| 4 | SecureLife | 126,289,039.58 |

Observation: MediCareX has the highest total billed amount.

### 2. Top 5 Insurance Providers with Highest Claim Rejection Rate

The dataset contains 4 insurance providers, so all available providers are shown.

| rank | insurance_provider | total_claims | rejected_claims | claim_rejection_rate_pct |
| ---: | --- | ---: | ---: | ---: |
| 1 | SecureLife | 5,965 | 936 | 15.69 |
| 2 | MediCareX | 6,532 | 996 | 15.25 |
| 3 | HealthPlus | 6,220 | 931 | 14.97 |
| 4 | CareOne | 6,283 | 934 | 14.87 |

Observation: SecureLife has the highest rejection rate at 15.69%.

### 3. Average Payment Delay by Insurance Provider

| insurance_provider | avg_payment_days |
| --- | ---: |
| HealthPlus | 13.08 |
| SecureLife | 13.08 |
| CareOne | 13.03 |
| MediCareX | 13.01 |

Observation: Average payment delay is very similar across providers, ranging from 13.01 to 13.08 days.

### 4. Revenue Realization Ratio by Department

Revenue realization ratio is calculated as:

```text
approved_amount / billed_amount
```

| department | total_approved_amount | total_billed_amount | revenue_realization_ratio |
| --- | ---: | ---: | ---: |
| Cardiology | 63,705,806.68 | 86,071,256.19 | 0.7402 |
| ER | 65,672,329.38 | 88,686,960.35 | 0.7405 |
| Neurology | 64,708,778.69 | 87,310,048.09 | 0.7411 |
| General | 64,690,870.95 | 87,131,451.86 | 0.7425 |
| Orthopedics | 65,211,585.83 | 87,811,455.80 | 0.7426 |
| ICU | 63,166,516.84 | 84,757,763.76 | 0.7453 |

Observation: Cardiology has the lowest revenue realization ratio, while ICU has the highest. All departments realize roughly 74% of billed amounts.

### 5. Visits Where Billed Amount Is High but Approved Amount Is Zero or Missing

For this analysis, "high billed amount" is defined as visits in the top 5% by billed amount. The query found 72 flagged visits. The flagged billed amount range is 44,175.34 to 78,054.79.

Top flagged visits by billed amount:

| visit_id | patient_id | department | insurance_provider | billed_amount | approved_amount | claim_status |
| ---: | ---: | --- | --- | ---: | ---: | --- |
| 1570 | 2685 | General | HealthPlus | 78,054.79 | missing | Paid |
| 18381 | 3817 | General | HealthPlus | 68,213.53 | 0.00 | Rejected |
| 15092 | 4096 | Neurology | CareOne | 66,410.33 | missing | Paid |
| 2638 | 4581 | Neurology | CareOne | 65,167.44 | missing | Paid |
| 8089 | 1774 | ER | HealthPlus | 62,661.81 | missing | Paid |
| 19310 | 931 | ICU | MediCareX | 60,510.22 | missing | Paid |
| 24623 | 2828 | Neurology | SecureLife | 58,275.40 | missing | Paid |
| 18189 | 3339 | Neurology | HealthPlus | 57,521.12 | missing | Paid |
| 14702 | 4844 | Orthopedics | HealthPlus | 56,848.91 | missing | Paid |
| 5131 | 2167 | Orthopedics | MediCareX | 56,736.52 | missing | Paid |

Observation: These visits are revenue leakage risks because billed amounts are large, but approval is zero or unavailable.

## Data Quality and Integrity Checks

### 1. Visits Without a Corresponding Billing Record

| check_name | issue_count |
| --- | ---: |
| visits_without_billing | 0 |

Result: Every visit in the final `visits` table has a corresponding billing record.

### 2. Billing Records Without a Corresponding Visit

| check_name | issue_count |
| --- | ---: |
| billing_without_visit | 0 |

Result: Every source billing record references a valid visit.

### 3. Patients with Duplicate `patient_id` Values

| check_name | issue_count |
| --- | ---: |
| duplicate_patient_ids | 0 |

Result: No duplicate patient IDs were found in the source patient data.

### 4. Records with Missing or Invalid `length_of_stay_hours` or `payment_days`

| data_quality_check | issue_count |
| --- | ---: |
| missing_or_invalid_length_of_stay_hours | 0 |
| missing_or_invalid_payment_days | 790 |

Result: No invalid length-of-stay records were found. However, 790 billing records have missing or invalid `payment_days`.

Sample records with missing or invalid `payment_days`:

| bill_id | visit_id | claim_status | billed_amount | approved_amount | payment_days |
| ---: | ---: | --- | ---: | ---: | --- |
| 3 | 3 | Paid | 5,038.97 | 5,038.97 | missing |
| 22 | 22 | Paid | 31,418.34 | 31,418.34 | missing |
| 41 | 41 | Paid | 12,924.18 | 12,924.18 | missing |
| 66 | 66 | Paid | 28,126.25 | 28,126.25 | missing |
| 109 | 109 | Pending | 1,233.62 | 911.46 | missing |
| 120 | 120 | Paid | 23,218.37 | missing | missing |
| 133 | 133 | Paid | 500.00 | 500.00 | missing |
| 173 | 173 | Pending | 11,493.55 | 8,735.77 | missing |
| 181 | 181 | Paid | 49,363.32 | 49,363.32 | missing |
| 237 | 237 | Paid | 66,037.73 | 66,037.73 | missing |

### 5. Visits Linked to Patients with Missing Insurance Provider Information

| check_name | issue_count |
| --- | ---: |
| visits_missing_patient_insurance | 0 |

Result: No visits are linked to patients with missing insurance provider information.

## Summary

The relational layer loaded successfully with 5,000 patients, 25,000 visits, and 25,000 billing records. Referential integrity is clean: no orphan visits, no orphan billing rows, and no duplicate patient IDs were detected. The main data-quality issue is missing `payment_days` in 790 billing records. The main financial risk area is the set of 72 high-billed visits where `approved_amount` is zero or missing.
