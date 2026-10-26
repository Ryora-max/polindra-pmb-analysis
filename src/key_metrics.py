"""Hitung metrik kunci dari data -> outputs/key_metrics.md.

Satu sumber kebenaran untuk angka di README / EXECUTIVE_REPORT.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

p = pd.read_csv("data/raw/pendaftar.csv")
m = pd.read_csv("data/raw/mahasiswa.csv")
k = pd.read_csv("data/raw/khs.csv")

th = p.groupby("tahun_daftar").agg(
    n=("id_pendaftar", "size"),
    lulus=("status_seleksi", lambda s: (s == "Lulus").sum()))
th["pct"] = 100 * th.lulus / th.n

lu = p[p.status_seleksi == "Lulus"]
yld = lu.groupby("jalur_masuk").daftar_ulang.apply(lambda s: 100 * (s == "Ya").mean())
anova = stats.f_oneway(*[g.ipk.dropna() for _, g in m.groupby("jalur_masuk")])
allv = m.ipk.dropna()
eta2 = sum(len(g) * (g.ipk.mean() - allv.mean()) ** 2
           for _, g in m.groupby("jalur_masuk")) / ((allv - allv.mean()) ** 2).sum()
cium = ["Kab. Indramayu", "Kab. Cirebon", "Kota Cirebon", "Kab. Majalengka", "Kab. Kuningan"]

m["do"] = (m.status_mahasiswa == "Drop Out").astype(int)
last = k.groupby("nim").semester.max()
do_last = last[m.loc[m["do"] == 1, "nim"]]
ip1 = k[k.semester == 1].set_index("nim").ip_semester
al = m.assign(ip1=m.nim.map(ip1)).dropna(subset=["ip1"])
al = al.merge(p[["id_pendaftar", "nilai_rapor"]], on="id_pendaftar", how="left")

rule = []
for th_ in (2.5, 3.0, 3.2):
    f = al[al.ip1 < th_]
    rule.append(f"IP1<{th_}: flag {100*len(f)/len(al):.0f}% mhs, recall "
                f"{100*f['do'].sum()/al['do'].sum():.0f}%, precision "
                f"{100*f['do'].mean():.1f}%, lift {f['do'].mean()/al['do'].mean():.2f}x")

lg = smf.logit("do ~ ip1 + nilai_rapor + C(jenis_sekolah) + C(jurusan) + C(jalur_masuk)"
               " + C(beasiswa_kip)", data=al.dropna(subset=["nilai_rapor"])).fit(disp=0)
orr = pd.DataFrame({"OR": np.exp(lg.params), "p": lg.pvalues}).drop("Intercept")
sig = orr[orr.p < 0.05].sort_values("OR")

X = pd.get_dummies(al.dropna(subset=["nilai_rapor"])[
    ["nilai_rapor", "ip1", "jenis_kelamin", "jenis_sekolah", "jurusan",
     "jalur_masuk", "beasiswa_kip"]], drop_first=True).astype(float)
y = al.dropna(subset=["nilai_rapor"])["do"]
auc = cross_val_score(
    RandomForestClassifier(200, max_depth=6, random_state=7, n_jobs=-1), X, y,
    cv=StratifiedKFold(5, shuffle=True, random_state=7), scoring="roc_auc")

L = [
    "# Key metrics POLINDRA (dihitung otomatis dari data)", "",
    f"- Pendaftar {len(p):,} | Mahasiswa {len(m):,} | KHS {len(k):,}",
    f"- Pendaftar {th.n.iloc[0]:,} -> {th.n.iloc[-1]:,} "
    f"(+{100*(th.n.iloc[-1]/th.n.iloc[0]-1):.0f}%); lulus seleksi "
    f"{th.pct.iloc[0]:.1f}% -> {th.pct.iloc[-1]:.1f}%; kursi lulus "
    f"{th.lulus.iloc[0]:,} -> {th.lulus.iloc[-1]:,} (+{100*(th.lulus.iloc[-1]/th.lulus.iloc[0]-1):.0f}%)",
    "- Yield daftar ulang (lulus -> registrasi): " + ", ".join(
        f"{a} {b:.1f}%" for a, b in yld.sort_values().items()),
    f"- ANOVA IPK ~ jalur: F={anova.statistic:.1f}, p={anova.pvalue:.1e}, eta^2={eta2:.3f}",
    "- Mahasiswa per jalur: " + ", ".join(
        f"{a} {b:,}" for a, b in m.jalur_masuk.value_counts().items()),
    f"- Kab. Indramayu {100*(m.asal_kota=='Kab. Indramayu').mean():.1f}% | "
    f"Ciayumajakuning (5 wilayah) {100*m.asal_kota.isin(cium).mean():.1f}%",
    f"- Dropout rate {100*m['do'].mean():.1f}%; {100*(do_last<=2).mean():.0f}% DO "
    f"berhenti dalam 2 semester pertama",
    f"- Rata IP sem-1: DO {al[al['do']==1].ip1.mean():.2f} vs non-DO {al[al['do']==0].ip1.mean():.2f}",
    *[f"- Aturan {r}" for r in rule],
    "- Logit DO (p<0.05): " + "; ".join(f"{i} OR={r.OR:.2f}" for i, r in sig.iterrows()),
    f"- Random Forest DO ROC-AUC 5-fold CV: {auc.mean():.2f} +- {auc.std():.2f}",
]
open("outputs/key_metrics.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
