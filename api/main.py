#!/usr/bin/env python3
"""FastAPI service for hospital analytics model scoring."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[1]
MODEL_TABLE_PATH = ROOT / "data_outputs" / "model_table.csv"
DATA_SCHEMA_PATH = ROOT / "data_outputs" / "feature_schema.json"
MODEL_SCHEMA_PATH = ROOT / "model_artifacts" / "feature_schema.json"
RISK_MODEL_PATH = ROOT / "model_artifacts" / "risk_best_model.joblib"
CLAIM_MODEL_PATH = ROOT / "model_artifacts" / "claim_best_model.joblib"
LOG_DIR = ROOT / "logs"
PREDICTION_LOG_PATH = LOG_DIR / "predictions.jsonl"

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

Gender = Literal["F", "M"]
RiskScore = Literal["High", "Low", "Medium"]

app = FastAPI(
    title="Hospital Analytics Prediction API",
    version="1.0.0",
    description="Phase 5 FastAPI service for real-time visit-risk and claim-outcome predictions.",
)


class VisitRiskRequest(BaseModel):
    age: int = Field(ge=0, le=120)
    gender: Gender
    city: str = Field(min_length=1)
    insurance_provider: str = Field(min_length=1)
    chronic_flag: int = Field(ge=0, le=1)
    department: str = Field(min_length=1)
    visit_type: str = Field(min_length=1)
    doctor_id: int = Field(ge=1)
    length_of_stay_hours_filled: float = Field(ge=0)
    visit_frequency: int = Field(ge=1)
    days_since_registration: int = Field(ge=0)
    visit_month: int = Field(ge=1, le=12)
    visit_day_of_week: int = Field(ge=0, le=6)
    visit_quarter: int = Field(ge=1, le=4)


class ClaimOutcomeRequest(BaseModel):
    age: int = Field(ge=0, le=120)
    gender: Gender
    city: str = Field(min_length=1)
    insurance_provider: str = Field(min_length=1)
    chronic_flag: int = Field(ge=0, le=1)
    department: str = Field(min_length=1)
    visit_type: str = Field(min_length=1)
    risk_score: RiskScore
    doctor_id: int = Field(ge=1)
    billed_amount: float = Field(ge=0)
    length_of_stay_hours_filled: float = Field(ge=0)
    visit_frequency: int = Field(ge=1)
    days_since_registration: int = Field(ge=0)
    visit_month: int = Field(ge=1, le=12)
    visit_day_of_week: int = Field(ge=0, le=6)
    visit_quarter: int = Field(ge=1, le=4)
    billing_month: int = Field(ge=1, le=12)
    billing_lag_days: int


class PredictionResponse(BaseModel):
    prediction: str
    probabilities: dict[str, float]
    model_name: str
    model_version: str
    timestamp_utc: str
    input_feature_hash: str
    audit_log_id: str


class HeuristicRiskRequest(BaseModel):
    department: str
    visit_type: str
    insurance_provider: str
    billed_amount: float = Field(ge=0)
    approved_amount: float | None = Field(default=None, ge=0)
    payment_days: float | None = Field(default=None, ge=0)
    length_of_stay_hours: float = Field(ge=0)
    provider_rejection_rate: float | None = Field(default=None, ge=0, le=1)
    visit_frequency: int = Field(default=1, ge=1)
    chronic_flag: int = Field(default=0, ge=0, le=1)


class HeuristicRiskResponse(BaseModel):
    risk_score: float
    risk_level: str
    signals: list[str]


def load_model_table() -> pd.DataFrame:
    if not MODEL_TABLE_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="model_table.csv is missing. Run `python3 scripts/build_features.py` first.",
        )
    return pd.read_csv(MODEL_TABLE_PATH)


def load_json(path: Path, missing_message: str) -> dict[str, Any]:
    if not path.exists():
        raise HTTPException(status_code=503, detail=missing_message)
    return json.loads(path.read_text())


@lru_cache(maxsize=1)
def load_risk_model():
    if not RISK_MODEL_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="risk_best_model.joblib is missing. Run `python3 scripts/train_phase3_models.py` first.",
        )
    return joblib.load(RISK_MODEL_PATH)


@lru_cache(maxsize=1)
def load_claim_model():
    if not CLAIM_MODEL_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="claim_best_model.joblib is missing. Run `python3 scripts/train_phase3_models.py` first.",
        )
    return joblib.load(CLAIM_MODEL_PATH)


def artifact_version(path: Path) -> str:
    if not path.exists():
        return "missing"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    modified = datetime.fromtimestamp(path.stat().st_mtime, UTC).strftime("%Y%m%d%H%M%S")
    return f"{path.stem}:{modified}:{digest}"


def canonical_payload(payload: BaseModel, features: list[str]) -> dict[str, Any]:
    raw = payload.model_dump()
    return {feature: raw[feature] for feature in features}


def feature_hash(features: dict[str, Any]) -> str:
    encoded = json.dumps(features, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def predict_with_model(
    *,
    model,
    payload: BaseModel,
    features: list[str],
    model_name: str,
    model_path: Path,
) -> PredictionResponse:
    feature_payload = canonical_payload(payload, features)
    X = pd.DataFrame([feature_payload], columns=features)
    prediction = str(model.predict(X)[0])
    probabilities = {
        str(label): round(float(probability), 6)
        for label, probability in zip(model.classes_, model.predict_proba(X)[0], strict=True)
    }
    timestamp = datetime.now(UTC).isoformat()
    input_hash = feature_hash(feature_payload)
    audit_log_id = str(uuid4())
    model_version = artifact_version(model_path)

    response = PredictionResponse(
        prediction=prediction,
        probabilities=probabilities,
        model_name=model_name,
        model_version=model_version,
        timestamp_utc=timestamp,
        input_feature_hash=input_hash,
        audit_log_id=audit_log_id,
    )
    write_prediction_log(
        {
            "audit_log_id": audit_log_id,
            "timestamp_utc": timestamp,
            "model_name": model_name,
            "model_version": model_version,
            "input_feature_hash": input_hash,
            "prediction": prediction,
            "probabilities": probabilities,
        }
    )
    return response


def write_prediction_log(record: dict[str, Any]) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    with PREDICTION_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def amount_percentile(df: pd.DataFrame, value: float, column: str) -> float:
    return float((df[column] <= value).mean())


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "api_version": app.version,
        "model_table_available": MODEL_TABLE_PATH.exists(),
        "data_schema_available": DATA_SCHEMA_PATH.exists(),
        "model_schema_available": MODEL_SCHEMA_PATH.exists(),
        "risk_model_available": RISK_MODEL_PATH.exists(),
        "claim_model_available": CLAIM_MODEL_PATH.exists(),
        "prediction_log_path": str(PREDICTION_LOG_PATH.relative_to(ROOT)),
    }


@app.get("/schema")
def schema() -> dict[str, Any]:
    return {
        "data_schema": load_json(
            DATA_SCHEMA_PATH,
            "data_outputs/feature_schema.json is missing. Run `python3 scripts/build_features.py` first.",
        ),
        "model_schema": load_json(
            MODEL_SCHEMA_PATH,
            "model_artifacts/feature_schema.json is missing. Run `python3 scripts/train_phase3_models.py` first.",
        ),
    }


@app.get("/summary")
def summary() -> dict[str, Any]:
    df = load_model_table()
    return {
        "rows": int(len(df)),
        "departments": sorted(df["department"].dropna().unique().tolist()),
        "visit_types": sorted(df["visit_type"].dropna().unique().tolist()),
        "insurance_providers": sorted(df["insurance_provider"].dropna().unique().tolist()),
        "avg_billed_amount": round(float(df["billed_amount"].mean()), 2),
        "avg_payment_days": round(float(df["payment_days_filled"].mean()), 2),
        "avg_length_of_stay_hours": round(float(df["length_of_stay_hours_filled"].mean()), 2),
    }


@app.post("/predict/risk", response_model=PredictionResponse)
def predict_risk(payload: VisitRiskRequest) -> PredictionResponse:
    return predict_with_model(
        model=load_risk_model(),
        payload=payload,
        features=RISK_FEATURES,
        model_name="visit_risk_classifier",
        model_path=RISK_MODEL_PATH,
    )


@app.post("/predict/claim", response_model=PredictionResponse)
def predict_claim(payload: ClaimOutcomeRequest) -> PredictionResponse:
    return predict_with_model(
        model=load_claim_model(),
        payload=payload,
        features=CLAIM_FEATURES,
        model_name="claim_outcome_classifier",
        model_path=CLAIM_MODEL_PATH,
    )


@app.post("/score/visit", response_model=HeuristicRiskResponse)
def score_visit(payload: HeuristicRiskRequest) -> HeuristicRiskResponse:
    """Legacy transparent heuristic endpoint retained for Phase 2 compatibility."""
    df = load_model_table()

    rejection_rate = payload.provider_rejection_rate
    if rejection_rate is None:
        provider_rows = df[df["insurance_provider"] == payload.insurance_provider]
        rejection_rate = (
            float(provider_rows["provider_rejection_rate"].mean())
            if not provider_rows.empty
            else float(df["provider_rejection_rate"].mean())
        )

    approval_ratio = None
    if payload.approved_amount is not None and payload.billed_amount > 0:
        approval_ratio = payload.approved_amount / payload.billed_amount

    score = 0.0
    signals: list[str] = []

    if amount_percentile(df, payload.billed_amount, "billed_amount") >= 0.95:
        score += 25
        signals.append("billed_amount_top_5_percent")

    if payload.payment_days is None:
        score += 15
        signals.append("payment_days_missing")
    elif amount_percentile(df, payload.payment_days, "payment_days_filled") >= 0.90:
        score += 20
        signals.append("payment_delay_top_10_percent")

    if amount_percentile(df, payload.length_of_stay_hours, "length_of_stay_hours_filled") >= 0.90:
        score += 20
        signals.append("length_of_stay_top_10_percent")

    if rejection_rate >= 0.155:
        score += 15
        signals.append("provider_high_rejection_rate")

    if approval_ratio is None:
        score += 10
        signals.append("approved_amount_missing")
    elif approval_ratio < 0.5:
        score += 15
        signals.append("low_approval_ratio")

    if payload.visit_frequency >= 8:
        score += 10
        signals.append("frequent_patient_visits")

    if payload.chronic_flag == 1:
        score += 5
        signals.append("chronic_patient")

    score = min(round(score, 2), 100.0)
    if score >= 60:
        risk_level = "high"
    elif score >= 30:
        risk_level = "medium"
    else:
        risk_level = "low"

    return HeuristicRiskResponse(risk_score=score, risk_level=risk_level, signals=signals)
