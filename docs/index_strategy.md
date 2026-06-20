# Phase 1 Index Strategy

The primary keys automatically index `patients.patient_id`, `visits.visit_id`, and `billing.bill_id`.

Indexes are added on columns that are frequently used in:

- `JOIN` conditions, such as `visits.patient_id` and `billing.visit_id`
- `WHERE` filters, such as `risk_score`, `claim_status`, and `billed_amount`
- `GROUP BY` analysis, such as `department`, `city`, `insurance_provider`, and `doctor_id`
- future dashboard filters, such as `visit_date`

## How Indexes Work

Without an index, the database may scan every row in a table to find matching records. That is acceptable for a small CSV, but it becomes slow as the hospital data grows.

An index is like a sorted lookup structure. When a query filters or joins on an indexed column, SQLite can jump directly to matching values instead of reading the full table.

Example:

```sql
SELECT *
FROM visits
WHERE patient_id = 756;
```

Because `visits.patient_id` has an index, SQLite can quickly find visits for patient `756`.

Another example:

```sql
SELECT *
FROM visits AS v
JOIN billing AS b
    ON b.visit_id = v.visit_id;
```

Because `billing.visit_id` is indexed, the database can quickly find the billing row for each visit.

Indexes improve read performance, but they slightly slow down inserts/updates because the index also has to be maintained. For this analytics layer, that tradeoff is appropriate because the main workload is reporting and analysis.

| Index | Helps Queries | Reason |
| --- | --- | --- |
| `idx_patients_city` | Average visits per patient by city | Speeds patient grouping and city-level aggregation. |
| `idx_patients_insurance_provider` | Insurance billed amount, rejection rate, payment delay | Speeds grouping after joining visits/billing to patient insurance. |
| `idx_visits_patient_id` | Patient visit counts, visit-to-patient joins, FK enforcement | Speeds joins from visits to patients and validates visit imports. |
| `idx_visits_department` | Department volume, length of stay, realization ratio | Speeds department grouping and sorting. |
| `idx_visits_department_risk` | High Risk percentage per department | Covers department/risk grouping and conditional risk counts. |
| `idx_visits_doctor_risk` | Doctors with the most High Risk visits | Speeds filtering by `risk_score = 'High'` and grouping by doctor. |
| `idx_visits_visit_date` | Future date-window dashboards | Supports common leadership reporting by period. |
| `idx_billing_visit_id` | Visit billing joins, missing billing checks | Speeds joins from visits to billing and supports the one-bill-per-visit relationship. |
| `idx_billing_claim_status` | Rejection-rate analysis | Speeds claim-status filtering and conditional aggregation. |
| `idx_billing_billed_amount` | High billed / zero approved leakage checks | Speeds top-value billing analysis and percentile/ranking workflows. |

## Query-to-Index Mapping

| Required Query | Helpful Indexes | Why These Indexes Help |
| --- | --- | --- |
| Top 10 departments by total visit volume | `idx_visits_department` | Query groups visits by `department`. |
| Top 5 departments with highest average length of stay | `idx_visits_department` | Query groups visits by `department` before calculating average `length_of_stay_hours`. |
| Percentage of High Risk visits per department | `idx_visits_department_risk` | Query groups by `department` and checks `risk_score = 'High'`. Composite index keeps both columns together. |
| Average number of visits per patient by city | `idx_patients_city`, `idx_visits_patient_id` | Query groups patients by `city` and joins visits through `patient_id`. |
| Doctors handling highest number of High Risk visits | `idx_visits_doctor_risk` | Query filters/counts High Risk visits and groups by `doctor_id`. |
| Top 10 insurance providers by total billed amount | `idx_patients_insurance_provider`, `idx_visits_patient_id`, `idx_billing_visit_id` | Query joins patients, visits, and billing, then groups by insurer. |
| Insurance providers with highest claim rejection rate | `idx_patients_insurance_provider`, `idx_billing_claim_status`, `idx_billing_visit_id` | Query groups by insurer and counts `claim_status = 'Rejected'`. |
| Average payment delay by insurance provider | `idx_patients_insurance_provider`, `idx_billing_visit_id` | Query joins billing to patient insurance and groups by insurer. |
| Revenue realization ratio by department | `idx_visits_department`, `idx_billing_visit_id` | Query groups by department and joins billing amounts by visit. |
| High billed amount but zero or missing approved amount | `idx_billing_billed_amount`, `idx_billing_visit_id` | Query ranks or filters by `billed_amount` and joins back to visit details. |
| Visits without corresponding billing record | `idx_billing_visit_id` | Query left joins visits to billing using `visit_id`. |
| Billing records without corresponding visit | Primary key index on `visits.visit_id` | Query checks whether each billing `visit_id` exists in visits. |
| Duplicate patient IDs | Primary key index on `patients.patient_id`; raw table scan for source duplicates | Final table prevents duplicates; raw table check scans source data to detect duplicate IDs before enforcement. |
| Missing or invalid length of stay | No dedicated index | This is a full data-quality scan of `raw_visits`; an index is not useful for checking all rows. |
| Missing or invalid payment days | No dedicated index | This is a full data-quality scan of `raw_billing`; an index is not useful for checking all rows. |
| Visits linked to patients with missing insurance provider | `idx_visits_patient_id`, `idx_patients_insurance_provider` | Query joins visits to patients and filters missing/blank insurer values. |

For this data volume, full scans are still acceptable. These indexes document the access paths that matter once the hospital dataset grows or the same views power dashboards.
