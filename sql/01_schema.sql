PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS vw_visit_billing_detail;
DROP VIEW IF EXISTS vw_department_kpis;
DROP VIEW IF EXISTS vw_insurance_kpis;

DROP TABLE IF EXISTS billing;
DROP TABLE IF EXISTS visits;
DROP TABLE IF EXISTS patients;

DROP TABLE IF EXISTS raw_billing;
DROP TABLE IF EXISTS raw_visits;
DROP TABLE IF EXISTS raw_patients;

CREATE TABLE raw_patients (
    patient_id TEXT,
    age TEXT,
    gender TEXT,
    city TEXT,
    insurance_provider TEXT,
    chronic_flag TEXT,
    registration_date TEXT
);

CREATE TABLE raw_visits (
    visit_id TEXT,
    patient_id TEXT,
    visit_date TEXT,
    department TEXT,
    visit_type TEXT,
    length_of_stay_hours TEXT,
    risk_score TEXT,
    doctor_id TEXT
);

CREATE TABLE raw_billing (
    bill_id TEXT,
    visit_id TEXT,
    billed_amount TEXT,
    approved_amount TEXT,
    claim_status TEXT,
    payment_days TEXT,
    billing_date TEXT
);

CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY,
    age INTEGER,
    gender TEXT NOT NULL CHECK (gender IN ('M', 'F', 'Other')),
    city TEXT NOT NULL,
    insurance_provider TEXT,
    chronic_flag INTEGER NOT NULL CHECK (chronic_flag IN (0, 1)),
    registration_date TEXT NOT NULL CHECK (registration_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    CHECK (age IS NULL OR age BETWEEN 0 AND 120)
);

CREATE TABLE visits (
    visit_id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    visit_date TEXT NOT NULL CHECK (visit_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    department TEXT NOT NULL,
    visit_type TEXT NOT NULL CHECK (visit_type IN ('ER', 'ICU', 'OPD')),
    length_of_stay_hours REAL,
    risk_score TEXT NOT NULL CHECK (risk_score IN ('Low', 'Medium', 'High')),
    doctor_id INTEGER NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    CHECK (length_of_stay_hours IS NULL OR length_of_stay_hours >= 0)
);

CREATE TABLE billing (
    bill_id INTEGER PRIMARY KEY,
    visit_id INTEGER NOT NULL UNIQUE,
    billed_amount REAL NOT NULL CHECK (billed_amount >= 0),
    approved_amount REAL CHECK (approved_amount IS NULL OR approved_amount >= 0),
    claim_status TEXT NOT NULL CHECK (claim_status IN ('Paid', 'Pending', 'Rejected')),
    payment_days REAL CHECK (payment_days IS NULL OR payment_days >= 0),
    billing_date TEXT NOT NULL CHECK (billing_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    FOREIGN KEY (visit_id) REFERENCES visits(visit_id),
    CHECK (approved_amount IS NULL OR approved_amount <= billed_amount)
);

CREATE INDEX idx_patients_city ON patients(city);
CREATE INDEX idx_patients_insurance_provider ON patients(insurance_provider);
CREATE INDEX idx_visits_patient_id ON visits(patient_id);
CREATE INDEX idx_visits_department ON visits(department);
CREATE INDEX idx_visits_department_risk ON visits(department, risk_score);
CREATE INDEX idx_visits_doctor_risk ON visits(doctor_id, risk_score);
CREATE INDEX idx_visits_visit_date ON visits(visit_date);
CREATE INDEX idx_billing_visit_id ON billing(visit_id);
CREATE INDEX idx_billing_claim_status ON billing(claim_status);
CREATE INDEX idx_billing_billed_amount ON billing(billed_amount);
