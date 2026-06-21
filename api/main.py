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
from fastapi.responses import HTMLResponse
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

DASHBOARD_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hospital Analytics Capstone</title>
  <style>
    :root {
      --ink: #1d2433;
      --muted: #5e6878;
      --line: #d9dee7;
      --panel: #ffffff;
      --bg: #f5f7fb;
      --accent: #0f766e;
      --accent-dark: #0b5f59;
      --warn: #9a3412;
      --blue: #1d4ed8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
      line-height: 1.5;
    }
    header {
      background: #ffffff;
      border-bottom: 1px solid var(--line);
    }
    .wrap {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
    }
    .hero {
      padding: 48px 0 32px;
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.65fr);
      gap: 32px;
      align-items: start;
    }
    h1 {
      margin: 0 0 12px;
      font-size: clamp(2rem, 4vw, 3.7rem);
      line-height: 1.05;
      letter-spacing: 0;
    }
    h2 {
      margin: 0 0 12px;
      font-size: 1.25rem;
      letter-spacing: 0;
    }
    p { margin: 0 0 14px; color: var(--muted); }
    .lead {
      font-size: 1.1rem;
      max-width: 720px;
      color: #3b4557;
    }
    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 22px;
    }
    a.button, button {
      border: 1px solid transparent;
      border-radius: 6px;
      padding: 10px 14px;
      font: inherit;
      font-weight: 650;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 42px;
    }
    .primary, button.primary {
      background: var(--accent);
      color: #ffffff;
    }
    .primary:hover, button.primary:hover { background: var(--accent-dark); }
    .secondary {
      background: #ffffff;
      color: var(--ink);
      border-color: var(--line);
    }
    .summary-box {
      background: #eef7f5;
      border: 1px solid #bee3de;
      border-radius: 8px;
      padding: 18px;
    }
    .summary-box strong {
      display: block;
      font-size: 2rem;
      line-height: 1;
      color: var(--accent-dark);
      margin-bottom: 6px;
    }
    main { padding: 28px 0 48px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }
    .panel p:last-child { margin-bottom: 0; }
    .demo {
      display: grid;
      grid-template-columns: 320px minmax(0, 1fr);
      gap: 16px;
      align-items: stretch;
    }
    .demo-controls {
      display: grid;
      gap: 10px;
      align-content: start;
    }
    .demo-controls button {
      width: 100%;
      color: var(--ink);
      background: #ffffff;
      border-color: var(--line);
    }
    .demo-controls button.active {
      border-color: var(--accent);
      color: var(--accent-dark);
      background: #eef7f5;
    }
    .result {
      min-height: 260px;
      background: #111827;
      color: #f8fafc;
      border-radius: 8px;
      padding: 18px;
      overflow: auto;
      white-space: pre-wrap;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
      font-size: 0.92rem;
    }
    .plain-result {
      font-family: inherit;
      white-space: normal;
      background: #ffffff;
      color: var(--ink);
      border: 1px solid var(--line);
    }
    .metric-list {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-top: 10px;
    }
    .metric {
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfe;
    }
    .metric span {
      display: block;
      color: var(--muted);
      font-size: 0.88rem;
    }
    .metric strong {
      display: block;
      margin-top: 4px;
      font-size: 1.2rem;
    }
    .tag {
      display: inline-flex;
      padding: 4px 8px;
      border-radius: 999px;
      background: #e8efff;
      color: var(--blue);
      font-size: 0.85rem;
      font-weight: 650;
      margin: 0 6px 6px 0;
    }
    footer {
      border-top: 1px solid var(--line);
      padding: 20px 0;
      color: var(--muted);
      background: #ffffff;
      font-size: 0.95rem;
    }
    @media (max-width: 820px) {
      .hero, .demo { grid-template-columns: 1fr; }
      .grid, .metric-list { grid-template-columns: 1fr; }
      h1 { font-size: 2.2rem; }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap hero">
      <section>
        <h1>Hospital Analytics Capstone</h1>
        <p class="lead">
          This project turns hospital visit, patient, and billing data into insights that help explain operational risk,
          insurance claim outcomes, billing delays, and model monitoring.
        </p>
        <p>
          Built with SQL, Python, machine learning, FastAPI, and public IIT-M capstone data.
        </p>
        <div class="actions">
          <a class="button primary" href="#demo">Run Simple Demo</a>
          <a class="button secondary" href="/docs">Technical API Docs</a>
          <a class="button secondary" href="https://github.com/shuuriii/capstone-iitm">GitHub Repo</a>
        </div>
      </section>
      <aside class="summary-box">
        <strong>25,000</strong>
        <p>hospital visits analyzed across departments, patients, billing records, prediction models, and monitoring reports.</p>
      </aside>
    </div>
  </header>

  <main class="wrap">
    <section class="grid" aria-label="Project highlights">
      <div class="panel">
        <h2>Business Question</h2>
        <p>Where are patient risk, claim rejection, missing billing values, and unusual charges most visible?</p>
      </div>
      <div class="panel">
        <h2>What It Builds</h2>
        <p>A reusable workflow from raw CSV files to SQL tables, feature engineering, ML models, API endpoints, and governance reports.</p>
      </div>
      <div class="panel">
        <h2>Why It Matters</h2>
        <p>Hospitals can use this type of workflow to find operational bottlenecks, explain claims behavior, and monitor model reliability.</p>
      </div>
    </section>

    <section id="demo" class="panel">
      <h2>Simple Live Demo</h2>
      <p>Use these buttons to see the deployed model and analytics API return real results from the project data.</p>
      <div class="demo">
        <div class="demo-controls">
          <button type="button" data-demo="summary" class="active">Show Dataset Summary</button>
          <button type="button" data-demo="risk">Predict Visit Risk</button>
          <button type="button" data-demo="claim">Predict Claim Outcome</button>
          <button type="button" data-demo="score">Explain Visit Risk Signals</button>
        </div>
        <div id="result" class="result plain-result">Loading dataset summary...</div>
      </div>
    </section>
  </main>

  <footer>
    <div class="wrap">
      Portfolio project by Shuuri. The technical API documentation remains available at <a href="/docs">/docs</a>.
    </div>
  </footer>

  <script>
    const result = document.getElementById("result");
    const buttons = document.querySelectorAll("[data-demo]");

    const payloads = {
      risk: {
        age: 45,
        gender: "M",
        city: "Chennai",
        insurance_provider: "CareOne",
        chronic_flag: 1,
        department: "Cardiology",
        visit_type: "OPD",
        doctor_id: 10,
        length_of_stay_hours_filled: 12.5,
        visit_frequency: 3,
        days_since_registration: 500,
        visit_month: 6,
        visit_day_of_week: 2,
        visit_quarter: 2
      },
      claim: {
        age: 45,
        gender: "M",
        city: "Chennai",
        insurance_provider: "CareOne",
        chronic_flag: 1,
        department: "Cardiology",
        visit_type: "OPD",
        risk_score: "Medium",
        doctor_id: 10,
        billed_amount: 25000,
        length_of_stay_hours_filled: 12.5,
        visit_frequency: 3,
        days_since_registration: 500,
        visit_month: 6,
        visit_day_of_week: 2,
        visit_quarter: 2,
        billing_month: 6,
        billing_lag_days: 4
      },
      score: {
        department: "Cardiology",
        visit_type: "OPD",
        insurance_provider: "CareOne",
        billed_amount: 25000,
        approved_amount: 18000,
        payment_days: 18,
        length_of_stay_hours: 12.5,
        visit_frequency: 3,
        chronic_flag: 1
      }
    };

    function setActive(name) {
      buttons.forEach((button) => {
        button.classList.toggle("active", button.dataset.demo === name);
      });
    }

    function percent(value) {
      return `${Math.round(value * 100)}%`;
    }

    function showSummary(data) {
      result.className = "result plain-result";
      result.innerHTML = `
        <h2>Dataset Summary</h2>
        <p>This demo is using the modeled hospital dataset created in the project pipeline.</p>
        <div class="metric-list">
          <div class="metric"><span>Visits analyzed</span><strong>${data.rows.toLocaleString()}</strong></div>
          <div class="metric"><span>Average billed amount</span><strong>${data.avg_billed_amount.toLocaleString()}</strong></div>
          <div class="metric"><span>Average payment days</span><strong>${data.avg_payment_days}</strong></div>
        </div>
        <p style="margin-top: 16px;"><strong>Departments:</strong></p>
        <p>${data.departments.map((item) => `<span class="tag">${item}</span>`).join("")}</p>
      `;
    }

    function showPrediction(title, data) {
      const probabilities = Object.entries(data.probabilities)
        .map(([label, value]) => `<span class="tag">${label}: ${percent(value)}</span>`)
        .join("");
      result.className = "result plain-result";
      result.innerHTML = `
        <h2>${title}</h2>
        <p>The model prediction for the sample case is:</p>
        <div class="metric-list">
          <div class="metric"><span>Prediction</span><strong>${data.prediction}</strong></div>
          <div class="metric"><span>Model</span><strong>${data.model_name.replaceAll("_", " ")}</strong></div>
          <div class="metric"><span>Audit log</span><strong>Created</strong></div>
        </div>
        <p style="margin-top: 16px;"><strong>Model confidence by class:</strong></p>
        <p>${probabilities}</p>
      `;
    }

    function showSignals(data) {
      result.className = "result plain-result";
      result.innerHTML = `
        <h2>Rule-Based Visit Risk Signals</h2>
        <p>This transparent score explains which business signals raised or lowered risk for the sample visit.</p>
        <div class="metric-list">
          <div class="metric"><span>Risk level</span><strong>${data.risk_level}</strong></div>
          <div class="metric"><span>Risk score</span><strong>${data.risk_score}</strong></div>
          <div class="metric"><span>Signals found</span><strong>${data.signals.length}</strong></div>
        </div>
        <p style="margin-top: 16px;"><strong>Signals:</strong></p>
        <p>${data.signals.map((item) => `<span class="tag">${item.replaceAll("_", " ")}</span>`).join("") || "No high-risk signals found."}</p>
      `;
    }

    async function runDemo(name) {
      setActive(name);
      result.className = "result";
      result.textContent = "Running demo...";

      try {
        if (name === "summary") {
          const response = await fetch("/summary");
          showSummary(await response.json());
          return;
        }

        const endpoint = name === "risk" ? "/predict/risk" : name === "claim" ? "/predict/claim" : "/score/visit";
        const response = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payloads[name])
        });
        const data = await response.json();

        if (!response.ok) {
          throw new Error(JSON.stringify(data, null, 2));
        }

        if (name === "risk") showPrediction("Visit Risk Prediction", data);
        if (name === "claim") showPrediction("Insurance Claim Outcome Prediction", data);
        if (name === "score") showSignals(data);
      } catch (error) {
        result.className = "result";
        result.textContent = `Demo request failed.\\n\\n${error.message}`;
      }
    }

    buttons.forEach((button) => {
      button.addEventListener("click", () => runDemo(button.dataset.demo));
    });
    runDemo("summary");
  </script>
</body>
</html>
"""


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


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    return HTMLResponse(DASHBOARD_HTML)


@app.get("/health")
@app.get("/api/health")
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
