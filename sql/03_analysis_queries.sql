-- Operational Analysis

-- 1. Top 10 departments by total visit volume.
SELECT
    department,
    COUNT(*) AS total_visits
FROM visits
GROUP BY department
ORDER BY total_visits DESC, department
LIMIT 10;

-- 2. Top 5 departments with the highest average length of stay.
SELECT
    department,
    AVG(length_of_stay_hours) AS avg_length_of_stay_hours
FROM visits
WHERE length_of_stay_hours IS NOT NULL
GROUP BY department
ORDER BY avg_length_of_stay_hours DESC, department
LIMIT 5;

-- 3. Percentage of High Risk visits per department.
SELECT
    department,
    COUNT(*) AS total_visits,
    SUM(CASE WHEN risk_score = 'High' THEN 1 ELSE 0 END) AS high_risk_visits,
    ROUND(100.0 * SUM(CASE WHEN risk_score = 'High' THEN 1 ELSE 0 END) / COUNT(*), 2) AS high_risk_visit_pct
FROM visits
GROUP BY department
ORDER BY high_risk_visit_pct DESC, department;

-- 4. Average number of visits per patient by city.
WITH visits_per_patient AS (
    SELECT
        p.city,
        p.patient_id,
        COUNT(v.visit_id) AS visit_count
    FROM patients AS p
    LEFT JOIN visits AS v
        ON v.patient_id = p.patient_id
    GROUP BY p.city, p.patient_id
)
SELECT
    city,
    ROUND(AVG(visit_count), 2) AS avg_visits_per_patient
FROM visits_per_patient
GROUP BY city
ORDER BY avg_visits_per_patient DESC, city;

-- 5. Doctors handling the highest number of High Risk visits.
SELECT
    doctor_id,
    COUNT(*) AS high_risk_visits
FROM visits
WHERE risk_score = 'High'
GROUP BY doctor_id
ORDER BY high_risk_visits DESC, doctor_id
LIMIT 10;

-- Financial Analysis

-- 6. Top 10 insurance providers by total billed amount.
SELECT
    insurance_provider,
    ROUND(SUM(billed_amount), 2) AS total_billed_amount
FROM vw_visit_billing_detail
WHERE billed_amount IS NOT NULL
GROUP BY insurance_provider
ORDER BY total_billed_amount DESC, insurance_provider
LIMIT 10;

-- 7. Top 5 insurance providers with the highest claim rejection rate.
SELECT
    insurance_provider,
    COUNT(*) AS total_claims,
    SUM(CASE WHEN claim_status = 'Rejected' THEN 1 ELSE 0 END) AS rejected_claims,
    ROUND(100.0 * SUM(CASE WHEN claim_status = 'Rejected' THEN 1 ELSE 0 END) / COUNT(*), 2) AS claim_rejection_rate_pct
FROM vw_visit_billing_detail
WHERE bill_id IS NOT NULL
GROUP BY insurance_provider
ORDER BY claim_rejection_rate_pct DESC, total_claims DESC, insurance_provider
LIMIT 5;

-- 8. Average payment delay by insurance provider.
SELECT
    insurance_provider,
    ROUND(AVG(payment_days), 2) AS avg_payment_days
FROM vw_visit_billing_detail
WHERE payment_days IS NOT NULL
GROUP BY insurance_provider
ORDER BY avg_payment_days DESC, insurance_provider;

-- 9. Revenue realization ratio by department.
SELECT
    department,
    ROUND(SUM(approved_amount), 2) AS total_approved_amount,
    ROUND(SUM(billed_amount), 2) AS total_billed_amount,
    ROUND(SUM(approved_amount) / NULLIF(SUM(billed_amount), 0), 4) AS revenue_realization_ratio
FROM vw_visit_billing_detail
WHERE billed_amount IS NOT NULL
GROUP BY department
ORDER BY revenue_realization_ratio ASC, department;

-- 10. Visits where billed amount is high but approved amount is zero or missing.
-- "High" is defined as at or above the 95th percentile proxy: the top 5% by billed amount.
WITH billing_rank AS (
    SELECT
        vbd.*,
        PERCENT_RANK() OVER (ORDER BY billed_amount) AS billed_amount_percent_rank
    FROM vw_visit_billing_detail AS vbd
    WHERE billed_amount IS NOT NULL
)
SELECT
    visit_id,
    patient_id,
    department,
    insurance_provider,
    billed_amount,
    approved_amount,
    claim_status
FROM billing_rank
WHERE billed_amount_percent_rank >= 0.95
  AND COALESCE(approved_amount, 0) = 0
ORDER BY billed_amount DESC, visit_id;
