# Data Dictionary — Dataset PMB Polindra (Sintetis)

Dokumen ini menjelaskan setiap kolom, asumsi pemodelan, dan cara membaca dataset.
**Semua data SINTETIS** — dihasilkan oleh `src/generate_data.py` dengan `seed=42`
(reproducible), menggunakan struktur prodi & konteks riil Polindra.

---

## Tabel 1: `pendaftar` — Funnel Seleksi (17.900 baris)

Satu baris = satu calon mahasiswa yang mendaftar.

| Kolom | Tipe | Penjelasan |
|---|---|---|
| `id_pendaftar` | string | ID unik, format `PMB<ta_hun><5_digit>`. Primary key, dipakai JOIN ke tabel mahasiswa. |
| `tahun_daftar` | int | Tahun pendaftaran 2019–2025. Volume tumbuh: 1.400 → 3.800/tahun. |
| `jalur_masuk` | kategori | Meniru kebijakan nyata: era **2019–2023** → SNMPN (rapor, ~35%), SBMPN (ujian, ~35%), Mandiri (~25%), Prestasi (~5%). Era **2024–2025** → SNBP (rapor, ~30%), SNBT (UTBK, ~42%), Mandiri (~26%), Prestasi (~2%) — sesuai Permendikbudristek 48/2022. |
| `prodi_pilihan_1` | kategori | Prodi pilihan utama (11 prodi riil Polindra). |
| `prodi_pilihan_2` | kategori | Prodi cadangan; 70% peluang masih dalam jurusan yang sama. |
| `jurusan` | kategori | Teknik Informatika / Teknik / Kesehatan — turunan dari prodi. |
| `jenis_kelamin` | kategori | `L`/`P`. Proporsi per jurusan: TI 62% L, Teknik 85% L, Kesehatan 80% P. |
| `asal_kota` | kategori | Domisili. Indramayu 34%, sisanya Ciayumajakuning & sekitarnya. |
| `jenis_sekolah` | kategori | SMA / SMK / MA / Lainnya. SMK dominan di teknik (~55–60%), SMA/MA dominan di Kesehatan (~93%). |
| `sumber_informasi` | kategori | Kanal akuisisi: TikTok/IG (naik 10%→46%), Guru BK, Alumni/Keluarga, Website, Pameran Kampus, Teman. Tren per tahun berubah realistis. |
| `nilai_rapor` | float | Rerata rapor, distribusi normal μ=80, σ=5, rentang 65–98. |
| `nilai_ujian` | float | Hanya ada di jalur berbasis tes (SBMPN, SNBT, Mandiri). `NaN` di jalur rapor (SNMPN, SNBP, Prestasi) = **by design**, bukan data kotor. |
| `skor_seleksi` | float | `0.6×rapor + 0.4×ujian` (+3 bonus SMK di teknik, +3 bonus SMA/MA di kesehatan). |
| `status_seleksi` | kategori | `Lulus` / `Tidak Lulus`. Ditentukan per **prodi × tahun × jalur** — tiap jalur punya kuota sendiri. Era ≤2023: SNMPN 30%, SBMPN 40%, Mandiri 27%, Prestasi 3%. Era ≥2024: SNBP 20%, SNBT 40%, Mandiri 38%, Prestasi 2% (mengikuti Permendikbudristek 48/2022: SNBT min. 40% daya tampung). |
| `prodi_diterima` | kategori | Prodi yang menerima (bisa pilihan 1 atau 2). `NA` jika tidak lulus. |
| `daftar_ulang` | kategori | `Ya` = jadi mahasiswa. 88% untuk SNMPN/SBMPN/Prestasi, **78% Mandiri** (leakage lebih tinggi). |

## Tabel 2: `mahasiswa` — Akademik (6.264 baris)

Satu baris = satu mahasiswa (pendaftar yang lulus + daftar ulang). Relasi: `mahasiswa.id_pendaftar → pendaftar.id_pendaftar`.

