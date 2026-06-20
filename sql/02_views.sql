CREATE VIEW vw_visit_billing_detail AS
SELECT
    v.visit_id,
    v.patient_id,
    p.city,
    p.insurance_provider,
    v.visit_date,
    v.department,
    v.visit_type,
    v.length_of_stay_hours,
    v.risk_score,
    v.doctor_id,
    b.bill_id,
    b.billed_amount,
    b.approved_amount,
    b.claim_status,
    b.payment_days,
    b.billing_date
FROM visits AS v
JOIN patients AS p
    ON p.patient_id = v.patient_id
LEFT JOIN billing AS b
    ON b.visit_id = v.visit_id;

CREATE VIEW vw_department_kpis AS
SELECT
    department,
    COUNT(*) AS total_visits,
    AVG(length_of_stay_hours) AS avg_length_of_stay_hours,
    100.0 * SUM(CASE WHEN risk_score = 'High' THEN 1 ELSE 0 END) / COUNT(*) AS high_risk_visit_pct,
    SUM(billed_amount) AS total_billed_amount,
    SUM(approved_amount) AS total_approved_amount,
    SUM(approved_amount) / NULLIF(SUM(billed_amount), 0) AS revenue_realization_ratio
FROM vw_visit_billing_detail
GROUP BY department;

CREATE VIEW vw_insurance_kpis AS
SELECT
    insurance_provider,
    COUNT(*) AS billed_visits,
    SUM(billed_amount) AS total_billed_amount,
    100.0 * SUM(CASE WHEN claim_status = 'Rejected' THEN 1 ELSE 0 END) / COUNT(*) AS claim_rejection_rate_pct,
    AVG(payment_days) AS avg_payment_days,
    SUM(approved_amount) / NULLIF(SUM(billed_amount), 0) AS revenue_realization_ratio
FROM vw_visit_billing_detail
WHERE bill_id IS NOT NULL
GROUP BY insurance_provider;
