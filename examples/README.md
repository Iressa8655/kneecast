# Example patients

Synthetic demo patients (no real patient data) for the [demo](../demo.html).
**Switch to "With X-ray" mode, click "Import CSV", and pick one** — the fields
fill in, then press *Estimate risk*.

| File | Expected time to surgery | 5-year risk |
| --- | --- | --- |
| `example_surgery_within_4y.csv` | ≈ 4 years | 62 % |
| `example_surgery_within_5y.csv` | ≈ 5 years | 50 % |
| `example_surgery_within_7y.csv` | ≈ 7 years | 36 % |
| `example_surgery_within_10y.csv` | ≈ 10 years | 24 % |
| `example_no_surgery_within_10y.csv` | ≈ 14 years | 15 % |

"Expected time to surgery" is the median time-to-event (when cumulative risk
reaches 50 %). Each file is one header row of feature names + one row of values,
matching the demo's fields.

**Why no 1–3 year examples?** The soonest the model puts a *median* time to
replacement is ~4 years, even for the most severe knee. Total knee replacement
within 1–3 years of baseline is rare in the OAI cohort, so the data does not
support that prediction — a limit worth stating rather than faking.

⚠️ Illustrative, model-generated — not real patients, not clinical advice.
