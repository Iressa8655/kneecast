# Internal validation

Discrimination and the triage operating points, from **5-fold cross-validation**
(out-of-fold predictions) on the OAI cohort — the same data the models are
trained on. Outcome = total knee replacement; "5-year event" = TKR within 5 years
(4.5 % of the cohort, 208 / 4610).

| | Stage 1 — clinical model (X-ray?) | Stage 2 — + X-ray model (specialist?) |
| --- | --- | --- |
| Harrell C (OOF) | **0.77** (per-fold 0.770 ± 0.018) | **0.84** (0.835 ± 0.014) |
| Uno C, 5-year (IPCW) | 0.83 | 0.88 |
| Green cut-off **5 %** — sensitivity / specificity / flagged | 76 % / 74 % / 28 % | 85 % / 76 % / 27 % |
| Red cut-off — sensitivity / specificity / flagged | ≥10 %: 54 % / 89 % / 13 % | ≥20 %: 37 % / 97 % / 5 % |

**Reading it**

- Adding the X-ray lifts discrimination from C = 0.77 to 0.84.
- Stage 2 at the 5 % green cut-off catches **85 %** of patients who reach TKR
  within 5 years (anyone amber-or-above is referred); ~15 % fall in green and are
  managed conservatively **with review**, so a worsening knee re-enters the pathway.
- The out-of-fold numbers are essentially the same as in-sample, i.e. the
  penalised Cox model is not over-fitting.

**⚠️ Limits**

- This is **internal** validation on one US cohort — not external validation.
  Performance in a Dutch hospital is unknown (the transportability caveat in the
  [compliance notes](https://github.com/OuyangXiaotong/oai-summer-school-umcg/blob/main/docs/COMPLIANCE_NOTES.md)
  still stands). Re-estimate on a held-out / external validation set before use.
- Thresholds are set at each model's Youden-optimal point; confirm them with a
  clinician and a decision-curve / cost analysis.

Reproduce: 5-fold `StratifiedKFold` (seed 42) on `clean_master`, CoxNet per fold,
out-of-fold 5-year risk → C-index and sensitivity/specificity vs 5-year TKR.
