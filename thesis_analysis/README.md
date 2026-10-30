# Thesis analysis: Taxation and Welfare in Ghana (ARDL)

Code that produces every number in Chapter 4 of `ELDER_JHON_corrected.zip`.

## Data

- `John Mphil N.xlsx` (repo root, sheet `Sheet1`): annual data for Ghana, 1983–2022.
- `ntra.csv`: non-tax revenue (% of GDP) for Ghana, taken from the `Merged` sheet of
  `UNUWIDERGRD_2023 - Gh.xlsx` (UNU-WIDER Government Revenue Dataset 2023).

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
mkdir -p data && cp "../John Mphil N.xlsx" ntra.csv data/
python ardl.py "data/John Mphil N.xlsx" . results.json   # about 15 minutes (simulation)
mkdir -p gen && python gen.py results.json gen
```

The bounds-test critical values come from a simulation with a fixed seed, so a rerun
gives the same values.
