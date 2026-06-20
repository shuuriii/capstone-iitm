#!/usr/bin/env python3
"""Phase 6 monitoring, drift detection, and governance reporting."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "data_outputs" / "model_table.csv"
SCHEMA_PATH = ROOT / "data_outputs" / "feature_schema.json"
PREDICTION_LOG_PATH = ROOT / "logs" / "predictions.jsonl"
REPORT_DIR = ROOT / "docs" / "phase6"

CRITICAL_FIELDS = [
    "approved_amount",
    "payment_days",
    "length_of_stay_hours",
    "billed_amount",
    "risk_score",
    "claim_status",
]

NUMERIC_RANGE_RULES = {
    "age": (0, 120),
    "chronic_flag": (0, 1),
    "billed_amount": (0, None),
    "approved_amount_filled": (0, None),
    "payment_days_filled": (0, None),
    "length_of_stay_hours_filled": (0, None),
    "visit_frequency": (1, None),
    "provider_rejection_rate": (0, 1),
    "visit_month": (1, 12),
    "visit_day_of_week": (0, 6),
    "visit_quarter": (1, 4),
    "billing_month": (1, 12),
    "approval_ratio": (0, None),
}

MONITORED_NUMERIC_FEATURES = [
    "billed_amount",
    "approved_amount_filled",
    "payment_days_filled",
    "length_of_stay_hours_filled",
    "visit_frequency",
    "provider_rejection_rate",
    "approval_ratio",
]

MONITORED_CATEGORICAL_FEATURES = [
    "department",
    "visit_type",
    "insurance_provider",
    "city",
    "risk_score",
    "claim_status",
]


def read_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing input data: {path}")
    return pd.read_csv(path, parse_dates=["visit_date", "billing_date", "registration_date"])


def read_schema() -> dict[str, Any]:
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Missing schema: {SCHEMA_PATH}")
    return json.loads(SCHEMA_PATH.read_text())


def missing_value_checks(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for field in CRITICAL_FIELDS:
        if field not in df.columns:
            rows.append(
                {
                    "check_type": "missing_values",
                    "field": field,
                    "issue": "missing_column",
                    "issue_count": len(df),
                    "issue_pct": 100.0,
                    "status": "fail",
                }
            )
            continue
        issue_count = int(df[field].isna().sum())
        rows.append(
            {
                "check_type": "missing_values",
                "field": field,
                "issue": "null_or_missing",
                "issue_count": issue_count,
                "issue_pct": round(issue_count / len(df) * 100, 4),
                "status": "pass" if issue_count == 0 else "review",
            }
        )
    return pd.DataFrame(rows)


def numeric_range_checks(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for field, (min_value, max_value) in NUMERIC_RANGE_RULES.items():
        if field not in df.columns:
            rows.append(
                {
                    "check_type": "numeric_range",
                    "field": field,
                    "issue": "missing_column",
                    "issue_count": len(df),
                    "issue_pct": 100.0,
                    "status": "fail",
                }
            )
            continue
        series = pd.to_numeric(df[field], errors="coerce")
        invalid = series.isna()
        if min_value is not None:
            invalid = invalid | (series < min_value)
        if max_value is not None:
            invalid = invalid | (series > max_value)
        issue_count = int(invalid.sum())
        rows.append(
            {
                "check_type": "numeric_range",
                "field": field,
                "issue": f"outside_{min_value}_{max_value}",
                "issue_count": issue_count,
                "issue_pct": round(issue_count / len(df) * 100, 4),
                "status": "pass" if issue_count == 0 else "fail",
            }
        )
    return pd.DataFrame(rows)


def unseen_category_checks(baseline: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for field in MONITORED_CATEGORICAL_FEATURES:
        if field not in baseline.columns or field not in current.columns:
            rows.append(
                {
                    "check_type": "unseen_categories",
                    "field": field,
                    "issue": "missing_column",
                    "issue_count": len(current),
                    "issue_pct": 100.0,
                    "status": "fail",
                    "unseen_values": "",
                }
            )
            continue
        baseline_values = set(baseline[field].dropna().astype(str).unique())
        current_values = set(current[field].dropna().astype(str).unique())
        unseen = sorted(current_values - baseline_values)
        count = int(current[field].astype(str).isin(unseen).sum()) if unseen else 0
        rows.append(
            {
                "check_type": "unseen_categories",
                "field": field,
                "issue": "unseen_category_values",
                "issue_count": count,
                "issue_pct": round(count / len(current) * 100, 4),
                "status": "pass" if count == 0 else "review",
                "unseen_values": ", ".join(unseen[:20]),
            }
        )
    return pd.DataFrame(rows)


def population_stability_index(expected: pd.Series, actual: pd.Series, bins: int = 10) -> float:
    expected = pd.to_numeric(expected, errors="coerce").dropna()
    actual = pd.to_numeric(actual, errors="coerce").dropna()
    if expected.empty or actual.empty or expected.nunique() < 2:
        return 0.0

    edges = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    edges[0] = -np.inf
    edges[-1] = np.inf

    expected_counts = pd.cut(expected, edges, include_lowest=True).value_counts(sort=False)
    actual_counts = pd.cut(actual, edges, include_lowest=True).value_counts(sort=False)
    expected_pct = expected_counts / expected_counts.sum()
    actual_pct = actual_counts / actual_counts.sum()
    expected_pct = expected_pct.replace(0, 0.0001)
    actual_pct = actual_pct.replace(0, 0.0001)
    return float(((actual_pct - expected_pct) * np.log(actual_pct / expected_pct)).sum())


def drift_status(value: float) -> str:
    if value >= 0.25:
        return "high_drift"
    if value >= 0.10:
        return "moderate_drift"
    return "stable"


def numeric_drift(baseline: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for field in MONITORED_NUMERIC_FEATURES:
        if field not in baseline.columns or field not in current.columns:
            continue
        baseline_mean = baseline[field].mean()
        current_mean = current[field].mean()
        pct_change = np.nan if baseline_mean == 0 else (current_mean - baseline_mean) / baseline_mean * 100
        psi = population_stability_index(baseline[field], current[field])
        rows.append(
            {
                "feature": field,
                "feature_type": "numeric",
                "baseline_mean": round(float(baseline_mean), 4),
                "current_mean": round(float(current_mean), 4),
                "pct_change": round(float(pct_change), 4) if not np.isnan(pct_change) else np.nan,
                "drift_metric": round(psi, 6),
                "drift_metric_name": "psi",
                "status": drift_status(psi),
            }
        )
    return pd.DataFrame(rows)


def categorical_drift(baseline: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for field in MONITORED_CATEGORICAL_FEATURES:
        if field not in baseline.columns or field not in current.columns:
            continue
        baseline_dist = baseline[field].astype(str).value_counts(normalize=True)
        current_dist = current[field].astype(str).value_counts(normalize=True)
        values = sorted(set(baseline_dist.index) | set(current_dist.index))
        max_abs_diff = max(abs(current_dist.get(value, 0) - baseline_dist.get(value, 0)) for value in values)
        rows.append(
            {
                "feature": field,
                "feature_type": "categorical",
                "baseline_mean": np.nan,
                "current_mean": np.nan,
                "pct_change": np.nan,
                "drift_metric": round(float(max_abs_diff), 6),
                "drift_metric_name": "max_category_share_diff",
                "status": "high_drift"
                if max_abs_diff >= 0.15
                else "moderate_drift"
                if max_abs_diff >= 0.05
                else "stable",
            }
        )
    return pd.DataFrame(rows)


def prediction_log_summary(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not path.exists():
        empty_summary = pd.DataFrame(
            [
                {
                    "model_name": "none",
                    "prediction": "none",
                    "count": 0,
                    "share": 0.0,
                }
            ]
        )
        empty_audit = pd.DataFrame(
            [
                {
                    "records": 0,
                    "unique_model_versions": 0,
                    "unique_input_hashes": 0,
                    "first_timestamp_utc": "",
                    "last_timestamp_utc": "",
                }
            ]
        )
        return empty_summary, empty_audit

    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not rows:
        return prediction_log_summary(Path("__missing__"))
    logs = pd.DataFrame(rows)
    summary = (
        logs.groupby(["model_name", "prediction"])
        .size()
        .rename("count")
        .reset_index()
    )
    summary["share"] = summary["count"] / summary.groupby("model_name")["count"].transform("sum")
    summary["share"] = summary["share"].round(4)
    audit = pd.DataFrame(
        [
            {
                "records": int(len(logs)),
                "unique_model_versions": int(logs["model_version"].nunique()),
                "unique_input_hashes": int(logs["input_feature_hash"].nunique()),
                "first_timestamp_utc": str(logs["timestamp_utc"].min()),
                "last_timestamp_utc": str(logs["timestamp_utc"].max()),
            }
        ]
    )
    return summary, audit


def write_markdown_reports(
    validation: pd.DataFrame,
    drift: pd.DataFrame,
    prediction_summary: pd.DataFrame,
    audit_summary: pd.DataFrame,
    current_path: Path,
) -> None:
    failed_checks = int((validation["status"] == "fail").sum())
    review_checks = int((validation["status"] == "review").sum())
    high_drift = int((drift["status"] == "high_drift").sum())
    moderate_drift = int((drift["status"] == "moderate_drift").sum())

    drift_report = f"""# Phase 6 Drift Detection Report

