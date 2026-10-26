# Laporan Eksekutif — Analisis PMB Politeknik Negeri Indramayu

**Periode data:** 2019–2025 · **Status:** dataset sintetis terkalibrasi (bukan data riil)
**Audiens:** manajemen PMB / pimpinan politeknik · **Analis:** [Nama Kamu]
**Sumber angka:** `outputs/key_metrics.md` (dihitung otomatis oleh `src/key_metrics.py`)

---

## Ringkasan Eksekutif

Peminat Polindra tumbuh **171%** dalam 7 tahun (1.400 → 3.800 pendaftar/tahun),
sementara kursi yang diluluskan hanya naik **50%** (808 → 1.214, dan datar di
1.214 sejak 2023). Akibatnya tingkat kelulusan seleksi turun dari **57,7%
(2019) menjadi 31,9% (2025)**. Kampus makin selektif; ruang perbaikan ada pada
**yield jalur Mandiri** (22,6% yang lulus tidak mendaftar ulang vs ±11–12% di jalur
lain) dan pada **retensi dini**: 65% mahasiswa DO berhenti dalam 2 semester
pertama, dan IP semester 1 adalah sinyal terkuat.

## Temuan Utama (evidence-based)

| # | Temuan | Data pendukung |
|---|---|---|
| 1 | Demand naik 2,7× tetapi kursi lulus hanya +50% | Pendaftar 1.400→3.800; lulus 808→1.214 (datar sejak 2023); % lulus 57,7%→31,9% |
| 2 | Lonjakan demand sejalan dengan pembukaan prodi S1 Terapan (2022+) | Heatmap peminat prodi × tahun |
| 3 | D3 Keperawatan & D3 Teknik Informatika = peminat terbanyak | 885 & 775 peminat (pilihan 1, 2025); tingkat diterima 33,4% & 30,1% |
| 4 | **Yield jalur Mandiri terendah** | 77,4% registrasi vs 88,0–89,1% di jalur lain → 22,6% *leakage* |
| 5 | Domisili terkonsentrasi | Kab. Indramayu 34,4%; 5 wilayah Ciayumajakuning 68,0% |
| 6 | Efek jalur masuk pada IPK **signifikan tetapi sangat kecil** | ANOVA F=14,9, p=1,5e-14, **η²=0,012** (jalur menjelaskan ±1% variasi IPK); SNMPN 3,42 vs SNBT 3,28 |
| 7 | Dropout 7,2%; **65% terjadi dalam 2 semester pertama** | IP sem-1 rata-rata 3,15 (DO) vs 3,34 (non-DO) |
| 8 | **IP semester 1 = prediktor terkuat DO**; jenis sekolah & jurusan relevan, nilai rapor tidak signifikan setelah IP sem-1 dikontrol | Logit (p<0,05): OR IP sem-1 = 0,22 per +1 poin; MA 0,49 & SMK 0,55 relatif terhadap kategori "Lainnya" (n kecil, DO tinggi); Teknik 0,59 & TI 0,70 relatif terhadap Kesehatan |
| 9 | Kanal TikTok/Instagram: volume terbesar tetapi konversi terendah | 5.949 pendaftar, 32,5% vs Alumni/Keluarga 37,9% |

## Model early-warning — apa yang boleh diklaim

Random Forest (fitur akhir semester 1) mencapai **ROC-AUC 0,62 ± 0,02 (5-fold
CV)**: sinyal moderat, cocok untuk *memprioritaskan* pembinaan, bukan
memvonis individu. Trade-off ambang batas aturan sederhana "IP semester 1 < X"
(dari seluruh mahasiswa, DO base rate 7,2%):

| Ambang | % mahasiswa ter-flag | Recall DO | Precision | Lift vs acak |
|---|---|---|---|---|
| IP1 < 2,5 | 1% | 5% | 26,1% | 3,6× |
| **IP1 < 3,0** | **19%** | **33%** | 12,4% | **1,7×** |
| IP1 < 3,2 | 36% | 52% | 10,6% | 1,5× |

Ambang 2,5 terlalu ketat (nyaris tidak menangkap DO); 3,0 adalah titik
kompromi yang masuk akal bila kapasitas mentoring terbatas (±19% mahasiswa).
Precision rendah (±10–12%) adalah konsekuensi *base rate* DO yang kecil —
program pembinaan harus murah dan non-stigmatisasi.

## Rekomendasi

1. **Pertimbangkan ekspansi kursi selektif** di prodi peminat tinggi
   (Keperawatan, Teknik Informatika) — kursi lulus datar sejak 2023 sementara
   peminat terus naik; keputusan akhir bergantung kapasitas dosen/lab.
2. **Perbaiki yield jalur Mandiri**: follow-up aktif pasca pengumuman, opsi
   cicilan UKT — target leakage <15% (dari 22,6%).
3. **Early-warning dropout**: flag IP semester 1 < 3,0 (±19% mahasiswa,
   menangkap ±33% calon DO) untuk mentoring semester 2; evaluasi dampak
   dengan pembanding (A/B) sebelum diperluas.
4. **Alokasi promosi berbasis kualitas lead**: konversi TikTok/IG terendah
   — ukur *cost per mahasiswa terdaftar*, bukan jumlah pendaftar.
5. **Diversifikasi geografis**: 68% mahasiswa dari 5 wilayah Ciayumajakuning;
   Subang–Karawang mulai muncul.

## Metodologi

- **Data**: 17.900 pendaftar + 6.278 mahasiswa + 27.013 baris KHS
  (3 tabel relasional, SQLite); generator ber-seed (reprodusibel).
- **Analisis**: funnel & cohort (deskriptif); chi-square + Cramér's V, ANOVA
  + η², Mann-Whitney, korelasi (inferensial); regresi logistik (OR), Random
  Forest dengan cross-validation; K-Means; forecast OLS.
- **Validasi**: 23 data-quality checks lolos; notebook ter-execute.
- **Tools**: Python (pandas, scipy, statsmodels, scikit-learn), SQL, Streamlit, Plotly.

## Keterbatasan & Disclaimer

- Seluruh data **sintetis** — dikalibrasi ke statistik publik (SNPMB, BPS,
  polindra.ac.id) tetapi angka bukan data riil Polindra. Hubungan antar
  variabel adalah *asumsi pemodelan*; yang didemonstrasikan adalah
  kemampuan pipeline analisis memulihkan dan mengkuantifikasinya.
- Faktor ekonomi keluarga, prestasi non-akademik, dan kondisi individu tidak
  termodelkan; rekomendasi bersifat demonstrasi pendekatan analitis.

---
*Lampiran: notebook 01 (EDA), notebook 02 (statistik & model), dashboard Streamlit, `docs/DATA_DICTIONARY.md`, `docs/SUMBER_DATA.md`.*
