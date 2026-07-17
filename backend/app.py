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
        "curve": [{"days": int(d), "risk": float(1 - sf(d))} for d in CURVE_DAYS],
        "used_defaults_for": [c for c in cols if c not in inp.features],
        "disclaimer": "Research/education demo — not a medical device. "
                      "Outcome = total knee replacement.",
    }
