"""ARDL estimation for the thesis: AIC lag selection (all regressors kept), bounds test with
simulated small-sample critical values (case III), long-run coefficients, ECM, diagnostics, CUSUM."""
import sys, json, itertools, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy import stats
from statsmodels.stats.diagnostic import acorr_breusch_godfrey, het_breuschpagan
from statsmodels.stats.stattools import jarque_bera
sys.path.insert(0, sys.argv[2]); from prep import load

HB = 2  # hold-back: first two years (1983, 1984) used only as lags -> 38 observations, 1985-2022

def lag(s, k): return s.shift(k)

def levels_design(d, y, X, p, q):
    cols = {f"{y}(-{i})": lag(d[y], i) for i in range(1, p + 1)}
    for x, qq in zip(X, q):
        for l in range(qq + 1):
            cols[x if l == 0 else f"{x}(-{l})"] = lag(d[x], l)
    D = pd.DataFrame(cols).iloc[HB:]
    return d[y].iloc[HB:], sm.add_constant(D)

def uecm_design(d, y, X, p, q):
    dy = d[y].diff()
    cols = {f"{y}(-1)": lag(d[y], 1)}
    for x, qq in zip(X, q):                       # EViews convention: q=0 regressors enter at x_t
        cols[f"{x}(-1)" if qq > 0 else x] = lag(d[x], 1) if qq > 0 else d[x]
    for i in range(1, p):
        cols[f"D({y}(-{i}))"] = lag(dy, i)
    for x, qq in zip(X, q):
        dx = d[x].diff()
        for l in range(qq):
            cols[f"D({x})" if l == 0 else f"D({x}(-{l}))"] = lag(dx, l)
    D = pd.DataFrame(cols).iloc[HB:]
    return dy.iloc[HB:], sm.add_constant(D)

def select(d, y, X):
    best = None
    for p in (1, 2):
        for q in itertools.product((0, 1, 2), repeat=len(X)):
            yy, Z = levels_design(d, y, X, p, q)
            aic = sm.OLS(yy, Z).fit().aic
            if best is None or aic < best[0]:
                best = (aic, p, q)
    return best

def fstat_bounds(yv, Z, level_cols):
    r = sm.OLS(yv, Z).fit()
    R = np.zeros((len(level_cols), Z.shape[1]))
    for i, c in enumerate(level_cols): R[i, list(Z.columns).index(c)] = 1
    return float(r.f_test(R).fvalue)

def simulate_cv(p, q, k, n, nsim=20000, seed=1):
    """Exact small-sample bounds (case III): y is a random walk unrelated to x under H0.
    I(0) bound: x are white noise; I(1) bound: x are random walks. Same lag structure and sample size."""
    rng = np.random.default_rng(seed); T = n + HB + 50
    out = {}
    for name, integ in (("I0", False), ("I1", True)):
        F = np.empty(nsim)
        for s in range(nsim):
            e = rng.standard_normal((T, k + 1))
            ysim = np.cumsum(e[:, 0]); xs = e[:, 1:]
            if integ: xs = np.cumsum(xs, axis=0)
            sim = pd.DataFrame(np.column_stack([ysim, xs])[50:], columns=["y"] + [f"x{j}" for j in range(k)])
            yv, Z = uecm_design(sim, "y", [f"x{j}" for j in range(k)], p, q)
            lc = ["y(-1)"] + [f"x{j}(-1)" if qq > 0 else f"x{j}" for j, qq in enumerate(q)]
            F[s] = fstat_bounds(yv, Z, lc)
        out[name] = {a: float(np.quantile(F, 1 - a)) for a in (0.10, 0.05, 0.01)}
    return out


def cusum(Xm, yv, a=0.948):
    """Brown, Durbin & Evans (1975) CUSUM of recursive residuals with 5% bounds (a = 0.948)."""
    n, k = Xm.shape; w = []
    for t in range(k, n):
        Xt, yt = Xm[:t], yv[:t]
        XtX_inv = np.linalg.pinv(Xt.T @ Xt); b = XtX_inv @ Xt.T @ yt
        x = Xm[t]; w.append((yv[t] - x @ b) / np.sqrt(1 + x @ XtX_inv @ x))
    w = np.array(w); s = w.std(ddof=1); W = np.cumsum(w) / s
    r = np.arange(1, n - k + 1); m = n - k
    hi = a * (np.sqrt(m) + 2 * r / np.sqrt(m))
    return W, -hi, hi

