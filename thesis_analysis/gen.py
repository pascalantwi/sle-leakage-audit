"""Turn results JSON into LaTeX tables and the CUSUM figure for the thesis."""
import sys, json, re
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

res = json.load(open(sys.argv[1]))
if len(sys.argv) > 3:                       # replace models re-estimated separately
    for r in json.load(open(sys.argv[3])):
        res = [r if x["y"] == r["y"] else x for x in res]
out = sys.argv[2]
R = {r["y"]: r for r in res}
json.dump(res, open(out + "/results_final.json", "w"), indent=1)

def star(p): return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""
def num(v, nd=4):
    a = abs(v)
    if a != 0 and a < 0.001: return f"{v:.6f}"
    return f"{v:.{nd}f}"
def var(name):
    m = re.fullmatch(r"D\((\w+)(?:\(-(\d)\))?\)", name)
    if m: return f"$\\Delta$ {m.group(1)}" + (f"$_{{t-{m.group(2)}}}$" if m.group(2) else "$_{t}$")
    return name

def order_str(r): return f"ARDL({r['p']}, {', '.join(map(str, r['q']))})"

def bounds_table():
    L = [r"\begin{table}[H]", r"\centering", r"\caption{ARDL Bounds Test for Cointegration}", r"\label{tab:bounds}",
         r"\resizebox{\textwidth}{!}{%", r"\begin{tabular}{llcccccc}", r"\hline",
         r"\textbf{Model} & \textbf{ARDL order} & \textbf{F-statistic} & $k$ & \multicolumn{2}{c}{\textbf{5\% critical values}} & \textbf{Decision} \\",
         r" & & & & I(0) & I(1) & \\", r"\hline"]
    for y, lab in (("GINI", "Income inequality (GINI)"), ("SSER", "Education (SSER)"), ("IMU", "Healthcare (IMU)"), ("POVH", "Poverty (POVH)"), ("GDPPC", "Growth (GDPPC)")):
        r = R[y]; F = r["bounds_F"]; c5 = r["cv"]["I0"]["0.05"], r["cv"]["I1"]["0.05"]
        c10 = r["cv"]["I0"]["0.1"], r["cv"]["I1"]["0.1"]
        dec = "Cointegrated" if F > c5[1] else ("Inconclusive" if F > c5[0] else "No cointegration")
        if F <= c5[1] and F > c10[1]: dec = "Inconclusive$^{a}$"
        if y == "POVH": dec = "Not valid$^{b}$"
        L.append(f"{lab} & {order_str(r)} & {F:.3f} & {r['k']} & {c5[0]:.3f} & {c5[1]:.3f} & {dec} \\\\")
    L += [r"\hline", r"\end{tabular}}",
          r"\par\footnotesize Note: Case III (unrestricted intercept, no trend). Critical values simulated for the estimation sample ($n = 38$) and each model's lag structure (20,000 replications). $k$ = number of regressors. $^{a}$Above the 10\\% upper bound. $^{b}$The F-statistic exceeds the upper bound, but the test is not valid because the interpolated poverty headcount behaves as an I(2) series (Section \\ref{sec:ur}).",
          r"\end{table}"]
    return "\n".join(L)

def lr_table(y, cap, label):
    r = R[y]
    L = [r"\begin{table}[H]", r"\centering", f"\\caption{{{cap}}}", f"\\label{{{label}}}", r"\begin{tabular}{lcccc}", r"\hline",
         r"\textbf{Variable} & \textbf{Coefficient} & \textbf{Std. Error} & \textbf{t-statistic} & \textbf{p-value} \\", r"\hline"]
    for k in r["X"] + ["Constant"]:
        v = r["longrun"][k]
        L.append(f"{k} & {num(v['coef'])} & {num(v['se'])} & {v['t']:.3f} & {v['p']:.4f}{star(v['p'])} \\\\")
    e = r["ect"]
    L += [r"\hline", f"ECT$_{{t-1}}$ (speed of adjustment) & {num(e['coef'])} & {num(e['se'])} & {e['t']:.3f} & {e['p']:.4f}{star(e['p'])} \\\\"]
    L += [r"\hline", f"\\multicolumn{{5}}{{l}}{{\\footnotesize Dependent variable: {y}. {order_str(r)}; observations: {r['n']} (1985--2022). *** p$<$0.01, ** p$<$0.05, * p$<$0.10.}} \\\\",
          r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)

def lagname(k):
    m = re.fullmatch(r"(\w+)\(-(\d)\)", k)
    return f"{m.group(1)}$_{{t-{m.group(2)}}}$" if m else (k if k != "const" else "Constant")

