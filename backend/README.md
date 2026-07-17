# KneeCast backend — the "hospital server"

A small FastAPI service that turns a patient's baseline data into a time-to-
total-knee-replacement risk curve. It stands in for a model running on a
hospital's own machine: patient data is posted to *this* server, not to any
third party.

## What's here

| File | |
| --- | --- |
| `app.py` | the API (`/health`, `/meta`, `/predict`) |
| `train_model.py` | fits + freezes the model(s) → `model.joblib` + `meta.json` |
| `model.joblib` | the frozen CoxNet models (clinical + radiographic) |
| `meta.json` | per-mode feature list + ranges (drives the web form) |

The model is a penalised Cox survival model from the Track C code, trained on the
Track A `clean_master` table with the real per-patient censoring
(`last_followup_days`). Outcome = **total** knee replacement (626 events).

## Run

```bash
# 1. environment (scikit-survival needs conda-forge, not pip — see requirements.txt)
conda create -n kneecast -c conda-forge python=3.11 scikit-survival fastapi uvicorn pandas pyarrow joblib
conda activate kneecast

# 2. start the server
uvicorn app:app --port 8000
```

Then open `../demo.html` in a browser (or serve the site) and it will call
`http://127.0.0.1:8000`.

## Re-training

`model.joblib` is committed so the demo runs out of the box. To rebuild it you
need the **oai** repo (it holds the restricted data + Track C code) as a sibling
folder, then:

```bash
OAI_REPO=/path/to/oai python train_model.py
```

## API

`POST /predict?mode=clinical|radiographic`

```json
{ "features": { "V00AGE": 68, "P01BMI": 31, "V00WOMKP_worse": 9,
                "V00XRKL_worse": 3 } }
```
Any omitted feature is filled with the cohort median/mode. Response: per-year
risk (1–5 y), the 5-year headline, and a ~monthly cumulative-risk curve.

## ⚠️ Not a medical device

Research / education demo. Trained on US OAI data; transportability to other
health systems is unvalidated. It ranks; it does not diagnose.
