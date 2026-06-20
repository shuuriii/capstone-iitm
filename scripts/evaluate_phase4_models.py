#!/usr/bin/env python3
"""Evaluate Phase 3 models for Phase 4 governance and safety checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.train_phase3_models import (
    CLAIM_FEATURES,
    CLAIM_TARGET,
    RISK_FEATURES,
    RISK_TARGET,
    time_split,
)


MODEL_TABLE_PATH = ROOT / "data_outputs" / "model_table.csv"
ARTIFACT_DIR = ROOT / "model_artifacts"
REPORT_DIR = ROOT / "docs" / "phase4"
FIGURE_DIR = ROOT / "reports" / "figures"


MODEL_CONFIG = {
    "risk_model": {
        "target": RISK_TARGET,
        "features": RISK_FEATURES,
        "artifact": ARTIFACT_DIR / "risk_best_model.joblib",
        "critical_class": "High",
        "business_metric_name": "high_risk_recall",
        "report_path": REPORT_DIR / "risk_model_evaluation_report.md",
    },
    "claim_model": {
        "target": CLAIM_TARGET,
        "features": CLAIM_FEATURES,
        "artifact": ARTIFACT_DIR / "claim_best_model.joblib",
        "critical_class": "Rejected",
        "business_metric_name": "rejected_claim_recall",
        "report_path": REPORT_DIR / "claim_model_evaluation_report.md",
    },
}


def load_data() -> pd.DataFrame:
    if not MODEL_TABLE_PATH.exists():
        raise FileNotFoundError("Run `python3 scripts/build_features.py` before Phase 4 evaluation.")
    return pd.read_csv(MODEL_TABLE_PATH, parse_dates=["visit_date", "billing_date", "registration_date"])


def evaluate_split(model, df: pd.DataFrame, features: list[str], target: str) -> dict:
    y_true = df[target]
    y_pred = model.predict(df[features])
    labels = sorted(y_true.dropna().unique().tolist())
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
    )
    per_class = pd.DataFrame(
        {
            "class": labels,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }
    )
    return {
        "labels": labels,
        "predictions": y_pred,
        "classification_report": report,
        "per_class": per_class,
        "confusion_matrix": pd.DataFrame(
            confusion_matrix(y_true, y_pred, labels=labels),
            index=[f"actual_{label}" for label in labels],
            columns=[f"predicted_{label}" for label in labels],
        ),
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "weighted_f1": float(report["weighted avg"]["f1-score"]),
        "accuracy": float(report["accuracy"]),
    }


def critical_recall(per_class: pd.DataFrame, critical_class: str) -> float:
    row = per_class.loc[per_class["class"] == critical_class]
    if row.empty:
        return float("nan")
    return float(row["recall"].iloc[0])


def segment_performance(
    df: pd.DataFrame,
    y_pred: np.ndarray,
    target: str,
    segment_cols: list[str],
    critical_class: str,
) -> pd.DataFrame:
    scored = df[[target, *segment_cols]].copy()
    scored["prediction"] = y_pred
    rows = []
    for segment_col in segment_cols:
        for segment_value, segment_df in scored.groupby(segment_col, dropna=False):
            y_true = segment_df[target]
            pred = segment_df["prediction"]
            labels = sorted(y_true.dropna().unique().tolist())
            report = classification_report(y_true, pred, output_dict=True, zero_division=0)
            support = int(len(segment_df))
            critical_mask = y_true == critical_class
            critical_support = int(critical_mask.sum())
            critical_hits = int(((pred == critical_class) & critical_mask).sum())
            critical_class_recall = (
                critical_hits / critical_support if critical_support else np.nan
            )
            rows.append(
                {
                    "segment": segment_col,
                    "value": segment_value,
                    "rows": support,
                    "accuracy": round(float(report["accuracy"]), 4),
                    "macro_f1": round(float(report["macro avg"]["f1-score"]), 4),
                    "critical_class": critical_class,
                    "critical_class_support": critical_support,
                    "critical_class_recall": round(float(critical_class_recall), 4)
                    if not np.isnan(critical_class_recall)
                    else np.nan,
                }
            )
    return pd.DataFrame(rows).sort_values(["segment", "critical_class_recall", "macro_f1"])


def fairness_gap(segment_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for segment, group in segment_df.groupby("segment"):
        valid = group.dropna(subset=["critical_class_recall"])
        if valid.empty:
            continue
        rows.append(
            {
                "segment": segment,
                "min_critical_recall": round(float(valid["critical_class_recall"].min()), 4),
                "max_critical_recall": round(float(valid["critical_class_recall"].max()), 4),
                "critical_recall_gap": round(
                    float(valid["critical_class_recall"].max() - valid["critical_class_recall"].min()),
                    4,
                ),
                "lowest_recall_group": str(
                    valid.sort_values("critical_class_recall").iloc[0]["value"]
                ),
            }
        )
    return pd.DataFrame(rows)


def get_feature_importance(model, features: list[str], top_n: int = 20) -> pd.DataFrame:
    preprocessor = model.named_steps["preprocess"]
    estimator = model.named_steps["model"]
    feature_names = preprocessor.get_feature_names_out()
    if hasattr(estimator, "feature_importances_"):
        values = estimator.feature_importances_
    elif hasattr(estimator, "coef_"):
        values = np.abs(estimator.coef_).mean(axis=0)
    else:
        values = np.zeros(len(feature_names))
    importance = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": values,
        }
    ).sort_values("importance", ascending=False)
    importance["source_feature"] = importance["feature"].str.replace(
        r"^(numeric|categorical)__", "", regex=True
    )
    return importance.head(top_n)


def write_markdown_report(
    problem_name: str,
    config: dict,
    train_eval: dict,
    test_eval: dict,
    segment_metrics: pd.DataFrame,
    gaps: pd.DataFrame,
    importance: pd.DataFrame,
) -> None:
    business_metric = config["business_metric_name"]
    critical_class = config["critical_class"]
    train_critical_recall = critical_recall(train_eval["per_class"], critical_class)
    test_critical_recall = critical_recall(test_eval["per_class"], critical_class)

    text = f"""# {problem_name.replace('_', ' ').title()} Evaluation Report

