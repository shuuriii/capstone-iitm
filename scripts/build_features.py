#!/usr/bin/env python3
"""Build the Phase 2 modeling table and data quality outputs."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data_outputs"
REPORT_PATH = ROOT / "docs" / "phase2_data_quality_report.md"

SOURCE_FILES = {
    "patients": ROOT / "patients.csv",
    "visits": ROOT / "visits.csv",
    "billing": ROOT / "billing.csv",
}


def load_sources() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    patients = pd.read_csv(SOURCE_FILES["patients"], parse_dates=["registration_date"])
    visits = pd.read_csv(SOURCE_FILES["visits"], parse_dates=["visit_date"])
    billing = pd.read_csv(SOURCE_FILES["billing"], parse_dates=["billing_date"])
    return patients, visits, billing


def classify_iqr_outliers(series: pd.Series) -> pd.Series:
    """Classify outliers using mild 1.5*IQR and extreme 3*IQR fences."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    mild_low = q1 - 1.5 * iqr
    mild_high = q3 + 1.5 * iqr
    extreme_low = q1 - 3.0 * iqr
    extreme_high = q3 + 3.0 * iqr

    labels = pd.Series("normal", index=series.index, dtype="object")
    labels = labels.mask(series.isna(), "missing")
    labels = labels.mask(series < extreme_low, "extreme_low")
    labels = labels.mask((series >= extreme_low) & (series < mild_low), "mild_low")
    labels = labels.mask((series > mild_high) & (series <= extreme_high), "mild_high")
    labels = labels.mask(series > extreme_high, "extreme_high")
    return labels


