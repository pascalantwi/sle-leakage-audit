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
    return d