## Scope

This report evaluates the saved Phase 3 best model artifact `{config['artifact'].relative_to(ROOT)}` using the same time-based split used during training.

## Core Metrics

| split | accuracy | macro_f1 | weighted_f1 | {business_metric} |
| --- | ---: | ---: | ---: | ---: |
| train | {train_eval['accuracy']:.4f} | {train_eval['macro_f1']:.4f} | {train_eval['weighted_f1']:.4f} | {train_critical_recall:.4f} |
| test | {test_eval['accuracy']:.4f} | {test_eval['macro_f1']:.4f} | {test_eval['weighted_f1']:.4f} | {test_critical_recall:.4f} |

## Test Set Per-Class Metrics

{test_eval['per_class'].round(4).to_markdown(index=False)}

## Test Set Confusion Matrix

{test_eval['confusion_matrix'].to_markdown()}

## Fairness and Segment Review

Segment performance is computed by `gender`, `city`, and `insurance_provider`. The critical safety metric is recall for `{critical_class}`.

{gaps.to_markdown(index=False)}

Lowest-performing segment rows by critical-class recall:

{segment_metrics.head(10).to_markdown(index=False)}

## Explainability Summary

Top model drivers:

{importance.round(6).to_markdown(index=False)}

## Governance Notes

- This model is suitable for decision support and prioritization, not autonomous clinical or financial action.
- Segment-level recall gaps should be reviewed before production deployment.
- Thresholding, calibration, richer history features, and imbalance strategies such as class-weight tuning, undersampling, or SMOTE should be evaluated in the next iteration.
"""
    config["report_path"].write_text(text)


def write_model_card(all_results: dict) -> None:
    lines = [
        "# Consolidated Model Card",
        "",
        "## Intended Use",
        "",
        "The Phase 4 models are intended for hospital decision support: visit-risk triage and claim-outcome prioritization. They should support human review rather than replace clinical or finance judgment.",
        "",
        "## Data and Split",
        "",
        "- Source: `data_outputs/model_table.csv`",
        "- Split: earliest 80% of visits for training, latest 20% for testing by `visit_date`.",
        "- Protected or sensitive review segments: `gender`, `city`, and `insurance_provider`.",
        "",
        "## Performance Summary",
        "",
        "| model | test_accuracy | test_macro_f1 | critical_class | critical_class_recall |",
        "| --- | ---: | ---: | --- | ---: |",
    ]
    for problem_name, result in all_results.items():
        critical_class = result["critical_class"]
        recall = critical_recall(result["test_eval"]["per_class"], critical_class)
        lines.append(
            f"| {problem_name} | {result['test_eval']['accuracy']:.4f} | "
            f"{result['test_eval']['macro_f1']:.4f} | {critical_class} | {recall:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Key Limitations",
            "",
            "- Current features are structured operational and billing fields; diagnosis, procedure, prior-authorization, and longitudinal payer-history features are not yet available.",
            "- Models show modest macro F1, so outputs should be treated as triage signals.",
            "- Segment recall gaps require governance review before external or high-stakes use.",
            "",
            "## Recommended Controls",
            "",
            "- Monitor recall for High Risk visits and Rejected claims monthly.",
            "- Review performance by gender, city, and insurance provider after every retraining.",
            "- Use human-in-the-loop workflows for any action affecting clinical care or claim handling.",
            "- Explore class-weight tuning, tree-depth tuning, interaction features, and resampling strategies for imbalance mitigation.",
        ]
    )
    (REPORT_DIR / "model_card.md").write_text("\n".join(lines))


def write_explainability_summary(all_results: dict) -> None:
    sections = ["# Explainability Summary", ""]
    for problem_name, result in all_results.items():
        sections.extend(
            [
                f"## {problem_name.replace('_', ' ').title()}",
                "",
                "Top feature importances:",
                "",
                result["importance"].round(6).to_markdown(index=False),
                "",
                "Interpretation:",
                "",
                "- Higher importance means the model relied more on that transformed feature for splits.",
                "- One-hot encoded categorical values appear as specific category indicators.",
                "- Importance does not prove causality; it indicates predictive contribution in this trained model.",
                "",
            ]
        )
    (REPORT_DIR / "explainability_summary.md").write_text("\n".join(sections))


def write_metrics_json(all_results: dict) -> None:
    serializable = {}
    for problem_name, result in all_results.items():
        serializable[problem_name] = {
            "critical_class": result["critical_class"],
            "train": {
                "accuracy": round(result["train_eval"]["accuracy"], 4),
                "macro_f1": round(result["train_eval"]["macro_f1"], 4),
                "weighted_f1": round(result["train_eval"]["weighted_f1"], 4),
                "critical_class_recall": round(
                    critical_recall(result["train_eval"]["per_class"], result["critical_class"]),
                    4,
                ),
            },
            "test": {
                "accuracy": round(result["test_eval"]["accuracy"], 4),
                "macro_f1": round(result["test_eval"]["macro_f1"], 4),
                "weighted_f1": round(result["test_eval"]["weighted_f1"], 4),
                "critical_class_recall": round(
                    critical_recall(result["test_eval"]["per_class"], result["critical_class"]),
                    4,
                ),
            },
            "fairness_gaps": result["gaps"].to_dict(orient="records"),
        }
    (REPORT_DIR / "phase4_metrics.json").write_text(json.dumps(serializable, indent=2))


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    train_df, test_df = time_split(df)

    all_results = {}
    segment_cols = ["gender", "city", "insurance_provider"]
    for problem_name, config in MODEL_CONFIG.items():
        model = joblib.load(config["artifact"])
        target = config["target"]
        features = config["features"]
        critical_class = config["critical_class"]

        train_eval = evaluate_split(model, train_df, features, target)
        test_eval = evaluate_split(model, test_df, features, target)
        segment_metrics = segment_performance(
            test_df,
            test_eval["predictions"],
            target,
            segment_cols,
            critical_class,
        )
        gaps = fairness_gap(segment_metrics)
        importance = get_feature_importance(model, features)

        all_results[problem_name] = {
            "critical_class": critical_class,
            "train_eval": train_eval,
            "test_eval": test_eval,
            "segment_metrics": segment_metrics,
            "gaps": gaps,
            "importance": importance,
        }

        segment_metrics.to_csv(REPORT_DIR / f"{problem_name}_segment_metrics.csv", index=False)
        importance.to_csv(REPORT_DIR / f"{problem_name}_feature_importance.csv", index=False)
        write_markdown_report(
            problem_name,
            config,
            train_eval,
            test_eval,
            segment_metrics,
            gaps,
            importance,
        )

    write_model_card(all_results)
    write_explainability_summary(all_results)
    write_metrics_json(all_results)

    summary_rows = []
    for problem_name, result in all_results.items():
        summary_rows.append(
            {
                "model": problem_name,
                "test_accuracy": round(result["test_eval"]["accuracy"], 4),
                "test_macro_f1": round(result["test_eval"]["macro_f1"], 4),
                "critical_class": result["critical_class"],
                "critical_class_recall": round(
                    critical_recall(result["test_eval"]["per_class"], result["critical_class"]),
                    4,
                ),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(REPORT_DIR / "phase4_evaluation_summary.csv", index=False)
    print(summary.to_string(index=False))
    print(f"wrote reports to: {REPORT_DIR}")


if __name__ == "__main__":
    main()
