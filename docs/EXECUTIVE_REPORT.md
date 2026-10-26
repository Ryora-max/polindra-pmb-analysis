# Laporan Eksekutif — Analisis PMB Politeknik Negeri Indramayu

**Periode data:** 2019–2025 · **Status:** dataset sintetis terkalibrasi (bukan data riil)
**Audiens:** manajemen PMB / pimpinan politeknik · **Analis:** [Nama Kamu]

---

## Ringkasan Eksekutif

Peminat Polindra tumbuh **~170%** dalam 6 tahun (1.400 → 3.800 pendaftar/tahun),
tetapi daya tampung nyaris tidak berubah — akibatnya tingkat kelulusan seleksi
turun dari **58% (2019) menjadi 32% (2025)**. Kampus makin kompetitif dan
selektif, namun efisiensi konversi dan retensi masih menyisakan ruang perbaikan,
terutama pada jalur Mandiri (leakage daftar ulang ~22%) dan intervensi mahasiswa
berisiko dropout pada 2 tahun pertama studi.

## Temuan Utama (evidence-based)

| # | Temuan | Data pendukung |
|---|---|---|
| 1 | Demand naik 2,7×; seleksi makin ketat | Pendaftar 1.400→3.800/thn; % lulus 58%→32% |
| 2 | Lonjakan demand berkorelasi dengan pembukaan prodi S1 Terapan baru (2022+) | Heatmap peminat prodi × tahun |
| 3 | D3 Keperawatan & D3 Teknik Informatika = prodi unggulan | Peminat tertinggi, tingkat diterima terendah — konsisten dgn angka riil SNBT 2025 |
| 4 | Jalur ujian tulis (SBMPN/SNBT) menyumbang mahasiswa terbanyak | Kuota seleksi ~40% daya tampung |
| 5 | Jalur Mandiri: yield terendah | ~22% lulusan tidak jadi registrasi |
| 6 | Domisili sangat terkonsentrasi | Kab. Indramayu ≈33% mahasiswa; Ciayumajakuning ≈75% |
| 7 | Jalur rapor → IPK lebih tinggi | Mann-Whitney p<0.01, tetapi **Cohen's d = 0,07 → efek kecil** |
| 8 | Dropout terkonsentrasi di 2 tahun pertama & kelompok risiko spesifik | Regresi logistik: nilai rapor rendah + mismatch sekolah ↔ jurusan |

## Rekomendasi

1. **Ekspansi daya tampung selektif** pada prodi permintaan tinggi (Keperawatan,
   Teknik Informatika) — indikator kekuatan pasar paling jelas dalam data.
2. **Perbaiki yield jalur Mandiri**: follow-up aktif 7 hari pertama pasca
   pengumuman (call center/wa), opsi cicilan UKT — targetkan leakage turun ke <15%.
3. **Early-warning dropout**: terapkan skor risiko sederhana (model logistik,
   notebook 02) — fokuskan mentoring semester 1–2 pada 2 desil risiko teratas;
   program bridging untuk lulusan non-SMK di prodi teknik.
4. **Diversifikasi geografis**: kampanye sosialisasi di luar Ciayumajakuning
   (Subang–Karawang sudah muncul; potensi Brebes/Tegal di timur).
5. **Pantau komposisi jalur pasca-transisi SNPMB**: evaluasi kualitas SNBP vs
   SNBT tahunan — data menunjukkan jalur rapor menghasilkan IPK sedikit lebih
   tinggi (efek kecil namun signifikan).

## Metodologi Singkat

- **Data**: 17.900 pendaftar + 6.278 mahasiswa + 27.013 baris KHS
  (3 tabel relasional, SQLite).
- **Analisis**: funnel & cohort analysis (deskriptif), chi-square + Cramér's V,
  ANOVA, Mann-Whitney, korelasi Pearson/Spearman (inferensial), regresi
  logistik untuk faktor risiko dropout + Random Forest (pemodelan), K-Means
  segmentasi, forecast OLS, validasi lift per desil.
- **Tools**: Python (pandas, scipy, statsmodels, scikit-learn), SQL,
  Streamlit, Plotly.
- **Reproducibility**: generator ber-seed, validator data 23 checks, seluruh
  notebook ter-execute.

## Keterbatasan & Disclaimer

- Seluruh data **sintetis** — dikalibrasi ke statistik publik (SNPMB, BPS,
  polindra.ac.id) tetapi angka bukan data riil Polindra.
- Faktor ekonomi keluarga, prestasi non-akademik, dan kondisi individu tidak
  termodelkan; rekomendasi bersifat demonstrasi pendekatan analitis.

---
*Lampiran: notebook 01 (EDA), notebook 02 (statistik & model), dashboard Streamlit, `docs/DATA_DICTIONARY.md`, `docs/SUMBER_DATA.md`.*
