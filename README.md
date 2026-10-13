# Analisis Penerimaan Mahasiswa Baru — Politeknik Negeri Indramayu

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
├── data/raw/              # Dataset CSV (pendaftar, mahasiswa)
├── database/
│   ├── polindra.db        # SQLite — 2 tabel relasional (JOIN by id_pendaftar)
│   └── queries.sql        # Kumpulan query analisis (tren, funnel, retensi)
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
| `pendaftar` | ~17.900 | funnel: jalur masuk, pilihan prodi, demografi, skor seleksi, status |
| `mahasiswa` | ~6.300 | subset yang registrasi: NIM, angkatan, prodi, IPK, status akademik |

Mencakup 11 prodi riil Polindra (3 jurusan: Teknik Informatika, Teknik,
Kesehatan), jalur masuk yang meniru kebijakan nyata — **SNMPN/SBMPN/Mandiri/
Prestasi (2019–2023)** bertransisi ke **SNBP/SNBT/Mandiri (2024–2025)**
mengikuti Permendikbudristek 48/2022 — dengan kuota seleksi terpisah per
jalur, serta demografi Ciayumajakuning (BPS).

Dokumentasi:
- � [`docs/EXECUTIVE_REPORT.md`](docs/EXECUTIVE_REPORT.md) — laporan eksekutif: temuan → rekomendasi
- �📖 [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) — penjelasan tiap kolom & asumsi pemodelan
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

## Temuan Utama

- **Demand naik ~170%** dalam 6 tahun; lonjakan mulai 2022 berbarengan dengan
  pembukaan prodi S1 Terapan baru (SIKC, Elektro-Medis, Instrumen & Kontrol).
- **Seleksi makin kompetitif**: persentase lulus seleksi turun dari ~58% (2019)
  ke ~32% (2025) — peminat tumbuh jauh lebih cepat dari daya tampung.
- **Prodi Teknik Informatika & Kesehatan paling diminati** — daya tampung sama
  tetapi peminat jauh lebih besar → tingkat diterima rendah.
- **Jalur Mandiri punya leakage daftar ulang tertinggi** (~22% lulus tidak jadi
  registrasi) — peluang perbaikan *yield* via follow-up aktif pendaftar.
- **Mahasiswa jalur SNMPN mencatat IPK tertinggi** — nilai rapor terbukti
  prediktor performa akademik yang baik.
- **Dropout terkonsentrasi di 2 tahun pertama** masa studi — periode kritis
  untuk program early-warning & mentoring.
- **Polindra sangat lokal**: mayoritas mahasiswa dari Indramayu &
  Ciayumajakuning — peluang diversifikasi geografis.

## Tech Stack

`Python` `pandas` `NumPy` `SQL (SQLite)` `SciPy` `statsmodels` `Matplotlib/Seaborn` `Plotly` `Streamlit` `Jupyter`

---
*Dibuat untuk portofolio Data Analyst.*
