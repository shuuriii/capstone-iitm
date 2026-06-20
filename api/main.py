#!/usr/bin/env python3
"""FastAPI package for Phase 2 hospital risk scoring."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[1]
MODEL_TABLE_PATH = ROOT / "data_outputs" / "model_table.csv"
SCHEMA_PATH = ROOT / "data_outputs" / "feature_schema.json"

app = FastAPI(
    title="Hospital Analytics API",
    version="0.1.0",
    description="Phase 2 deployment package for hospital operations and billing risk scoring.",
)


class VisitRiskRequest(BaseModel):
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


class VisitRiskResponse(BaseModel):
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


def amount_percentile(df: pd.DataFrame, value: float, column: str) -> float:
    return float((df[column] <= value).mean())


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "model_table_available": MODEL_TABLE_PATH.exists(),
        "schema_available": SCHEMA_PATH.exists(),
    }


@app.get("/schema")
def schema() -> dict[str, Any]:
    if not SCHEMA_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="feature_schema.json is missing. Run `python3 scripts/build_features.py` first.",
        )
    return json.loads(SCHEMA_PATH.read_text())


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


@app.post("/score/visit", response_model=VisitRiskResponse)
def score_visit(payload: VisitRiskRequest) -> VisitRiskResponse:
    df = load_model_table()

    rejection_rate = payload.provider_rejection_rate
    if rejection_rate is None:
        provider_rows = df[df["insurance_provider"] == payload.insurance_provider]
        rejection_rate = (
            float(provider_rows["provider_rejection_rate"].mean())
            if not provider_rows.empty
            else float(df["provider_rejection_rate"].mean())
        )

    approved_amount = payload.approved_amount
    approval_ratio = None
    if approved_amount is not None and payload.billed_amount > 0:
        approval_ratio = approved_amount / payload.billed_amount

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

    return VisitRiskResponse(risk_score=score, risk_level=risk_level, signals=signals)
