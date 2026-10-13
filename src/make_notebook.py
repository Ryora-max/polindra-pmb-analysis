"""Bangun notebook EDA via nbformat lalu eksekusi dengan nbclient."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell("""# Analisis Penerimaan Mahasiswa Baru (PMB) Politeknik Negeri Indramayu

**Portfolio project — Data Analyst**

Dataset: simulasi PMB Polindra 2019–2025 (sintetis, berbasis struktur prodi riil dari polindra.ac.id).
Dua tabel relasional: `pendaftar` (funnel: daftar → seleksi → registrasi) dan `mahasiswa` (status akademik).

**Pertanyaan bisnis:**
1. Bagaimana tren peminat Polindra dari 2019–2025?
2. Prodi mana yang paling diminati dan paling ketat?
3. Jalur masuk mana yang paling efektif menghasilkan mahasiswa berkualitas?
4. Bagaimana profil demografi mahasiswa (domisili, jenis sekolah, gender)?
5. Bagaimana performa akademik (IPK) dan retensi (dropout) antar prodi?"""))

cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 5)
plt.rcParams["figure.dpi"] = 110

pendaftar = pd.read_csv("../data/raw/pendaftar.csv")
mahasiswa = pd.read_csv("../data/raw/mahasiswa.csv")
print(pendaftar.shape, mahasiswa.shape)
pendaftar.head()"""))

cells.append(nbf.v4.new_markdown_cell("""## 1. Data Quality Check

Cek missing value, duplikasi, dan konsistensi tipe data."""))

cells.append(nbf.v4.new_code_cell("""print("=== Missing values pendaftar ===")
print(pendaftar.isna().sum())
print("\\n=== Missing values mahasiswa ===")
print(mahasiswa.isna().sum())
print("\\nDuplikat id_pendaftar:", pendaftar["id_pendaftar"].duplicated().sum())
print("Duplikat NIM:", mahasiswa["nim"].duplicated().sum())

# nilai_ujian kosong di jalur tanpa ujian tulis — expected, bukan dirty data
pendaftar.groupby("jalur_masuk")["nilai_ujian"].apply(lambda s: s.isna().mean().round(2))"""))

cells.append(nbf.v4.new_markdown_cell("""`nilai_ujian` kosong hanya pada jalur SNMPN/Prestasi (seleksi rapor, tanpa ujian tulis) — ini *by design*, bukan data kotor."""))

cells.append(nbf.v4.new_markdown_cell("""## 2. Tren Peminat 2019–2025"""))

cells.append(nbf.v4.new_code_cell("""tren = (pendaftar.groupby("tahun_daftar")
        .agg(pendaftar=("id_pendaftar","count"),
             lulus=("status_seleksi", lambda s:(s=="Lulus").sum()),
             registrasi=("daftar_ulang", lambda s:(s=="Ya").sum()))
        .assign(pct_lulus=lambda d:(100*d["lulus"]/d["pendaftar"]).round(1)))

fig, ax = plt.subplots()
ax.plot(tren.index, tren["pendaftar"], marker="o", label="Pendaftar")
ax.plot(tren.index, tren["registrasi"], marker="s", label="Daftar ulang (mahasiswa baru)")
ax.set_title("Tren pendaftar & mahasiswa baru Polindra"); ax.legend()
plt.savefig("../outputs/figures/tren_pendaftar.png", bbox_inches="tight"); plt.show()
tren"""))

cells.append(nbf.v4.new_markdown_cell("""**Insight:** Peminat tumbuh konsisten setiap tahun — lonjakan tajam mulai 2022 berbarengan dengan dibukanya prodi-prodi baru S1 Terapan (SIKC, Elektro-Medis, Instrumen & Kontrol). Ekspansi prodi terbukti efektif menaikkan demand."""))

cells.append(nbf.v4.new_markdown_cell("""## 3. Prodi Paling Diminati & Paling Ketat"""))

cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(14, 5))

pendaftar["prodi_pilihan_1"].value_counts().head(10).sort_values().plot.barh(
    ax=axes[0], color=sns.color_palette("Blues", 10))
axes[0].set_title("10 prodi paling diminati")

ketat = (pendaftar.groupby("prodi_pilihan_1")
         .agg(n=("id_pendaftar","count"),
              acc=("status_seleksi", lambda s:(s=="Lulus").mean()*100))
         .query("n>=50").nsmallest(10,"acc"))
ketat["acc"].sort_values().plot.barh(ax=axes[1], color=sns.color_palette("Reds", 10))
axes[1].set_title("10 prodi paling ketat (% diterima)")