def sr_table(y, cap, label):
    r = R[y]
    L = [r"\begin{table}[H]", r"\centering", f"\\caption{{{cap}}}", f"\\label{{{label}}}", r"\begin{tabular}{lccc}", r"\hline",
         r"\textbf{Variable} & \textbf{Coefficient} & \textbf{Std. Error} & \textbf{p-value} \\", r"\hline"]
    items = list(r["levels"].items()); items = items[1:] + items[:1]      # constant last
    for k, v in items:
        L.append(f"{lagname(k)} & {num(v['coef'])} & {num(v['se'])} & {v['p']:.4f}{star(v['p'])} \\\\")
    L += [r"\hline", f"$R^2$ & \\multicolumn{{3}}{{c}}{{{r['r2']:.4f}}} \\\\", f"Adjusted $R^2$ & \\multicolumn{{3}}{{c}}{{{r['adjr2']:.4f}}} \\\\",
          f"F-statistic & \\multicolumn{{3}}{{c}}{{{r['F_reg']:.2f} (p $<$ 0.001)}} \\\\", f"Observations & \\multicolumn{{3}}{{c}}{{{r['n']} (1985--2022)}} \\\\", r"\hline",
          f"\\multicolumn{{4}}{{l}}{{\\footnotesize Dependent variable: {y}. {order_str(r)} selected by AIC. *** p$<$0.01, ** p$<$0.05, * p$<$0.10.}} \\\\",
          r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)

def diag_table():
    order = ["GINI", "SSER", "IMU", "POVH", "GDPPC"]
    L = [r"\begin{table}[H]", r"\centering", r"\caption{Diagnostic Tests for the Estimated ARDL Models}", r"\label{tab:diagnostic_tests}",
         r"\resizebox{\textwidth}{!}{%", r"\begin{tabular}{lccccc}", r"\hline",
         r"\textbf{Diagnostic Test} & \textbf{GINI} & \textbf{SSER} & \textbf{IMU} & \textbf{POVH} & \textbf{GDPPC} \\", r"\hline",
         r"\multicolumn{6}{l}{\textit{Breusch--Godfrey Serial Correlation LM Test}} \\"]
    g = lambda key: " & ".join(num(R[y]["diag"][key], 4) for y in order)
    gp = lambda key: " & ".join(f"{R[y]['diag'][key]:.4f}{star(R[y]['diag'][key])}" for y in order)
    L += [f"LM Statistic & {g('bg')} \\\\", f"p-value & {gp('bg_p')} \\\\", r"\hline",
          r"\multicolumn{6}{l}{\textit{Breusch--Pagan Heteroskedasticity Test}} \\",
          f"BP Statistic & {g('bp')} \\\\", f"p-value & {gp('bp_p')} \\\\", r"\hline",
          r"\multicolumn{6}{l}{\textit{Jarque--Bera Normality Test}} \\",
          f"JB Statistic & {g('jb')} \\\\", f"p-value & {gp('jb_p')} \\\\", r"\hline",
          "CUSUM within 5\\% bounds & " + " & ".join("Yes" if R[y]["diag"]["cusum_inside"] else "No" for y in order) + r" \\",
          r"\hline", r"\end{tabular}}", r"\end{table}"]
    return "\n".join(L)

def cusum_fig(path):
    titles = {"GINI": "Income Inequality (GINI)", "SSER": "Education (SSER)", "IMU": "Healthcare (IMU)", "POVH": "Poverty Headcount (POVH)", "GDPPC": "GDP per Capita (GDPPC)"}
    fig, axes = plt.subplots(3, 2, figsize=(10, 10.5)); axes = axes.ravel()
    for ax, y in zip(axes, ["GINI", "SSER", "IMU", "POVH", "GDPPC"]):
        c = R[y]["cusum"]; yrs = c["years"]
        ax.plot(yrs, c["y"], color="#1f4e79", lw=2, label="CUSUM")
        ax.plot(yrs, c["hi"], color="#c0392b", ls="--", lw=1.2, label="5% significance bounds"); ax.plot(yrs, c["lo"], color="#c0392b", ls="--", lw=1.2)
        ax.axhline(0, color="grey", lw=0.6); ax.set_title(titles[y], fontsize=11, fontweight="bold"); ax.set_xlabel("Year")
    axes[0].legend(fontsize=8, loc="upper left"); axes[-1].axis("off")
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)

open(out + "/tab_bounds.tex", "w").write(bounds_table())
open(out + "/tab_diag.tex", "w").write(diag_table())
for y, nm in (("GINI", "Income Inequality"), ("SSER", "Secondary School Enrollment"), ("IMU", "Immunization Coverage"), ("POVH", "Poverty Headcount"), ("GDPPC", "GDP per Capita")):
    open(out + f"/tab_lr_{y}.tex", "w").write(lr_table(y, f"Long-Run Effects of Taxation on {nm}", f"tab:lr_{y.lower()}"))
    open(out + f"/tab_sr_{y}.tex", "w").write(sr_table(y, f"Short-Run and Lagged Effects of Taxation on {nm}", f"tab:ardl_{y.lower()}"))
cusum_fig(out + "/cusum.png")
print("generated")
