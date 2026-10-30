# Thesis analysis: Taxation and Welfare in Ghana (ARDL)

Code that produces every number in Chapter 4 of `ELDER_JHON_corrected.zip`.

## Data

- `John Mphil N.xlsx` (repo root, sheet `Sheet1`): annual data for Ghana, 1983–2022.
- `ntra.csv`: non-tax revenue (% of GDP) for Ghana, taken from the `Merged` sheet of
  `UNUWIDERGRD_2023 - Gh.xlsx` (UNU-WIDER Government Revenue Dataset 2023).
- `NEW DATA.xlsx` (repo root): raw series with gaps. `prep.py` rebuilds poverty headcount
  (POVH) and secondary enrollment (SSER) from it by **linear interpolation**, carrying the
  nearest observed value to the end years. It also checks that the Gini series in
  `John Mphil N.xlsx` already follows exactly this rule.

  | Variable | Observed years | Filled |
  |---|---|---|
  | GINI, POVH | 1987, 1988, 1991, 1998, 2005, 2012, 2016 (GLSS rounds) | 33 of 40 |
  | SSER | all but 1992–1995, 1997–1999, 2011 | 8 of 40 |

  The poverty values in `John Mphil N.xlsx` were filled by an unknown method (they range
  from 4.5% to 80.8% although every survey value is between 25% and 64%), so they are
  replaced. The interpolated POVH behaves as I(2), so the poverty model's bounds test
  is not valid and its results are indicative only.

The tax variables used are `DITA`, `IDTA`, `TOTA` (direct, indirect and total tax as a
share of GDP, converted to percent). They match the UNU-WIDER GRD series. The nominal cedi
series (`DIT`, `IDT`, `TOT`) are not used: they grow more than 100,000-fold over the
period and are I(2), which breaks the ARDL bounds test.

## Files

| File | What it does |
|---|---|
| `prep.py` | Loads the data, converts tax ratios to percent, adds non-tax revenue |
| `ardl.py` | For each model: AIC lag search (max 2 lags, all regressors kept), ARDL and UECM by OLS, bounds F-test with simulated small-sample critical values (case III, n = 38, 20,000 replications), long-run coefficients (delta method), ECT, Breusch–Godfrey / Breusch–Pagan / Jarque–Bera tests, CUSUM |
| `gen.py` | Turns the results into the LaTeX tables and the CUSUM figure |
| `results_final.json` | Saved results used in the thesis |

## Rerun

```bash
pip install pandas openpyxl statsmodels scipy matplotlib
mkdir -p data && cp "../John Mphil N.xlsx" "../NEW DATA.xlsx" ntra.csv data/
python ardl.py "data/John Mphil N.xlsx" . results.json   # about 15 minutes (simulation)
mkdir -p gen && python gen.py results.json gen
```

The bounds-test critical values come from a simulation with a fixed seed, so a rerun
gives the same values.
