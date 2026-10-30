# Thesis corrections: Taxation and Welfare in Ghana (2026-10-30)

Changes made to `ELDER_JHON.zip`, saved as `ELDER_JHON_corrected.zip`. Analysis code is in `thesis_analysis/`.

## Supervisor comments

1. **Title:** "Taxation and Welfare in Ghana: An Autoregressive Distributed Lag (ARDL) Approach".
2. **Data period:** the data cover **1983–2022 (40 years)**. With two lags, the ARDL models use **1985–2022, 38 observations**. That estimation sample is where the "38" comes from. The Abstract and Chapters 3, 4 and 6 now say this consistently.
3. **Unit root tables:** split into Table 4.2 (levels) and Table 4.3 (first difference). All variables are now stationary at first difference.
4. **Section 4.5:** headings follow the four objectives (4.5.1–4.5.4) instead of "Determinants of …".

## Problems found in the original analysis, and fixes

| Problem | Evidence | Fix |
|---|---|---|
| Tax variables were in nominal cedis and are I(2), which invalidates the ARDL bounds test | ADF p = 0.96 (DIT) and 0.99 (TOT) at first difference | Use tax as % of GDP (DITA, IDTA, TOTA; matches UNU-WIDER GRD). All are I(0) or I(1). |
| Healthcare (Objective 3) was never estimated | The "HCA" diagnostics (BG 5.0401, BP 19.6031, JB 2.2048) reproduce exactly from the **poverty** model; the "POVH" diagnostics come from the **GDP per capita** model | Estimated a healthcare model: immunization coverage (IMU) on DITA, IDTA, non-tax revenue (GRD) and INF |
| Long-run summary table (e.g. GINI −3.608 to 7.594) could not be reproduced | No standard long-run quantity matches | Replaced with the bounds test, long-run coefficients and ECT for each model |
| No bounds test or ECT reported | — | Added Table 4.4 (bounds test) and an ECT row in each long-run table |
| CUSUM figure had no 5% bounds and mislabelled panels | — | New figure with bounds. Inequality and healthcare models are **unstable** (strucchange p = 0.004 and 0.0008) |
| Chapter 3 equations did not match the estimated models | e.g. TTR, OPI, gold price and logs were listed but never used | Equations rewritten to match the models |
| Trend and correlation text contradicted the data | e.g. "inflation exceeded 120% in 2022" (actually 1983); "SSER–GINI r ≈ −0.47" (actually +0.60) | Rewritten from the data; correlation matrix regenerated |

## How the findings changed

- **Inequality:** still no tax effect, short or long run.
- **Education:** still a delayed positive direct-tax effect two years later (+4.46, p = 0.015). No long-run relationship.
- **Healthcare (new):** cointegrated. Indirect taxes raise immunization in the long run (+5.56, p = 0.034). ECT = −0.375.
- **Poverty:** government expenditure still reduces poverty in the same year (−4.03, p = 0.002), but the effect reverses the next year.
- **Growth:** total tax from the previous year raises GDP per capita (+22.67, p = 0.019).

## Still to check (Pascal / candidate)

- Data sources and units in Table 3.1 (Definition of Variables). In particular, check the exact immunization indicator (DPT or measles) and the base year of GDP per capita.
- The Chapter 5 literature discussion was kept. Only the result statements were updated.
