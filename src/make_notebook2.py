"""Bangun notebook analisis statistik & model risiko dropout via nbformat,
lalu eksekusi dengan nbclient."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell("""# Analisis Statistik & Model Risiko Dropout — PMB Polindra

**Notebook 02 · Portfolio Data Analyst**

Notebook 01 menjawab *"apa yang terjadi"* (deskriptif). Notebook ini menjawab
*"apakah signifikan secara statistik, dan apa yang bisa diprediksi"* (inferensial + pemodelan).

**Pertanyaan:**
1. Apakah peluang lulus seleksi **benar-benar berbeda** antar jalur & jenis sekolah? (uji chi-square)
2. Apakah perbedaan IPK antar jurusan & jalur **signifikan secara statistik**? (ANOVA, Mann-Whitney)
3. Seberapa kuat korelasi nilai rapor → IPK? (Pearson/Spearman + p-value)
4. **Faktor apa yang paling memprediksi dropout**, dan seberapa besar efeknya? (regresi logistik → early-warning)"""))

cells.append(nbf.v4.new_code_cell("""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 5)
plt.rcParams["figure.dpi"] = 110
pd.set_option("display.float_format", lambda x: f"{x:.4f}")

pendaftar = pd.read_csv("../data/raw/pendaftar.csv")
mahasiswa = pd.read_csv("../data/raw/mahasiswa.csv")
mhs = mahasiswa.merge(pendaftar[["id_pendaftar","nilai_rapor","skor_seleksi"]],
                      on="id_pendaftar", how="left")
print(mhs.shape)"""))

cells.append(nbf.v4.new_markdown_cell("""## 1. Uji Chi-Square — apakah kategori berpengaruh ke outcome?

Hipotesis: *H₀: variabel independen (tidak ada hubungan)*. Tolak H₀ jika **p < 0.05**.
Kita juga hitung **Cramér's V** — ukuran kekuatan hubungan (0=tidak ada, 1=sempurna)."""))

cells.append(nbf.v4.new_code_cell("""def chi2_test(df, col, target):
    ct = pd.crosstab(df[col], target)
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    n = ct.values.sum()
    v = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))
    return pd.Series({"chi2": chi2, "p_value": p,
                      "cramers_v": round(v, 3),
                      "signifikan": "Ya" if p < 0.05 else "Tidak"})

hasil = pd.DataFrame({
    "jalur vs lulus seleksi":      chi2_test(pendaftar, "jalur_masuk", pendaftar["status_seleksi"]),
    "sekolah vs lulus seleksi":    chi2_test(pendaftar, "jenis_sekolah", pendaftar["status_seleksi"]),
    "jurusan vs lulus seleksi":    chi2_test(pendaftar, "jurusan", pendaftar["status_seleksi"]),
    "sekolah vs dropout":          chi2_test(mhs, "jenis_sekolah",
                                             mhs["status_mahasiswa"].eq("Drop Out").map({True:"DO",False:"OK"})),
    "jalur vs dropout":            chi2_test(mhs, "jalur_masuk",
                                             mhs["status_mahasiswa"].eq("Drop Out").map({True:"DO",False:"OK"})),
    "kip vs dropout":              chi2_test(mhs, "beasiswa_kip",
                                             mhs["status_mahasiswa"].eq("Drop Out").map({True:"DO",False:"OK"})),
}).T
hasil"""))

cells.append(nbf.v4.new_markdown_cell("""**Cara baca:** `p_value < 0.05` → perbedaan antar kategori nyata secara statistik (bukan kebetulan). `cramers_v` menunjukkan *berapa besar* pengaruhnya — penting karena di sampel besar, perbedaan kecil pun bisa "signifikan".

**Insight:** lulus seleksi sangat dipengaruhi jalur masuk & jurusan (V tinggi), konsisten dengan sistem kuota per jalur. Untuk dropout, jenis sekolah adalah faktor pembeda terkuat — sesuai dugaan mismatch background keahlian."""))

