# KneeCast

Prognostic decision-support for knee osteoarthritis: predicts which patients will
progress to a **total knee replacement**, so clinicians triage referrals.

DASH Hackathon 2026 · Orange group. Working product name (pending team vote).

**Live:** https://iressa8655.github.io/kneecast/

## What's here

- `index.html` — the landing site (self-contained).
- `demo.html` — interactive demo: enter a patient's data, get a risk curve.
  Toggles between a clinical-only and a clinical + X-ray model. It calls the
  local backend below.
- `backend/` — a small FastAPI "hospital server" that serves the survival model
  (`/predict`). See [`backend/README.md`](backend/README.md).
- `group-pic.png` — team photo (add this file to show it in "Meet the team").

## Try the demo locally

The site is static (GitHub Pages), but the demo needs the model server, which
runs on your own machine — patient data is posted only to that local server, not
to any third party.

```bash
cd backend
# one-time env (scikit-survival needs conda-forge, see backend/requirements.txt)
conda create -n kneecast -c conda-forge python=3.11 scikit-survival fastapi uvicorn pandas pyarrow joblib
conda activate kneecast
python train_model.py      # builds model.joblib (needs the oai repo + OAI access)
uvicorn app:app --port 8000
```

Then open `demo.html` and press **Estimate risk**. On the public Pages URL the
demo can't reach your `localhost`, so run it locally for a live demo.

## Model

A penalised Cox survival model trained on the OAI cohort via the Track A data
pipeline (see the [oai repo](https://github.com/OuyangXiaotong/oai-summer-school-umcg)).
Outcome = total knee replacement (626 events). The trained model
(`backend/model.joblib`) is **git-ignored** — it is derived from access-restricted
OAI data and this repo is public; build it locally with `train_model.py`.

Internal 5-fold cross-validation (Harrell C 0.77 clinical / 0.84 with X-ray, plus
the triage sensitivity/specificity) is in
[`backend/VALIDATION.md`](backend/VALIDATION.md).

## Deploy

Published with GitHub Pages from `main` / root.

## ⚠️ Not a medical device

Student project, research / education only. Trained on US OAI data;
transportability to other health systems is unvalidated. It ranks; it does not
diagnose.