def outlier_summary(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    rows = []
    for column in columns:
        labels = classify_iqr_outliers(df[column])
        counts = labels.value_counts().to_dict()
        rows.append(
            {
                "field": column,
                "normal": int(counts.get("normal", 0)),
                "mild_low": int(counts.get("mild_low", 0)),
                "mild_high": int(counts.get("mild_high", 0)),
                "extreme_low": int(counts.get("extreme_low", 0)),
                "extreme_high": int(counts.get("extreme_high", 0)),
                "missing": int(counts.get("missing", 0)),
            }
        )
    return pd.DataFrame(rows)


def safe_group_median(df: pd.DataFrame, group_cols: list[str], value_col: str) -> pd.Series:
    grouped = df.groupby(group_cols, dropna=False)[value_col].transform("median")
    return grouped.fillna(df[value_col].median())


def build_model_table() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    patients, visits, billing = load_sources()

    df = (
        visits.merge(patients, on="patient_id", how="left", validate="many_to_one")
        .merge(billing, on="visit_id", how="left", validate="one_to_one")
    )

    df["approved_amount_missing"] = df["approved_amount"].isna().astype(int)
    df["payment_days_missing"] = df["payment_days"].isna().astype(int)
    df["length_of_stay_hours_missing"] = df["length_of_stay_hours"].isna().astype(int)

    df["length_of_stay_hours_filled"] = df["length_of_stay_hours"].fillna(
        safe_group_median(df, ["department", "visit_type"], "length_of_stay_hours")
    )
    df["payment_days_filled"] = df["payment_days"].fillna(
        safe_group_median(df, ["insurance_provider", "claim_status"], "payment_days")
    )
    approved_fallback = pd.Series(
        np.where(df["claim_status"].eq("Rejected"), 0, df["billed_amount"] * 0.74),
        index=df.index,
    )
    df["approved_amount_filled"] = df["approved_amount"].fillna(approved_fallback)

    patient_features = df.groupby("patient_id").agg(
        visit_frequency=("visit_id", "count"),
        avg_length_of_stay_per_patient=("length_of_stay_hours_filled", "mean"),
        total_billed_per_patient=("billed_amount", "sum"),
        high_risk_visit_count=("risk_score", lambda s: int((s == "High").sum())),
    )
    df = df.merge(patient_features, on="patient_id", how="left")

    provider_rejection_rate = (
        df.assign(is_rejected=df["claim_status"].eq("Rejected").astype(int))
        .groupby("insurance_provider")["is_rejected"]
        .mean()
        .rename("provider_rejection_rate")
    )
    df = df.merge(provider_rejection_rate, on="insurance_provider", how="left")

    reference_date = max(df["visit_date"].max(), df["billing_date"].max())
    df["days_since_registration"] = (reference_date - df["registration_date"]).dt.days
    df["visit_month"] = df["visit_date"].dt.month
    df["visit_day_of_week"] = df["visit_date"].dt.dayofweek
    df["visit_quarter"] = df["visit_date"].dt.quarter
    df["billing_month"] = df["billing_date"].dt.month
    df["billing_lag_days"] = (df["billing_date"] - df["visit_date"]).dt.days
    df["approval_ratio"] = np.where(
        df["billed_amount"] > 0,
        df["approved_amount_filled"] / df["billed_amount"],
        np.nan,
    )

    for column in ["billed_amount", "payment_days", "length_of_stay_hours"]:
        df[f"{column}_outlier_class"] = classify_iqr_outliers(df[column])
        df[f"{column}_is_outlier"] = (
            ~df[f"{column}_outlier_class"].isin(["normal", "missing"])
        ).astype(int)

    model_columns = [
        "visit_id",
        "patient_id",
        "bill_id",
        "age",
        "gender",
        "city",
        "insurance_provider",
        "chronic_flag",
        "department",
        "visit_type",
        "risk_score",
        "doctor_id",
        "claim_status",
        "billed_amount",
        "approved_amount",
        "approved_amount_filled",
        "payment_days",
        "payment_days_filled",
        "length_of_stay_hours",
        "length_of_stay_hours_filled",
        "approved_amount_missing",
        "payment_days_missing",
        "length_of_stay_hours_missing",
        "visit_frequency",
        "avg_length_of_stay_per_patient",
        "total_billed_per_patient",
        "high_risk_visit_count",
        "provider_rejection_rate",
        "days_since_registration",
        "visit_month",
        "visit_day_of_week",
        "visit_quarter",
        "billing_month",
        "billing_lag_days",
        "approval_ratio",
        "billed_amount_outlier_class",
        "payment_days_outlier_class",
        "length_of_stay_hours_outlier_class",
        "billed_amount_is_outlier",
        "payment_days_is_outlier",
        "length_of_stay_hours_is_outlier",
        "visit_date",
        "billing_date",
        "registration_date",
    ]
    model_table = df[model_columns].copy()

    summaries = {
        "missing": missing_summary(df),
        "outliers": outlier_summary(df, ["billed_amount", "payment_days", "length_of_stay_hours"]),
        "provider": provider_summary(df),
        "department": department_summary(df),
        "drift": drift_summary(model_table),
    }
    return model_table, summaries


def missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    fields = ["approved_amount", "payment_days", "length_of_stay_hours"]
    rows = []
    for field in fields:
        missing_count = int(df[field].isna().sum())
        rows.append(
            {
                "field": field,
                "missing_count": missing_count,
                "missing_pct": round(missing_count / len(df) * 100, 2),
            }
        )
    return pd.DataFrame(rows)


def provider_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("insurance_provider")
        .agg(
            claims=("visit_id", "count"),
            rejection_rate=("claim_status", lambda s: round((s == "Rejected").mean(), 4)),
            avg_payment_days=("payment_days", "mean"),
            approval_ratio=("approved_amount_filled", lambda s: round(s.sum() / df.loc[s.index, "billed_amount"].sum(), 4)),
        )
        .reset_index()
        .sort_values("rejection_rate", ascending=False)
    )


def department_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("department")
        .agg(
            visits=("visit_id", "count"),
            avg_length_of_stay_hours=("length_of_stay_hours", "mean"),
            avg_billed_amount=("billed_amount", "mean"),
            high_risk_rate=("risk_score", lambda s: round((s == "High").mean(), 4)),
        )
        .reset_index()
        .sort_values("visits", ascending=False)
    )


def drift_summary(model_table: pd.DataFrame) -> pd.DataFrame:
    dated = model_table.sort_values("visit_date").copy()
    midpoint = len(dated) // 2
    early = dated.iloc[:midpoint]
    late = dated.iloc[midpoint:]
    rows = []
    for field in [
        "billed_amount",
        "approved_amount_filled",
        "payment_days_filled",
        "length_of_stay_hours_filled",
        "approval_ratio",
        "provider_rejection_rate",
    ]:
        early_mean = early[field].mean()
        late_mean = late[field].mean()
        pct_change = np.nan if early_mean == 0 else ((late_mean - early_mean) / early_mean) * 100
        rows.append(
            {
                "feature": field,
                "early_period_mean": round(float(early_mean), 4),
                "late_period_mean": round(float(late_mean), 4),
                "pct_change": round(float(pct_change), 2),
            }
        )
    return pd.DataFrame(rows)