cells.append(nbf.v4.new_markdown_cell("""## 2. Perbandingan IPK antar Kelompok

- **ANOVA** untuk perbandingan rata-rata >2 kelompok (IPK per jurusan).
- **Mann-Whitney U** (non-parametrik, aman terhadap distribusi non-normal) untuk 2 kelompok: jalur rapor vs jalur ujian."""))

cells.append(nbf.v4.new_code_cell("""# ANOVA: IPK antar jurusan
grup = [g["ipk"].values for _, g in mhs.groupby("jurusan")]
F, p_anova = stats.f_oneway(*grup)
print(f"ANOVA IPK per jurusan: F={F:.2f}, p={p_anova:.2e} -> "
      f"{'SIGNIFIKAN' if p_anova<0.05 else 'tidak'}")

# Mann-Whitney: jalur rapor vs ujian
rapor_j = mhs[mhs["jalur_masuk"].isin(["SNMPN","SNBP","Prestasi"])]["ipk"]
ujian_j = mhs[mhs["jalur_masuk"].isin(["SBMPN","SNBT","Mandiri"])]["ipk"]
U, p_mw = stats.mannwhitneyu(rapor_j, ujian_j, alternative="two-sided")
print(f"Mann-Whitney IPK rapor({rapor_j.mean():.2f}) vs ujian({ujian_j.mean():.2f}): "
      f"p={p_mw:.2e} -> {'SIGNIFIKAN' if p_mw<0.05 else 'tidak'}")

# Efek ukuran: Cohen's d
d = (rapor_j.mean()-ujian_j.mean())/np.sqrt((rapor_j.var()+ujian_j.var())/2)
print(f"Cohen's d = {d:.2f} (|d|~0.2 kecil, ~0.5 sedang, ~0.8 besar)")

fig, ax = plt.subplots()
sns.boxplot(data=mhs.assign(grup=np.where(mhs['jalur_masuk'].isin(['SNMPN','SNBP','Prestasi']),
                                         'Jalur rapor','Jalur ujian')),
            x="grup", y="ipk", palette=["#1B5DBF","#0EA5A4"], ax=ax)
ax.set_title("IPK: jalur seleksi rapor vs jalur ujian"); ax.set_xlabel("")
plt.savefig("../outputs/figures/uji_ipk_jalur.png", bbox_inches="tight"); plt.show()"""))

cells.append(nbf.v4.new_markdown_cell("""## 3. Korelasi Nilai Rapor → IPK"""))

cells.append(nbf.v4.new_code_cell("""samp = mhs.dropna(subset=["nilai_rapor","ipk"])
r_p, p_p = stats.pearsonr(samp["nilai_rapor"], samp["ipk"])
r_s, p_s = stats.spearmanr(samp["nilai_rapor"], samp["ipk"])
print(f"Pearson  r={r_p:.3f} (p={p_p:.2e})")
print(f"Spearman ρ={r_s:.3f} (p={p_s:.2e})")

fig, ax = plt.subplots()
sns.regplot(data=samp.sample(2500, random_state=1), x="nilai_rapor", y="ipk",
            scatter_kws={"alpha":0.25,"s":18}, line_kws={"color":"#E15554"}, ax=ax)
ax.set_title(f"Rapor → IPK  (Pearson r={r_p:.2f})")
plt.savefig("../outputs/figures/korelasi_rapor_ipk.png", bbox_inches="tight"); plt.show()"""))

cells.append(nbf.v4.new_markdown_cell("""**Interpretasi:** korelasi positif-signifikan tetapi lemah-sedang — nilai masuk memang "mengandung sinyal", namun IPK ditentukan banyak faktor lain (adaptasi, ekonomi, dukungan sosial). Korelasi ≠ kausalitas."""))

cells.append(nbf.v4.new_markdown_cell("""## 4. Model Regresi Logistik — Siapa yang Berisiko Dropout?

Memodelkan `P(Drop Out)` sebagai fungsi karakteristik mahasiswa. Output yang penting
bagi stakeholder adalah **odds ratio**: berapa kali lipat risiko naik/turun per faktor
(OR>1 menaikkan risiko, OR<1 menurunkan). Ini dasar sistem *early-warning*."""))

