# Example patients

Synthetic demo patients (no real patient data) for the [demo](../demo.html).
They are also embedded in the page — use the **"Load example ▾"** dropdown, or
switch to *With X-ray*, **Import CSV**, and pick one.

The demo is a **two-stage GP triage**:
- **Stage 1 (clinical only)** → should this knee be **X-rayed**?
- **Stage 2 (with the X-ray)** → refer to an **OA specialist to discuss surgery**?

| File | Stage 1 (X-ray?) | Stage 2 (specialist?) | Expected time to surgery |
| --- | --- | --- | --- |
| `example_healthy.csv` | 🟢 no X-ray | 🟢 conservative | > 16 y |
| `example_mild_moderate_oa.csv` | 🟡 consider X-ray | 🟢 conservative | > 16 y |
| `example_moderate_oa.csv` | 🔴 X-ray | 🟡 routine referral | > 16 y |
| `example_no_surgery_within_10y.csv` | 🔴 X-ray | 🟡 routine referral | ≈ 14 y |
| `example_surgery_within_10y.csv` | 🔴 X-ray | 🔴 discuss surgery | ≈ 10 y |
| `example_surgery_within_7y.csv` | 🔴 X-ray | 🔴 discuss surgery | ≈ 7 y |
| `example_surgery_within_5y.csv` | 🔴 X-ray | 🔴 discuss surgery | ≈ 5 y |
| `example_surgery_within_4y.csv` | 🔴 X-ray | 🔴 discuss surgery | ≈ 4 y |

*Moderate OA* shows the value of imaging: the clinical picture alone says "get an
X-ray" (red), but with the X-ray the risk is only moderate (amber → routine, not
urgent). "Expected time to surgery" is the median time-to-event (when cumulative
risk reaches 50 %).

**Why no 1–3 year examples?** Even the most severe knee has a ~4-year median;
total knee replacement within 1–3 years of baseline is rare in OAI, so the data
does not support that prediction.

⚠️ Illustrative, model-generated — not real patients, not clinical advice. The
green/amber/red thresholds are placeholders to be set with a clinician.
