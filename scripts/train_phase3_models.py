#!/usr/bin/env python3
"""Train Phase 3 visit-risk and claim-outcome classifiers."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
MODEL_TABLE_PATH = ROOT / "data_outputs" / "model_table.csv"
ARTIFACT_DIR = ROOT / "model_artifacts"

RISK_TARGET = "risk_score"
CLAIM_TARGET = "claim_status"

RISK_FEATURES = [
    "age",
    "gender",
    "city",
    "insurance_provider",
    "chronic_flag",
    "department",
    "visit_type",
    "doctor_id",
    "length_of_stay_hours_filled",
    "visit_frequency",
    "days_since_registration",
    "visit_month",
    "visit_day_of_week",
    "visit_quarter",
]

CLAIM_FEATURES = [
    "age",
    "gender",
    "city",
    "insurance_provider",
    "chronic_flag",
    "department",
    "visit_type",
    "risk_score",
    "doctor_id",
    "billed_amount",
    "length_of_stay_hours_filled",
    "visit_frequency",
    "days_since_registration",
    "visit_month",
    "visit_day_of_week",
    "visit_quarter",
    "billing_month",
    "billing_lag_days",
]

CATEGORICAL_FEATURES = {
    "risk": ["gender", "city", "insurance_provider", "department", "visit_type"],
    "claim": ["gender", "city", "insurance_provider", "department", "visit_type", "risk_score"],
}


def load_model_table() -> pd.DataFrame:
    if not MODEL_TABLE_PATH.exists():
        raise FileNotFoundError(
            f"{MODEL_TABLE_PATH} is missing. Run `python3 scripts/build_features.py` first."
        )
    return pd.read_csv(MODEL_TABLE_PATH, parse_dates=["visit_date", "billing_date", "registration_date"])


def time_split(df: pd.DataFrame, date_col: str = "visit_date", train_size: float = 0.8):
    ordered = df.sort_values(date_col).reset_index(drop=True)
    split_idx = int(len(ordered) * train_size)
    return ordered.iloc[:split_idx].copy(), ordered.iloc[split_idx:].copy()


def build_preprocessor(features: list[str], categorical_features: list[str]) -> ColumnTransformer:
    numeric_features = [feature for feature in features if feature not in categorical_features]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ]
    )


def build_models(features: list[str], categorical_features: list[str], random_state: int) -> dict[str, Pipeline]:
    preprocessor = build_preprocessor(features, categorical_features)
    return {
        "logistic_regression": Pipeline(
            steps=[
                ("preprocess", preprocessor),
                (
                    "model",
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                        random_state=random_state,
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("preprocess", preprocessor),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=250,
                        max_depth=12,
                        min_samples_leaf=8,
                        class_weight="balanced_subsample",
                        random_state=random_state,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }


def evaluate_model(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    predictions = model.predict(X_test)
    labels = sorted(y_test.dropna().unique().tolist())
    return {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "macro_f1": round(float(f1_score(y_test, predictions, average="macro")), 4),
        "weighted_f1": round(float(f1_score(y_test, predictions, average="weighted")), 4),
        "classification_report": classification_report(y_test, predictions, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=labels).tolist(),
        "labels": labels,
    }


def train_problem(
    df: pd.DataFrame,
    problem_name: str,
    target: str,
    features: list[str],
    categorical_features: list[str],
    random_state: int = 42,
) -> dict:
    train_df, test_df = time_split(df)
    X_train = train_df[features]
    y_train = train_df[target]
    X_test = test_df[features]
    y_test = test_df[target]

    models = build_models(features, categorical_features, random_state)
    results = {}
    for model_name, model in models.items():
        model.fit(X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test)
        artifact_path = ARTIFACT_DIR / f"{problem_name}_{model_name}.joblib"
        joblib.dump(model, artifact_path)
        results[model_name] = {
            "artifact": str(artifact_path.relative_to(ROOT)),
            "metrics": metrics,
        }

    best_model_name = max(results, key=lambda name: results[name]["metrics"]["macro_f1"])
    best_path = ARTIFACT_DIR / f"{problem_name}_best_model.joblib"
    joblib.dump(models[best_model_name], best_path)

    return {
        "problem": problem_name,
        "target": target,
        "features": features,
        "categorical_features": categorical_features,
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "train_date_min": str(train_df["visit_date"].min().date()),
        "train_date_max": str(train_df["visit_date"].max().date()),
        "test_date_min": str(test_df["visit_date"].min().date()),
        "test_date_max": str(test_df["visit_date"].max().date()),
        "class_distribution_train": y_train.value_counts(normalize=True).round(4).to_dict(),
        "class_distribution_test": y_test.value_counts(normalize=True).round(4).to_dict(),
        "models": results,
        "best_model": best_model_name,
        "best_artifact": str(best_path.relative_to(ROOT)),
    }


def write_feature_schema(results: dict[str, dict]) -> None:
    schema = {
        "phase": "Phase 3 Modeling",
        "source_dataset": "data_outputs/model_table.csv",
        "split_strategy": "time-based split by visit_date: earliest 80% train, latest 20% test",
        "leakage_policy": {
            "risk_model": "Excludes claim_status, approval, payment delay, approval ratio, and claim-derived fields.",
            "claim_model": "Excludes approved_amount, payment_days, approval_ratio, provider_rejection_rate, and target-derived outcome fields.",
        },
        "models": {
            key: {
                "target": value["target"],
                "features": value["features"],
                "categorical_features": value["categorical_features"],
                "best_model": value["best_model"],
                "best_artifact": value["best_artifact"],
            }
            for key, value in results.items()
        },
    }
    (ARTIFACT_DIR / "feature_schema.json").write_text(json.dumps(schema, indent=2))


def flatten_metrics(results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for problem_name, problem_result in results.items():
        for model_name, model_result in problem_result["models"].items():
            metrics = model_result["metrics"]
            rows.append(
                {
                    "problem": problem_name,
                    "model": model_name,
                    "accuracy": metrics["accuracy"],
                    "macro_f1": metrics["macro_f1"],
                    "weighted_f1": metrics["weighted_f1"],
                    "artifact": model_result["artifact"],
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    ARTIFACT_DIR.mkdir(exist_ok=True)
    df = load_model_table()

    results = {
        "risk_model": train_problem(
            df=df,
            problem_name="risk",
            target=RISK_TARGET,
            features=RISK_FEATURES,
            categorical_features=CATEGORICAL_FEATURES["risk"],
        ),
        "claim_model": train_problem(
            df=df,
            problem_name="claim",
            target=CLAIM_TARGET,
            features=CLAIM_FEATURES,
            categorical_features=CATEGORICAL_FEATURES["claim"],
        ),
    }

    write_feature_schema(results)
    (ARTIFACT_DIR / "metrics.json").write_text(json.dumps(results, indent=2))
    flatten_metrics(results).to_csv(ARTIFACT_DIR / "metrics_summary.csv", index=False)

    print(flatten_metrics(results).to_string(index=False))
    print(f"wrote artifacts to: {ARTIFACT_DIR}")


if __name__ == "__main__":
    main()