def run(d, y, X, label):
    aic, p, q = select(d, y, X)
    yy, Z = levels_design(d, y, X, p, q); lv = sm.OLS(yy, Z).fit()
    dy, U = uecm_design(d, y, X, p, q); ue = sm.OLS(dy, U).fit()
    assert np.allclose(lv.resid.values, ue.resid.values, atol=1e-6)  # UECM is a reparameterisation
    lvl_cols = [f"{y}(-1)"] + [f"{x}(-1)" if qq > 0 else x for x, qq in zip(X, q)]
    F = fstat_bounds(dy, U, lvl_cols)
    cv = simulate_cv(p, q, len(X), len(yy))
    # long-run coefficients by the delta method: beta_j = -lambda_j / lambda_0
    lam0 = ue.params[f"{y}(-1)"]; V = ue.cov_params(); lr = {}
    for x, c in zip(["Constant"] + X, ["const"] + lvl_cols[1:]):
        b = -ue.params[c] / lam0
        g = np.zeros(len(ue.params)); g[list(U.columns).index(c)] = -1 / lam0; g[list(U.columns).index(f"{y}(-1)")] = ue.params[c] / lam0**2
        se = float(np.sqrt(g @ V.values @ g)); t = b / se
        lr[x] = dict(coef=float(b), se=se, t=float(t), p=float(2 * stats.t.sf(abs(t), ue.df_resid)))
    sr = {c: dict(coef=float(ue.params[c]), se=float(ue.bse[c]), t=float(ue.tvalues[c]), p=float(ue.pvalues[c]))
          for c in U.columns if c.startswith("D(")}
    ect = dict(coef=float(lam0), se=float(ue.bse[f"{y}(-1)"]), t=float(ue.tvalues[f"{y}(-1)"]), p=float(ue.pvalues[f"{y}(-1)"]))
    bg = acorr_breusch_godfrey(lv, nlags=1); bp = het_breuschpagan(lv.resid, lv.model.exog); jb = jarque_bera(lv.resid)
    cus, lo, hi = cusum(Z.values, yy.values)
    inside = bool(np.all((cus >= lo) & (cus <= hi)))
    ci = (lo, hi)
    lev = {c: dict(coef=float(lv.params[c]), se=float(lv.bse[c]), p=float(lv.pvalues[c])) for c in Z.columns}
    return dict(label=label, y=y, X=X, p=p, q=list(q), aic=float(aic), n=int(lv.nobs), r2=float(lv.rsquared), adjr2=float(lv.rsquared_adj),
                F_reg=float(lv.fvalue), F_reg_p=float(lv.f_pvalue), bounds_F=F, cv=cv, k=len(X), longrun=lr, shortrun=sr, ect=ect, levels=lev,
                ecm_r2=float(ue.rsquared), ecm_adjr2=float(ue.rsquared_adj),
                diag=dict(bg=float(bg[0]), bg_p=float(bg[1]), bp=float(bp[0]), bp_df=int(lv.model.exog.shape[1] - 1), bp_p=float(bp[1]), jb=float(jb[0]), jb_p=float(jb[1]), cusum_inside=inside),
                cusum=dict(y=[float(v) for v in cus], lo=[float(v) for v in ci[0]], hi=[float(v) for v in ci[1]],
                           years=[int(v) for v in d["YEAR"].iloc[HB:].values[-len(cus):]]))

if __name__ == "__main__":
    d = load(sys.argv[1]).reset_index(drop=True)
    S = [("GINI", ["DITA", "IDTA", "FDI", "INF"], "Income inequality"),
         ("SSER", ["DITA", "GDPPC", "GEX"], "Access to education"),
         ("IMU", ["DITA", "IDTA", "NTRA", "INF"], "Access to healthcare"),
         ("POVH", ["DITA", "GDPPC", "GINI", "GEX", "AG"], "Poverty headcount"),
         ("GDPPC", ["TOTA", "FDI", "GEX", "INF", "AG"], "GDP per capita")]
    only = sys.argv[4].split(',') if len(sys.argv) > 4 else None
    res = [run(d, y, X, lab) for y, X, lab in S if only is None or y in only]
    json.dump(res, open(sys.argv[3], "w"), indent=1)
    for r in res:
        print(f"\n### {r['label']}  ARDL({r['p']},{','.join(map(str, r['q']))})  n={r['n']}  R2={r['r2']:.4f} adjR2={r['adjr2']:.4f}")
        cv = r["cv"]; print(f"Bounds F={r['bounds_F']:.3f}  5%: I0={cv['I0'][0.05]:.3f} I1={cv['I1'][0.05]:.3f} | 10%: {cv['I0'][0.1]:.3f}/{cv['I1'][0.1]:.3f} | 1%: {cv['I0'][0.01]:.3f}/{cv['I1'][0.01]:.3f}")
        print("ECT", {k: round(v, 4) for k, v in r["ect"].items()})
        print("LR ", {k: (round(v['coef'], 4), round(v['p'], 4)) for k, v in r["longrun"].items()})
        print("SR ", {k: (round(v['coef'], 4), round(v['p'], 4)) for k, v in r["shortrun"].items()})
        print("DIAG", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r["diag"].items()})
