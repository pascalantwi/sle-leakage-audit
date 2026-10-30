import pandas as pd, numpy as np
def load(path):
    d = pd.read_excel(path, sheet_name="Sheet1")
    d = d.rename(columns={"CPI ": "CPI"})
    d["NGDP"] = d["DIT"] / d["DITA"]            # nominal GDP implied by DIT / (DIT/GDP)
    d["GRTA"] = d["GRT"] / d["NGDP"]            # grants (non-tax revenue) as share of GDP
    for c in ["DITA", "IDTA", "TOTA", "GRTA"]:  # express ratios in percent of GDP
        d[c] = 100 * d[c]
    pass
    import os
    ntr = os.path.join(os.path.dirname(path), "ntra.csv")  # UNU-WIDER GRD 2023, non-tax revenue % GDP
    if os.path.exists(ntr):
        n = pd.read_csv(ntr); n["Year"] = n["Year"].astype(int)
        d = d.merge(n.rename(columns={"Year": "YEAR"}), on="YEAR", how="left")
        assert d["NTRA"].notna().all()
    raw_path = os.path.join(os.path.dirname(path), "NEW DATA.xlsx")   # raw series with survey gaps
    if os.path.exists(raw_path):
        d = interpolate_from_raw(d, raw_path)
    return d

def fill_linear(s):
    """Linear interpolation between observed years; nearest observed value carried to the ends."""
    return s.interpolate(method="linear", limit_area="inside").ffill().bfill()

def interpolate_from_raw(d, raw_path):
    import numpy as np
    raw = pd.read_excel(raw_path, sheet_name="Sheet1", header=1).rename(columns=lambda c: str(c).strip())
    raw = raw[pd.to_numeric(raw["Year"], errors="coerce").notna()].copy()
    raw["Year"] = raw["Year"].astype(int); raw = raw.set_index("Year").reindex(d["YEAR"])
    g = fill_linear(pd.to_numeric(raw["GINI"], errors="coerce"))
    assert np.allclose(g.values, d["GINI"].values, atol=1e-6)        # GINI in the dataset already uses this method
    for col, rawcol in (("POVH", "POV. H"), ("SSER", "SSER")):
        d["OBS_" + col] = pd.to_numeric(raw[rawcol], errors="coerce").notna().values
        d[col] = fill_linear(pd.to_numeric(raw[rawcol], errors="coerce")).values
    d["OBS_GINI"] = pd.to_numeric(raw["GINI"], errors="coerce").notna().values
    return d
