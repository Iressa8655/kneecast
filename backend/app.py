"""
app.py  —  KneeCast prediction API (the "hospital server")

Loads the frozen model(s) and turns a patient's baseline data into a time-to-
total-knee-replacement risk curve. Runs locally / on the hospital's own machine,
so patient data never leaves the building.

    uvicorn app:app --reload --port 8000

Two modes (chosen per request):
    clinical      — clinical + demographics only (no X-ray needed)
    radiographic  — clinical + radiographic severity (KL grade, JSW ...)

Endpoints:
    GET  /health           -> {status, model, modes}
    GET  /meta             -> per-mode feature list + ranges (drives the form)
    POST /predict?mode=..  -> {features:{...}} -> risk curve + per-year risk

⚠️ Research/education demo. Not a medical device. Trained on US OAI data
(transportability unvalidated). Outcome = TOTAL knee replacement (626 events).
"""
from __future__ import annotations
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

HERE = Path(__file__).resolve().parent
BUNDLE = joblib.load(HERE / "model.joblib")
META = json.loads((HERE / "meta.json").read_text(encoding="utf-8"))
MODELS = BUNDLE["models"]                       # {"clinical": {...}, "radiographic": {...}}

YEARS = [1, 2, 3, 4, 5]
CURVE_DAYS = np.linspace(0, int(365.25 * 5), 61)   # 0..5y, ~monthly

# Two-stage GP triage. The bands are keyed on 5-year risk and derived from the
# cohort risk distribution (X-ray = low bar / high sensitivity; surgery referral
# = high bar). ⚠️ ILLUSTRATIVE placeholders — set with the clinical mentor and a
# decision-curve / cost-effectiveness analysis before any real use.
# Both boundaries sit at the Youden-optimal ~5% (best sensitivity/specificity
# balance the models give) rather than an aggressive cut — so neither stage
# misses many true cases. "green" is conservative care WITH review, not
# discharge. Stage 2: anyone amber-or-above is referred, so surgery-bound
# patients reach the specialist. ⚠️ In-sample thresholds — validate out-of-fold
# and with a clinician before real use.
TRIAGE = {
    "clinical": {            # stage 1 — X-ray?  (Youden ~5%: sens 77%, spec 74%)
        "question": "Should this knee be X-rayed?",
        "bands": [
            (0.05, "green", "Conservative care + review in ~12 months — no X-ray yet"),
            (0.10, "amber", "Consider a knee X-ray (clinical judgement)"),
            (2.00, "red",   "Refer for a weight-bearing knee X-ray"),
        ],
    },
    "radiographic": {        # stage 2 — specialist?  (green 5%: sens 88%, spec 76%)
        "question": "Refer to an OA specialist to discuss surgery?",
        "bands": [
            (0.05, "green", "Continue conservative care; re-review later"),
            (0.20, "amber", "Refer to OA specialist — routine / shared decision"),
            (2.00, "red",   "Refer to OA specialist — priority, discuss surgery"),
        ],
    },
}


def _triage(mode, risk5):
    cfg = TRIAGE[mode]
    for thr, band, action in cfg["bands"]:
        if risk5 < thr:
            return {"question": cfg["question"], "band": band, "action": action}
    return None

# full time support of each model, for the median time-to-event
def _tmax(mode):
    m = MODELS[mode]["pipe"].named_steps["model"]
    et = getattr(m, "event_times_", None)
    return float(et[-1]) if et is not None and len(et) else 365.25 * 16


TMAX = {mode: _tmax(mode) for mode in MODELS}


def _median_years(mode, sf):
    """Time where cumulative replacement risk first reaches 50% (median time to
    surgery). None if the patient never reaches 50% within the model's horizon."""
    grid = np.linspace(0, TMAX[mode], 400)
    for t in grid:
        if 1 - float(sf(t)) >= 0.5:
            return round(t / 365.25, 1)
    return None


def _defaults(mode):
    m = META[mode]
    d = {c: m["numeric"][c]["median"] for c in m["numeric"]}
    d.update({c: m["categorical"][c]["mode"] for c in m["categorical"]})
    return d


DEFAULTS = {mode: _defaults(mode) for mode in MODELS}

app = FastAPI(title="KneeCast API")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


class PredictIn(BaseModel):
    features: dict


def _survival_function(mode, feat):
    b = MODELS[mode]
    cols = b["numeric"] + b["categorical"]
    row = {c: feat.get(c, DEFAULTS[mode].get(c)) for c in cols}
    X = pd.DataFrame([row], columns=cols)
    Xt = b["pipe"].named_steps["pre"].transform(X)
    return b["pipe"].named_steps["model"].predict_survival_function(Xt)[0]


@app.get("/health")
def health():
    return {"status": "ok", "model": BUNDLE["model_name"], "modes": list(MODELS)}


@app.get("/meta")
def meta():
    return META


@app.post("/predict")
def predict(inp: PredictIn, mode: str = "clinical"):
    if mode not in MODELS:
        raise HTTPException(400, f"mode must be one of {list(MODELS)}")
    sf = _survival_function(mode, inp.features)
    cols = MODELS[mode]["numeric"] + MODELS[mode]["categorical"]
    return {
        "mode": mode,
        "model": BUNDLE["model_name"],
        "risk_by_year": {str(yr): float(1 - sf(365.25 * yr)) for yr in YEARS},
        "risk_5y": float(1 - sf(365.25 * 5)),
        "triage": _triage(mode, float(1 - sf(365.25 * 5))),
        "expected_time_years": _median_years(mode, sf),   # None if 50% not reached
        "horizon_years": round(TMAX[mode] / 365.25, 1),
        "curve": [{"days": int(d), "risk": float(1 - sf(d))} for d in CURVE_DAYS],
        "used_defaults_for": [c for c in cols if c not in inp.features],
        "disclaimer": "Research/education demo — not a medical device. "
                      "Outcome = total knee replacement.",
    }