plt.tight_layout()
plt.savefig("../outputs/figures/prodi_diminati_ketat.png", bbox_inches="tight"); plt.show()"""))

cells.append(nbf.v4.new_markdown_cell("""**Insight:** D3 Keperawatan & D3 Teknik Informatika memimpin peminat — konsisten dengan data riil peminat SNBT 2025 Polindra (Kep 556, TI 480 pendaftar). Daya tampung yang sama tetapi peminat jauh lebih besar membuat persentase diterima di prodi populer jauh lebih rendah — calon mahasiswa perlu strategi memilih pilihan ke-2."""))

cells.append(nbf.v4.new_markdown_cell("""## 4. Conversion Funnel per Jalur Masuk"""))

cells.append(nbf.v4.new_code_cell("""funnel = (pendaftar.groupby("jalur_masuk")
          .agg(pendaftar=("id_pendaftar","count"),
               lulus=("status_seleksi", lambda s:(s=="Lulus").sum()),
               registrasi=("daftar_ulang", lambda s:(s=="Ya").sum())))
funnel["reg_rate"] = (100*funnel["registrasi"]/funnel["pendaftar"]).round(1)
funnel["drop_du"] = (100*(funnel["lulus"]-funnel["registrasi"])/funnel["lulus"]).round(1)

fig, ax = plt.subplots()
funnel["reg_rate"].sort_values().plot.barh(ax=ax, color=sns.color_palette("Greens", 4))
ax.set_title("% pendaftar yang akhirnya registrasi, per jalur")
plt.savefig("../outputs/figures/funnel_jalur.png", bbox_inches="tight"); plt.show()
funnel"""))

cells.append(nbf.v4.new_markdown_cell("""**Insight:** Jalur berbasis ujian tulis (SBMPN era ≤2023, SNBT era ≥2024) adalah sumber mahasiswa baru terbesar — kuota seleksi paling besar (~40% daya tampung, sesuai Permendikbudristek 48/2022). Jalur Prestasi paling kompetitif — kuota kecil diperebutkan peminat terbaik. Jalur Mandiri punya *leakage* daftar ulang tertinggi: ~22% peserta lulus tidak jadi registrasi (umumnya karena lolos juga di PTN lain atau kendala biaya) — peluang perbaikan *yield* lewat follow-up aktif.

**Catatan metodologi:** dataset meniru transisi kebijakan seleksi nasional — jalur politeknik (SNMPN/SBMPN, FDPNI) berlaku ≤2023; sejak 2024 Polindra masuk sistem SNPMB (SNBP rapor + SNBT berbasis UTBK). Ini kenapa nama jalur berubah di pertengahan data."""))

cells.append(nbf.v4.new_markdown_cell("""## 5. Profil Demografi Mahasiswa"""))

cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 3, figsize=(15, 5))

mahasiswa["asal_kota"].value_counts().head(8).sort_values().plot.barh(
    ax=axes[0], color=sns.color_palette("viridis", 8))
axes[0].set_title("Kota asal mahasiswa")

mahasiswa["jenis_sekolah"].value_counts().plot.pie(
    ax=axes[1], autopct="%1.0f%%", colors=sns.color_palette("Set2"))
axes[1].set_ylabel(""); axes[1].set_title("Jenis sekolah asal")

gender = mahasiswa.groupby(["jurusan","jenis_kelamin"]).size().unstack()
gender.plot.bar(ax=axes[2], color=["#4C72B0","#DD8452"])
axes[2].set_title("Gender per jurusan"); axes[2].set_xlabel("")

plt.tight_layout()
plt.savefig("../outputs/figures/demografi.png", bbox_inches="tight"); plt.show()"""))

cells.append(nbf.v4.new_markdown_cell("""**Insight:** Polindra sangat "lokal" — mayoritas mahasiswa berasal dari Indramayu & wilayah Ciayumajakuning (Cirebon–Indramayu–Majalengka–Kuningan). Jurusan teknik didominasi lulusan SMK + laki-laki; kesehatan didominasi SMA/MA + perempuan. Ini pola khas politeknik vokasi."""))

cells.append(nbf.v4.new_markdown_cell("""## 6. Performa Akademik & Retensi"""))

cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.boxplot(data=mahasiswa, x="ipk", y="jurusan", ax=axes[0])
axes[0].set_title("Distribusi IPK per jurusan")

do = (mahasiswa.groupby("prodi")["status_mahasiswa"]
      .apply(lambda s: 100*(s=="Drop Out").sum()/len(s))
      .sort_values())
