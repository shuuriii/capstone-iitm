-- 1. Visits that do not have a corresponding billing record.
SELECT
    v.visit_id,
    v.patient_id,
    v.department,
    v.visit_date
FROM visits AS v
LEFT JOIN billing AS b
    ON b.visit_id = v.visit_id
WHERE b.visit_id IS NULL;

-- 2. Billing records that do not have a corresponding visit.
-- Uses raw_billing so orphan rows can still be detected even though billing.visit_id is constrained.
SELECT
    rb.bill_id,
    rb.visit_id,
    rb.billed_amount,
    rb.billing_date
FROM raw_billing AS rb
LEFT JOIN visits AS v
    ON v.visit_id = CAST(rb.visit_id AS INTEGER)
WHERE v.visit_id IS NULL;

-- 3. Patients with duplicate patient_id values in the source data.
SELECT
    patient_id,
    COUNT(*) AS duplicate_count
FROM raw_patients
GROUP BY patient_id
HAVING COUNT(*) > 1;

-- 4a. Visit records with missing or invalid length_of_stay_hours.
SELECT
    visit_id,
    patient_id,
    length_of_stay_hours
FROM raw_visits
WHERE length_of_stay_hours IS NULL
   OR TRIM(length_of_stay_hours) = ''
   OR CAST(length_of_stay_hours AS REAL) < 0;

-- 4b. Billing records with missing or invalid payment_days.
SELECT
    bill_id,
    visit_id,
    claim_status,
    payment_days
FROM raw_billing
WHERE payment_days IS NULL
   OR TRIM(payment_days) = ''
   OR CAST(payment_days AS REAL) < 0;

-- 5. Visits linked to patients with missing insurance provider information.
SELECT
    v.visit_id,
    v.patient_id,
    p.city,
    p.insurance_provider,
    v.department,
    v.visit_date
FROM visits AS v
JOIN patients AS p
    ON p.patient_id = v.patient_id
WHERE p.insurance_provider IS NULL
   OR TRIM(p.insurance_provider) = '';