Generated at: {datetime.now(UTC).isoformat()}

Current data source: `{current_path.relative_to(ROOT) if current_path.is_relative_to(ROOT) else current_path}`

## Validation Summary

- Failed checks: {failed_checks}
- Review checks: {review_checks}
- Total validation checks: {len(validation)}

## Drift Summary

- High drift features: {high_drift}
- Moderate drift features: {moderate_drift}
- Total monitored features: {len(drift)}

## Data Validation Details

{validation.to_markdown(index=False)}

## Feature Drift Details

{drift.to_markdown(index=False)}

## Prediction Drift and Audit Summary

Prediction mix:

{prediction_summary.to_markdown(index=False)}

Audit log summary:

{audit_summary.to_markdown(index=False)}

## Interpretation

The first monitoring run uses the current modeling table as both baseline and current batch, so feature drift should be stable. In production, pass a new scored batch to `--current-data` and compare it against the Phase 2 baseline.
"""

    governance = """# Phase 6 Governance and Compliance Document

## Intended Use

The monitoring layer supports hospital operations and finance governance by checking data quality, feature drift, prediction drift, and prediction audit traceability.

## System Assumptions

- `data_outputs/model_table.csv` is the baseline training/reference dataset.
- Incoming production batches follow the same feature schema.
- Predictions are generated through the Phase 5 FastAPI service.
- Prediction logs are written to `logs/predictions.jsonl`.