| Kolom | Tipe | Penjelasan |
|---|---|---|
| `nim` | string | Nomor induk mahasiswa (sintetis). |
| `id_pendaftar` | string | Foreign key ke tabel `pendaftar`. |
| `angkatan` | int | = `tahun_daftar`. |
| `prodi` / `jurusan` | kategori | Prodi tempat diterima. |
| `jenis_kelamin`, `asal_kota`, `jenis_sekolah`, `jalur_masuk` | kategori | Diwarisi dari tabel pendaftar. |
| `beasiswa_kip` | kategori | KIP-Kuliah: ~15% dari Indramayu, ~25% dari luar kota (lebih banyak mahasiswa perantau). |
| `ipk` | float | Normal per jurusan: TI μ=3.35, Teknik μ=3.15, Kesehatan μ=3.45. Bonus +0.08 penerima KIP, +0.05 jalur rapor (SNMPN/SNBP); lulusan tepat waktu +0.15; Drop Out −0.6. |
| `status_mahasiswa` | kategori | `Lulus` / `Aktif` / `Cuti` / `Drop Out`. Bergantung usia angkatan: cohort ≥3(D3)/≥4(S1T) tahun dominan Lulus; DO terkonsentrasi di 2 tahun pertama. |

## Tabel 3: `khs` — Transkrip per Semester (longitudinal)

Satu baris = satu semester mahasiswa. Relasi: `khs.nim → mahasiswa.nim`.

| Kolom | Tipe | Penjelasan |
|---|---|---|
| `nim` | string | Foreign key ke tabel mahasiswa. |
| `semester` | int | Semester ke-1..6 (D3) atau 1..8 (S1T); DO berhenti di smt 1–4. |
| `ip_semester` | float | Indeks prestasi semester tsb. Lulus: naik tipis. DO: menurun tajam. Aktif/Cuti: fluktuatif di sekitar IPK. |
| `sks_ambil` | int | SKS diambil semester itu (18–24; DO cenderung lebih rendah). |

## Referensi Prodi (struktur riil Polindra)

| Prodi | Jenjang | Jurusan | Buka | Daya tampung/thn (asumsi) |
|---|---|---|---|---|
| Teknik Informatika | D3 | Teknik Informatika | 2015 | 96 |
| Rekayasa Perangkat Lunak | S1T | Teknik Informatika | 2016 | 96 |
| Sistem Informasi Kota Cerdas | S1T | Teknik Informatika | 2022 | 48 |
| Teknologi Rekayasa Komputer | S1T | Teknik Informatika | 2023 | 48 |
| Teknik Mesin | D3 | Teknik | 2015 | 64 |
| Teknik Pendingin & Tata Udara | D3 | Teknik | 2015 | 48 |
| Perancangan Manufaktur | S1T | Teknik | 2016 | 48 |
| Teknologi Rekayasa Instrumen & Kontrol | S1T | Teknik | 2022 | 48 |
| Keperawatan | D3 | Kesehatan | 2016 | 96 |
| Teknologi Laboratorium Medis | S1T | Kesehatan | 2020 | 48 |
| Teknologi Rekayasa Elektro-Medis | S1T | Kesehatan | 2022 | 32 |

*Sumber struktur prodi: polindra.ac.id & Wikipedia. Lihat `docs/SUMBER_DATA.md` untuk tautan lengkap.*

## Catatan Metodologi

- **Seleksi per kuota jalur** meniru dunia nyata: SNMPN/SBMPN/Mandiri adalah gelombang terpisah dengan kuota sendiri, bukan satu seleksi gabungan.
- **Skala nilai**: rapor & ujian 0–100, IPK 0–4.
- **Relasi**: `pendaftar (1) — (0..1) mahasiswa`; setiap mahasiswa pasti ada di tabel pendaftar.
- **Keterbatasan**: tidak ada data biaya/UKT, prestige sekolah, atau pendapatan orang tua — dropout dimodelkan secara agregat.
