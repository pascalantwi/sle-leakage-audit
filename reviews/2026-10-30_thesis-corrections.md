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

## Round 2: interpolation and Ghana evidence (supervisor comments)

### Interpolation

Comparing `NEW DATA.xlsx` (raw) with `John Mphil N.xlsx` (final) shows which years were filled:

| Variable | Observed | How the original file filled the gaps |
|---|---|---|
| GINI | 7 GLSS years (1987, 1988, 1991, 1998, 2005, 2012, 2016) | Linear interpolation, nearest value carried to the ends. Reproduces exactly; kept. |
| POVH | the same 7 years | **Unknown method.** Values range 4.5–80.8% although all survey values are 25–64%. Replaced with linear interpolation. |
| SSER | 32 years | Unknown (not linear or spline). Replaced with linear interpolation. |

New Section 3.3.1 "Treatment of Missing Data" gives the formula, a worked example and Table 3.1 (observed and filled years). It also states the limitations.

### Consequences

- **Interpolated POVH is I(2):** its first difference is not stationary under ADF and PP (p = 0.21–0.63); the second difference is. The bounds test is therefore not valid for the poverty model, which is reported as indicative only.
- **Education:** the main finding is stronger. DITA two years earlier gives +4.60 (p = 0.0015). The bounds test is inconclusive, the ECT is about 0, and the residuals are non-normal (JB p < 0.001).
- **Poverty:** GEX −0.117 (p = 0.030) and DITA insignificant. The earlier "effect reversed next year" result came from the unknown fill and has been removed. The ECT is about 0 and the residuals are non-normal.
- **Figures:** trend figures now mark observed and interpolated points; correlations, scatter plots and descriptive statistics are updated.

### Ghana empirical evidence added (Section 3.7.2)

Each was confirmed through search results (title, authors, venue). Full texts were not opened because the sandbox blocks those sites.

- Adu, Alagidede, Osei & Asamoah (2023), *Cogent Economics & Finance* 11(1), 2166211. Nonlinear ARDL; tax systems, poverty and inequality; Ghana 1983–2016.
- Ofori, Obeng & Armah (2018), *Cogent Economics & Finance* 6(1), 1537822. ARDL; exchange rate volatility and tax revenue in Ghana.
- Boachie (2015), MPRA Paper 67201. ARDL bounds test; health and growth in Ghana, 1982–2012.
- Atta-Ankomah, Lambon-Quayefio & Osei (2023), WIDER Working Paper 2023/91. Irregular GLSS-based inequality data for Ghana; supports the need to interpolate.

### Bibliography error found

The existing `adu2023tax` entry had a fabricated title, journal (*Journal of Economic Studies*), author initial and DOI. It is now corrected to the verified Cogent article. **Other `.bib` entries should be spot-checked.**