## Controls Implemented

- Missing-value checks for critical operational and billing fields.
- Numeric range checks for age, utilization, billing, calendar, and ratio fields.
- Unseen-category checks for department, visit type, city, payer, risk score, and claim status.
- Numeric feature drift using population stability index.
- Categorical drift using maximum category share difference.
- Prediction audit summaries by model version, prediction class, timestamp, and input feature hash.

## Limitations

- PSI and category-share drift are monitoring indicators, not causal explanations.
- Drift thresholds should be tuned with real production history.
- Logs store input hashes rather than raw features to reduce sensitive-data exposure.
- Current models remain decision-support tools and require human review.

## Retraining Strategy

- Review monitoring reports monthly.
- Trigger retraining if any feature has high drift, if multiple features show moderate drift, or if business-critical recall degrades in Phase 4 evaluation.
- Retrain after major payer contract changes, department workflow changes, or data collection process changes.
- Rerun Phase 4 evaluation and update the model card before promoting new model artifacts.

## Compliance Notes

- Preserve `logs/predictions.jsonl` according to internal audit retention policy.
- Restrict API and log access to authorized hospital analytics, operations, and finance users.
- Use model outputs for triage and prioritization, not autonomous clinical or claim decisions.
"""

    (REPORT_DIR / "drift_detection_report.md").write_text(drift_report)
    (REPORT_DIR / "governance_compliance.md").write_text(governance)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 6 monitoring checks.")
    parser.add_argument(
        "--current-data",
        type=Path,
        default=BASELINE_PATH,
        help="Current batch to validate and compare with the baseline.",
    )
    parser.add_argument(
        "--prediction-log",
        type=Path,
        default=PREDICTION_LOG_PATH,
        help="Prediction audit log JSONL path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    baseline = read_data(BASELINE_PATH)
    current = read_data(args.current_data)
    read_schema()

    validation = pd.concat(
        [
            missing_value_checks(current),
            numeric_range_checks(current),
            unseen_category_checks(baseline, current),
        ],
        ignore_index=True,
    )
    drift = pd.concat(
        [
            numeric_drift(baseline, current),
            categorical_drift(baseline, current),
        ],
        ignore_index=True,
    )
    prediction_summary, audit_summary = prediction_log_summary(args.prediction_log)

    validation.to_csv(REPORT_DIR / "data_validation_report.csv", index=False)
    drift.to_csv(REPORT_DIR / "feature_drift_report.csv", index=False)
    prediction_summary.to_csv(REPORT_DIR / "prediction_drift_report.csv", index=False)
    audit_summary.to_csv(REPORT_DIR / "audit_log_summary.csv", index=False)
    write_markdown_reports(validation, drift, prediction_summary, audit_summary, args.current_data)

    print(
        {
            "validation_checks": len(validation),
            "failed_checks": int((validation["status"] == "fail").sum()),
            "review_checks": int((validation["status"] == "review").sum()),
            "high_drift_features": int((drift["status"] == "high_drift").sum()),
            "moderate_drift_features": int((drift["status"] == "moderate_drift").sum()),
            "prediction_log_records": int(audit_summary["records"].iloc[0]),
            "report_dir": str(REPORT_DIR),
        }
    )


if __name__ == "__main__":
    main()
