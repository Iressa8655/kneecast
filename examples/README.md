# Example patients

Synthetic demo patients (no real patient data) for the [demo](../demo.html).
**Switch to "With X-ray" mode, click "Import CSV", and pick one** — the fields
fill in, then press *Estimate risk*.

| File | Expected time to surgery | 5-year risk |
| --- | --- | --- |
| `example_surgery_within_5y.csv` | ≈ 4.5 years | 56 % |
| `example_surgery_within_10y.csv` | ≈ 9.5 years | 25 % |
| `example_no_surgery_within_10y.csv` | ≈ 14 years | 15 % |

"Expected time to surgery" is the median time-to-event (when cumulative risk
reaches 50 %). Each file is one header row of feature names + one row of values,
matching the demo's fields.

⚠️ Illustrative, model-generated — not real patients, not clinical advice.