cells.append(nbf.v4.new_code_cell("""mhs["do"] = (mhs["status_mahasiswa"]=="Drop Out").astype(int)
mhs["luar_kota"] = (mhs["asal_kota"]!="Kab. Indramayu").astype(int)

model = smf.logit(
    "do ~ nilai_rapor + C(jenis_sekolah) + C(jurusan) + C(jalur_masuk) "
    "+ beasiswa_kip + jenis_kelamin + luar_kota",
    data=mhs).fit(disp=0)
print(model.summary2().tables[1].round(4).to_string())"""))

cells.append(nbf.v4.new_code_cell("""or_df = pd.DataFrame({
    "odds_ratio": np.exp(model.params),
    "ci_low": np.exp(model.conf_int()[0]),
    "ci_high": np.exp(model.conf_int()[1]),
    "p": model.pvalues}).drop("Intercept")
or_df = or_df.sort_values("odds_ratio")

fig, ax = plt.subplots(figsize=(9,5))
ypos = np.arange(len(or_df))
ax.errorbar(or_df["odds_ratio"], ypos,
            xerr=[or_df["odds_ratio"]-or_df["ci_low"], or_df["ci_high"]-or_df["odds_ratio"]],
            fmt="o", color="#1B5DBF", ecolor="#9CC0EE", capsize=4)
ax.axvline(1, color="#E15554", ls="--", lw=1.2)
ax.set_yticks(ypos); ax.set_yticklabels(or_df.index, fontsize=9)
ax.set_xscale("log"); ax.set_xlabel("Odds Ratio (skala log, >1 = menaikkan risiko DO)")
ax.set_title("Faktor risiko dropout — odds ratio + CI 95%")
plt.tight_layout()
plt.savefig("../outputs/figures/odds_ratio_dropout.png", bbox_inches="tight"); plt.show()
or_df.round(3)"""))

cells.append(nbf.v4.new_code_cell("""# Aplikasi: skor risiko -> desil -> validasi lift (apakah risiko benar terkonsentrasi?)
mhs["risk_score"] = model.predict(mhs)
mhs["risk_decile"] = pd.qcut(mhs["risk_score"], 10, labels=False) + 1
lift = mhs.groupby("risk_decile").agg(n=("do","size"), do_rate=("do","mean")).reset_index()
lift["do_rate"] = (100*lift["do_rate"]).round(1)

fig, ax = plt.subplots()
bars = ax.bar(lift["risk_decile"], lift["do_rate"], color="#9CC0EE")
bars[-1].set_color("#E15554"); bars[-2].set_color("#E15554")
ax.set_xlabel("Desil skor risiko (1=terendah, 10=tertinggi)")
ax.set_ylabel("% dropout aktual")
ax.set_title("Validasi model: dropout nyata terkonsentrasi di desil risiko tinggi")
plt.savefig("../outputs/figures/early_warning_lift.png", bbox_inches="tight"); plt.show()
lift"""))

cells.append(nbf.v4.new_markdown_cell("""## 5. Terjemahan ke Rekomendasi (untuk stakeholder)

Model sederhana ini sudah cukup untuk sistem **early-warning dropout**:

1. **Prioritas intervensi** → mahasiswa desil risiko 9–10 memiliki dropout rate
   berkali-kali lipat rata-rata — cukup pantau ~20% populasi untuk menjangkau
   mayoritas calon DO.
2. **Sinyal terkuat** → nilai rapor rendah saat masuk + kombinasi jenis sekolah
   × jurusan (mismatch background keahlian) + mahasiswa perantauan.
3. **Aksi konkret** → mentoring intensif semester 1–2 untuk kelompok risiko
   tinggi; program bridging untuk lulusan non-SMK di prodi teknik; cek rutin
   engagement akademik awal (kehadiran, tugas).

⚠️ **Batasan model:** data sintetis dengan pola terdesain — di dunia nyata,
faktor ekonomi, kesehatan, dan sosial (yang tidak tercatat di sini) ikut menentukan
dropout. Model ini demonstrasi *pendekatan*, bukan sistem produksi."""))

nb.cells = cells
nbf.write(nb, "notebooks/02_statistik_dan_model_dropout.ipynb")
print("Notebook 02 dibuat")
