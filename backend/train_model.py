"""
train_model.py  —  fit the survival model(s) once and freeze them for the API

Fits TWO models on the Track A table so the web form can toggle between them:
  clinical      — clinical + demographics only (no X-ray needed)
  radiographic  — clinical + radiographic severity (KL grade, JSW ...)

Reads the Track A table + Track C modelling code from the *oai* repo (kept
separate because it holds restricted data) and writes into this folder:
  model.joblib   both fitted pipelines
  meta.json      per-mode feature list + ranges, so the form can render fields

Point OAI_REPO at your local oai repo if it is not the sibling folder `../oai`:
    OAI_REPO=/path/to/oai  python train_model.py

The API (app.py) loads model.joblib and never re-fits, so the server — standing
in for a hospital's own machine — responds instantly and no raw cohort lives here.
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

import joblib

HERE = Path(__file__).resolve().parent
OAI = Path(os.environ.get("OAI_REPO", HERE.parents[1] / "oai")).resolve()
if not (OAI / "Compare model").exists():
    sys.exit(f"oai repo not found at {OAI} — set OAI_REPO=/path/to/oai")
sys.path.insert(0, str(OAI / "Compare model"))

import config as C        # noqa: E402
import data_io            # noqa: E402
import features           # noqa: E402
from models import make_pipeline   # noqa: E402

MODEL = "CoxNet"          # smooth monotonic curves + interpretable
# V00SITE is a US centre code stored as a letter (A–E); to_num() turns it into
# all-NaN, so it is silently dead weight anyway. Drop it: meaningless for a Dutch
# demo and the transportability liability flagged in the compliance notes.
DROP = ["V00SITE"]


def fit_one(df, radiographic):
    C.USE_RADIOGRAPHIC = radiographic
    # use the real per-patient censoring time from Track B (data-pipeline/
    # 10_followup_days.py) instead of a single ~16 y administrative horizon
    C.LAST_FOLLOWUP_DAYS_COL = "last_followup_days"
    X, y, numeric, categorical = features.prepare(df)
    drop = [c for c in DROP if c in X.columns]
    X = X.drop(columns=drop)
    numeric = [c for c in numeric if c not in drop]
    categorical = [c for c in categorical if c not in drop]
    pipe = make_pipeline(MODEL, numeric, categorical).fit(X, y)

    meta = {"model": MODEL, "n_train": int(X.shape[0]),
            "n_events": int(y["event"].sum()), "numeric": {}, "categorical": {}}
    for c in numeric:
        s = X[c].astype(float)
        meta["numeric"][c] = {"median": round(float(s.median()), 1),
                              "min": round(float(s.quantile(0.02)), 1),
                              "max": round(float(s.quantile(0.98)), 1)}
    for c in categorical:
        vals = sorted(v for v in X[c].dropna().unique())
        mode = X[c].mode(dropna=True)
        if not vals:
            continue
        meta["categorical"][c] = {
            "values": [int(v) if float(v).is_integer() else float(v) for v in vals],
            "mode": int(mode.iloc[0]) if len(mode) else None}
    return {"pipe": pipe, "numeric": numeric, "categorical": categorical}, meta


def main():
    df = data_io.load_table()
    bundle, meta = {}, {}
    for name, radiographic in [("clinical", False), ("radiographic", True)]:
        print(f"\n=== fitting '{name}' (radiographic={radiographic}) ===")
        b, m = fit_one(df, radiographic)
        bundle[name] = b
        meta[name] = m
        print(f"  {name}: {len(b['numeric']) + len(b['categorical'])} features, "
              f"{m['n_events']} events")

    joblib.dump({"models": bundle, "model_name": MODEL}, HERE / "model.joblib")
    (HERE / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("\nsaved model.joblib + meta.json (modes: clinical, radiographic)")


if __name__ == "__main__":
    main()
