#!/usr/bin/env python3
import csv
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "hospital_analytics.db"


RAW_TABLES = {
    "raw_patients": ("patients.csv", ["patient_id", "age", "gender", "city", "insurance_provider", "chronic_flag", "registration_date"]),
    "raw_visits": ("visits.csv", ["visit_id", "patient_id", "visit_date", "department", "visit_type", "length_of_stay_hours", "risk_score", "doctor_id"]),
    "raw_billing": ("billing.csv", ["bill_id", "visit_id", "billed_amount", "approved_amount", "claim_status", "payment_days", "billing_date"]),
}


def run_script(conn: sqlite3.Connection, relative_path: str) -> None:
    conn.executescript((ROOT / relative_path).read_text())


def load_raw_csv(conn: sqlite3.Connection, table_name: str, csv_name: str, columns: list[str]) -> None:
    csv_path = ROOT / csv_name
    placeholders = ", ".join(["?"] * len(columns))
    column_list = ", ".join(columns)
    sql = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"

    with csv_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [
            [None if row[column] == "" else row[column] for column in columns]
            for row in reader
        ]

    conn.executemany(sql, rows)


def populate_final_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        INSERT INTO patients (
            patient_id,
            age,
            gender,
            city,
            insurance_provider,
            chronic_flag,
            registration_date
        )
        SELECT
            CAST(patient_id AS INTEGER),
            CAST(age AS INTEGER),
            gender,
            city,
            NULLIF(TRIM(insurance_provider), ''),
            CAST(chronic_flag AS INTEGER),
            registration_date
        FROM raw_patients;

        INSERT INTO visits (
            visit_id,
            patient_id,
            visit_date,
            department,
            visit_type,
            length_of_stay_hours,
            risk_score,
            doctor_id
        )
        SELECT
            CAST(visit_id AS INTEGER),
            CAST(patient_id AS INTEGER),
            visit_date,
            department,
            visit_type,
            CAST(length_of_stay_hours AS REAL),
            risk_score,
            CAST(doctor_id AS INTEGER)
        FROM raw_visits;

        INSERT INTO billing (
            bill_id,
            visit_id,
            billed_amount,
            approved_amount,
            claim_status,
            payment_days,
            billing_date
        )
        SELECT
            CAST(bill_id AS INTEGER),
            CAST(visit_id AS INTEGER),
            CAST(billed_amount AS REAL),
            CAST(approved_amount AS REAL),
            claim_status,
            CAST(payment_days AS REAL),
            billing_date
        FROM raw_billing;
        """
    )


def table_count(conn: sqlite3.Connection, table_name: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        run_script(conn, "sql/01_schema.sql")
        for table_name, (csv_name, columns) in RAW_TABLES.items():
            load_raw_csv(conn, table_name, csv_name, columns)
        populate_final_tables(conn)
        run_script(conn, "sql/02_views.sql")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    conn = sqlite3.connect(DB_PATH)
    try:
        for table_name in ["patients", "visits", "billing"]:
            print(f"{table_name}: {table_count(conn, table_name):,} rows")
        print(f"database: {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