def write_schema(model_table: pd.DataFrame) -> None:
    fields = []
    for column in model_table.columns:
        fields.append(
            {
                "name": column,
                "dtype": str(model_table[column].dtype),
                "missing_count": int(model_table[column].isna().sum()),
                "role": infer_role(column),
            }
        )
    schema = {
        "dataset": "model_table.csv",
        "row_count": int(len(model_table)),
        "column_count": int(model_table.shape[1]),
        "primary_key": "visit_id",
        "grain": "one row per hospital visit with patient and billing attributes",
        "fields": fields,
    }
    (OUTPUT_DIR / "feature_schema.json").write_text(json.dumps(schema, indent=2))


def infer_role(column: str) -> str:
    if column in {"visit_id", "patient_id", "bill_id", "doctor_id"}:
        return "identifier"
    if column.endswith("_missing") or column.endswith("_is_outlier"):
        return "quality_flag"
    if column.endswith("_outlier_class"):
        return "quality_classification"
    if column in {"risk_score", "claim_status"}:
        return "label_candidate"
    if "date" in column:
        return "date"
    return "feature"


def write_report(model_table: pd.DataFrame, summaries: dict[str, pd.DataFrame]) -> None:
    missing = summaries["missing"]
    outliers = summaries["outliers"]
    provider = summaries["provider"]
    department = summaries["department"]
    drift = summaries["drift"]

    report = f"""# Phase 2 Data Quality Report

## Scope

This report profiles the combined patient, visit, and billing dataset used for Phase 2 exploratory analysis and feature engineering.

## Modeling Table

- Rows: {len(model_table):,}
- Columns: {model_table.shape[1]:,}
- Grain: one row per hospital visit with patient and billing attributes.
- Output file: `data_outputs/model_table.csv`

## Missing Value Assessment

{missing.to_markdown(index=False)}

Business interpretation:

- `approved_amount` is missing for {int(missing.loc[missing.field == 'approved_amount', 'missing_count'].iloc[0]):,} records, creating revenue-realization uncertainty.
- `payment_days` is missing for {int(missing.loc[missing.field == 'payment_days', 'missing_count'].iloc[0]):,} records, limiting payment-delay reliability.
- `length_of_stay_hours` has {int(missing.loc[missing.field == 'length_of_stay_hours', 'missing_count'].iloc[0]):,} missing records, so operations analysis is complete for this field.

## Outlier Detection

Outliers are classified using IQR fences: mild outliers beyond 1.5 times IQR and extreme outliers beyond 3.0 times IQR.

{outliers.to_markdown(index=False)}

Business interpretation:

- High billed-amount outliers should be reviewed with approval status because they can materially affect revenue leakage.
- Payment-day outliers identify slow-payer claims and possible follow-up opportunities.
- Length-of-stay outliers may reflect clinical complexity, discharge delays, or data-entry issues.

## Provider Reliability

{provider.to_markdown(index=False)}

## Department Operations

{department.to_markdown(index=False)}

## Drift Summary

The drift summary compares the first half and second half of visits by `visit_date`.

{drift.to_markdown(index=False)}

## Modeling Readiness Notes

- Missing-value indicator columns were added for critical fields before imputation.
- Filled versions of approved amount, payment days, and length of stay preserve original values while creating model-ready numeric features.
- Provider rejection rate, visit frequency, average patient length of stay, days since registration, and time-based visit features were engineered.
- The dataset is ready for baseline modeling, with `risk_score` and `claim_status` available as candidate labels depending on the Phase 3 use case.
"""
    REPORT_PATH.write_text(report)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    REPORT_PATH.parent.mkdir(exist_ok=True)

    model_table, summaries = build_model_table()
    model_table.to_csv(OUTPUT_DIR / "model_table.csv", index=False)
    summaries["drift"].to_csv(OUTPUT_DIR / "drift_summary.csv", index=False)
    write_schema(model_table)
    write_report(model_table, summaries)

    print(f"model_table: {len(model_table):,} rows x {model_table.shape[1]:,} columns")
    print(f"wrote: {OUTPUT_DIR / 'model_table.csv'}")
    print(f"wrote: {OUTPUT_DIR / 'feature_schema.json'}")
    print(f"wrote: {OUTPUT_DIR / 'drift_summary.csv'}")
    print(f"wrote: {REPORT_PATH}")


if __name__ == "__main__":
    main()
