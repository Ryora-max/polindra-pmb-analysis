# Analisis Penerimaan Mahasiswa Baru — Politeknik Negeri Indramayu

![Python](https://img.shields.io/badge/Python-3.12-2563EB)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B)
![pandas](https://img.shields.io/badge/pandas-EDA-150458)
![scikit--learn](https://img.shields.io/badge/scikit--learn-Modeling-F7931E)
![License](https://img.shields.io/badge/License-MIT-green)

Portfolio project **data analyst end-to-end**: simulasi funnel penerimaan mahasiswa baru (PMB)
Polindra 2019–2025, dari pendaftaran → seleksi → registrasi → performa akademik.

> **Disclaimer:** Seluruh data bersifat **sintetis** (hasil simulasi terprogram),
> bukan data riil Polindra. Struktur prodi/jurusan mengacu pada informasi publik
> di [polindra.ac.id](https://polindra.ac.id). Tujuan project: demonstrasi
> workflow analisis data pada konteks dunia nyata.

## Pertanyaan Bisnis

1. Bagaimana tren peminat Polindra 2019–2025, dan apa pendorongnya?
2. Prodi mana yang paling diminati dan paling kompetitif?
3. Jalur masuk (SNMPN/SBMPN/Mandiri/Prestasi) mana yang paling efektif
   menghasilkan mahasiswa baru — dan mana yang paling banyak *leakage*?
4. Bagaimana profil demografi mahasiswa (domisili, jenis sekolah, gender)?
5. Bagaimana performa akademik (IPK) dan retensi (dropout) antar prodi & jalur?

## Struktur Project

```
├── data/raw/              # Dataset CSV (pendaftar, mahasiswa, khs)
├── database/
│   ├── polindra.db        # SQLite — 3 tabel relasional (pendaftar→mahasiswa→khs)
│   └── queries.sql        # 10 query analisis (tren, funnel, retensi, kanal, trajektori)
├── notebooks/
│   ├── 01_analisis_pmb_polindra.ipynb        # EDA lengkap + insight bisnis
│   └── 02_statistik_dan_model_dropout.ipynb  # uji hipotesis + regresi logistik
├── dashboard/
│   └── app.py             # Dashboard interaktif Streamlit + Plotly
├── src/
│   ├── generate_data.py   # Generator dataset sintetis (reproducible, seed=42)
│   ├── db_setup.py        # Loader CSV → SQLite
│   ├── run_sql_analysis.py# Eksekusi semua query.sql → export CSV per hasil
│   ├── validate_data.py   # 17 data-quality checks (assertion pipeline)
│   ├── make_notebook.py   # Builder notebook 01 via nbformat
│   └── make_notebook2.py  # Builder notebook 02 via nbformat
└── outputs/
    ├── figures/           # Grafik hasil analisis
    └── sql_results/       # Output CSV dari tiap query SQL
```

## Dataset

| Tabel | Baris | Isi |
|---|---|---|
| `pendaftar` | ~17.900 | funnel: jalur masuk, kanal akuisisi, pilihan prodi, demografi, skor, status |
| `mahasiswa` | ~6.300 | subset yang registrasi: NIM, angkatan, prodi, IPK, status akademik |
| `khs` | ~27.000 | IP + SKS per semester per mahasiswa — analisis longitudinal |

Mencakup 11 prodi riil Polindra (3 jurusan: Teknik Informatika, Teknik,
Kesehatan), jalur masuk yang meniru kebijakan nyata — **SNMPN/SBMPN/Mandiri/
Prestasi (2019–2023)** bertransisi ke **SNBP/SNBT/Mandiri (2024–2025)**
mengikuti Permendikbudristek 48/2022 — dengan kuota seleksi terpisah per
jalur, serta demografi Ciayumajakuning (BPS).

Dokumentasi:
- 📋 [`docs/EXECUTIVE_REPORT.md`](docs/EXECUTIVE_REPORT.md) — laporan eksekutif: temuan → rekomendasi
- 📖 [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) — penjelasan tiap kolom & asumsi pemodelan
- 🔗 [`docs/SUMBER_DATA.md`](docs/SUMBER_DATA.md) — semua sumber riil: polindra.ac.id, PDDikti, SNPMB, BPS, beserta angka peminat riil SNBT 2025 yang dipakai untuk kalibrasi

## Cara Menjalankan

```bash
pip install -r requirements.txt

# (opsional) regenerasi dataset & database
python src/generate_data.py
python src/db_setup.py

# (opsional) jalankan seluruh analisis SQL → outputs/sql_results/
python src/run_sql_analysis.py

# (opsional) validasi kualitas data — 17 checks
python src/validate_data.py

# jalankan dashboard
streamlit run dashboard/app.py

# atau buka notebook langsung (output sudah ter-execute)
notebooks/01_analisis_pmb_polindra.ipynb
```

## Temuan Utama (fakta → implikasi)

> Seluruh angka dihitung otomatis (`python src/key_metrics.py` →
> `outputs/key_metrics.md`). Data sintetis: hubungan antar variabel adalah
> asumsi pemodelan; yang ditunjukkan adalah kemampuan analisis
> mengkuantifikasinya secara jujur.

- **Pendaftar +171% (1.400→3.800), kursi lulus hanya +50% (808→1.214, datar
  sejak 2023)** → keketatan turun dari 57,7% ke 31,9%; masalahnya
  *over-subscription*, bukan kurang peminat.
- **D3 Keperawatan (885) & D3 Teknik Informatika (775) peminat terbanyak**
  dengan tingkat diterima 33% & 30% → kandidat ekspansi kuota.
- **Jalur Mandiri: yield 77,4% vs 88–89% jalur lain** (leakage 22,6%) →
  follow-up aktif pasca-pengumuman lebih murah daripada menambah pendaftar.
- **Jalur masuk signifikan memengaruhi IPK, tetapi efeknya sangat kecil**
  (ANOVA p=1,5e-14, η²=0,012 — hanya ±1% variasi) → *signifikan ≠ penting*.
- **65% mahasiswa DO berhenti dalam 2 semester pertama; IP semester 1
  prediktor terkuat** (OR 0,22 per +1 poin; RF ROC-AUC 0,62 ± 0,02, 5-fold
  CV) → aturan flag **IP sem-1 < 3,0**: ±19% mahasiswa ter-flag, ±33% calon DO
  tertangkap (lift 1,7×). Ambang 2,5 terlalu ketat (recall 5%). Sinyal
  moderat — untuk memprioritaskan pembinaan, bukan memvonis individu.
- **TikTok/IG: volume terbesar (5.949) tapi konversi terendah (32,5% vs
  37,9% Alumni/Keluarga)** → ukur *cost per mahasiswa terdaftar*.
- **Polindra sangat lokal** (Kab. Indramayu 34,4%; Ciayumajakuning 68%) →
  konsentrasi geografis = risiko demografis; ekspansi di luar kawasan
  adalah tuas pertumbuhan berikutnya.

## Pendekatan analitis (apa yang ditunjukkan project ini)

Deskriptif (funnel, cohort, demografi) → **inferensial** (chi-square,
ANOVA, effect size — bukan cuma "terlihat beda") → **prediktif**
(Random Forest + threshold tuning: trade-off recall/precision sebagai
keputusan bisnis) → **segmentasi** (K-Means persona) → **peramalan**
(OLS + interval 90%). Semua insight di dashboard dihitung **dinamis
dari data terfilter** — tidak ada angka hardcode. Kualitas data dijaga
**23 assertion checks** otomatis.

## Tech Stack

`Python` `pandas` `NumPy` `SQL (SQLite)` `SciPy` `statsmodels` `Matplotlib/Seaborn` `Plotly` `Streamlit` `Jupyter`

---
*Dibuat untuk portofolio Data Analyst.*