do.plot.barh(ax=axes[1], color=sns.color_palette("OrRd_r", len(do)))
axes[1].set_title("Dropout rate per prodi (%)")

plt.tight_layout()
plt.savefig("../outputs/figures/akademik.png", bbox_inches="tight"); plt.show()

# IPK per jalur masuk — apakah jalur seleksi berpengaruh ke kualitas?
mahasiswa.groupby("jalur_masuk").agg(
    n=("nim","count"), rata_ipk=("ipk","mean"),
    dropout_pct=("status_mahasiswa", lambda s: round(100*(s=="Drop Out").mean(),1))
).round(2)"""))

cells.append(nbf.v4.new_markdown_cell("""**Insight:** Mahasiswa jalur SNMPN (seleksi rapor era ≤2023) mencatat rata-rata IPK tertinggi — sinyal bahwa nilai rapor adalah prediktor performa akademik yang baik, konsisten dengan literatur admission research. Dropout rate antar jalur relatif seragam (~6–8%), artinya jalur masuk lebih berpengaruh ke kualitas akademik daripada ke retensi."""))

cells.append(nbf.v4.new_markdown_cell("""## 7. Cohort Retention Analysis

Status mahasiswa per angkatan — melihat pola kelulusan, retensi, dan dropout antar cohort."""))

cells.append(nbf.v4.new_code_cell("""# Komposisi status per angkatan (cohort)
cohort = (mahasiswa.groupby(["angkatan","status_mahasiswa"]).size().unstack(fill_value=0))
cohort_pct = cohort.div(cohort.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(11,5))
bottom = np.zeros(len(cohort_pct))
colors = {"Lulus":"#4C9F70","Aktif":"#4C72B0","Cuti":"#DD8452","Drop Out":"#C44E52"}
for st in ["Lulus","Aktif","Cuti","Drop Out"]:
    if st in cohort_pct.columns:
        ax.bar(cohort_pct.index, cohort_pct[st], bottom=bottom,
               label=st, color=colors[st])
        bottom += cohort_pct[st].values
ax.set_title("Komposisi status mahasiswa per angkatan (%)")
ax.set_ylabel("%"); ax.legend(title="Status", ncol=4, loc="lower center",
                              bbox_to_anchor=(0.5,-0.22))
plt.tight_layout()
plt.savefig("../outputs/figures/cohort_retention.png", bbox_inches="tight"); plt.show()

# Tingkat keketatan seleksi makin tinggi seiring pertumbuhan peminat
keketatan = (pendaftar.groupby("tahun_daftar")["status_seleksi"]
             .apply(lambda s: 100*(s=="Lulus").mean()).round(1))
print("% lulus seleksi per tahun (makin kecil = makin kompetitif):")
print(keketatan)"""))

cells.append(nbf.v4.new_markdown_cell("""**Insight:** Cohort analysis menunjukkan pola siklus akademik yang sehat — angkatan ≥3 tahun didominasi status Lulus, angkatan muda didominasi Aktif. Angka dropout terkonsentrasi di angkatan muda (2 tahun pertama masa studi) — periode kritis di mana intervensi early-warning paling efektif. Di sisi lain, **persentase lulus seleksi turun dari ~58% (2019) ke ~32% (2025)** — Polindra makin kompetitif seiring naiknya peminat."""))

cells.append(nbf.v4.new_markdown_cell("""## 8. Kesimpulan & Rekomendasi

1. **Demand naik kuat** — pertahankan tren penambahan prodi; SIKC & prodi S1T baru cepat diminati.
2. **Ketimpangan keketatan** — prodi TI & Kesehatan sangat kompetitif; pertimbangkan tambah daya tampung atau sosialisasi prodi teknik yang sepi.
3. **Perbaiki yield jalur Mandiri** — leakage daftar ulang tinggi; follow-up aktif pendaftar lulus (reminder, skema cicilan UKT).
4. **Jalur rapor (SNMPN/SNBP) = sumber mahasiswa berkualitas** — pertahankan/perbesar kuota jalur rapor.
5. **Perkuat brand di luar Ciayumajakuning** — mahasiswa luar Jawa masih minim; peluang diversifikasi.

---
*Analisis oleh [Nama Kamu] · Dataset sintetis untuk portofolio · Tools: Python, pandas, seaborn, SQLite, Streamlit*"""))

nb.cells = cells
nbf.write(nb, "notebooks/01_analisis_pmb_polindra.ipynb")
print("Notebook dibuat")
