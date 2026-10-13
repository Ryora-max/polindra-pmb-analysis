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
│   └── 01_analisis_pmb_polindra.ipynb   # EDA lengkap + insight bisnis
├── dashboard/
│   └── app.py             # Dashboard interaktif Streamlit + Plotly
├── src/
│   ├── generate_data.py   # Generator dataset sintetis (reproducible, seed=42)
│   ├── db_setup.py        # Loader CSV → SQLite
│   └── make_notebook.py   # Builder notebook via nbformat
└── outputs/figures/       # Grafik hasil analisis
```

## Dataset

| Tabel | Baris | Isi |
|---|---|---|
| `pendaftar` | ~17.900 | funnel: jalur masuk, pilihan prodi, demografi, skor seleksi, status |
| `mahasiswa` | ~6.300 | subset yang registrasi: NIM, angkatan, prodi, IPK, status akademik |

Mencakup 11 prodi riil Polindra (3 jurusan: Teknik Informatika, Teknik,
Kesehatan), jalur masuk SNMPN/SBMPN/Mandiri/Prestasi dengan kuota seleksi
terpisah, serta demografi Ciayumajakuning.

## Cara Menjalankan

```bash
pip install -r requirements.txt

# (opsional) regenerasi dataset & database
python src/generate_data.py
python src/db_setup.py

# jalankan dashboard
streamlit run dashboard/app.py

# atau buka notebook langsung (output sudah ter-execute)
notebooks/01_analisis_pmb_polindra.ipynb
```

## Temuan Utama

- **Demand naik ~170%** dalam 6 tahun; lonjakan mulai 2022 berbarengan dengan
  pembukaan prodi S1 Terapan baru (SIKC, Elektro-Medis, Instrumen & Kontrol).
- **Prodi Teknik Informatika & Kesehatan paling diminati** — daya tampung sama
  tetapi peminat jauh lebih besar → tingkat diterima rendah.
- **Jalur Mandiri punya leakage daftar ulang tertinggi** (~22% lulus tidak jadi
  registrasi) — peluang perbaikan *yield* via follow-up aktif pendaftar.
- **Mahasiswa jalur SNMPN mencatat IPK tertinggi** — nilai rapor terbukti
  prediktor performa akademik yang baik.
- **Polindra sangat lokal**: mayoritas mahasiswa dari Indramayu &
  Ciayumajakuning — peluang diversifikasi geografis.

## Tech Stack

`Python` `pandas` `NumPy` `SQL (SQLite)` `Matplotlib/Seaborn` `Plotly` `Streamlit` `Jupyter`

---
*Dibuat untuk portofolio Data Analyst.*
