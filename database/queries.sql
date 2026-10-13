-- ============================================================
-- Analisis PMB Politeknik Negeri Indramayu — contoh query SQL
-- Database : SQLite (database/polindra.db)
-- Tabel    : pendaftar, mahasiswa
-- ============================================================

-- 1) Tren pendaftar & tingkat keketatan per tahun
SELECT
    tahun_daftar,
    COUNT(*)                                        AS total_pendaftar,
    SUM(CASE WHEN status_seleksi = 'Lulus' THEN 1 END) AS lulus_seleksi,
    ROUND(100.0 * SUM(CASE WHEN status_seleksi = 'Lulus' THEN 1 END)
          / COUNT(*), 1)                            AS persen_lulus,
    SUM(CASE WHEN daftar_ulang = 'Ya' THEN 1 END)   AS daftar_ulang
FROM pendaftar
GROUP BY tahun_daftar
ORDER BY tahun_daftar;

-- 2) Prodi paling diminati & paling ketat (2025)
SELECT
    prodi_pilihan_1                              AS prodi,
    COUNT(*)                                     AS peminat,
    SUM(CASE WHEN status_seleksi = 'Lulus' THEN 1 END) AS diterima,
    ROUND(100.0 * SUM(CASE WHEN status_seleksi = 'Lulus' THEN 1 END)
          / COUNT(*), 1)                         AS persen_diterima
FROM pendaftar
WHERE tahun_daftar = 2025
GROUP BY prodi_pilihan_1
ORDER BY peminat DESC;

-- 3) Conversion funnel per jalur masuk (2025)
SELECT
    jalur_masuk,
    COUNT(*)                                         AS pendaftar,
    SUM(CASE WHEN status_seleksi = 'Lulus' THEN 1 END)  AS lulus,
    SUM(CASE WHEN daftar_ulang = 'Ya' THEN 1 END)       AS registrasi,
    ROUND(100.0 * SUM(CASE WHEN daftar_ulang = 'Ya' THEN 1 END)
          / COUNT(*), 1)                             AS funnel_ke_mahasiswa_pct
FROM pendaftar
WHERE tahun_daftar = 2025
GROUP BY jalur_masuk
ORDER BY funnel_ke_mahasiswa_pct DESC;

-- 4) Rata-rata IPK per prodi per angkatan (JOIN dua tabel)
SELECT
    m.prodi,
    m.angkatan,
    COUNT(*)          AS jml_mahasiswa,
    ROUND(AVG(m.ipk), 2) AS rata_ipk,
    SUM(CASE WHEN m.status_mahasiswa = 'Drop Out' THEN 1 END) AS drop_out
FROM mahasiswa m
JOIN pendaftar p ON p.id_pendaftar = m.id_pendaftar
GROUP BY m.prodi, m.angkatan
ORDER BY m.prodi, m.angkatan;

-- 5) Sebaran domisili mahasiswa (top 10 kota asal)
SELECT
    asal_kota,
    COUNT(*) AS jml,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM mahasiswa), 1) AS persen
FROM mahasiswa
GROUP BY asal_kota
ORDER BY jml DESC
LIMIT 10;

-- 6) Retensi: dropout rate per jenis sekolah asal & jurusan
SELECT
    jurusan,
    jenis_sekolah,
    COUNT(*) AS jml_mahasiswa,
    ROUND(100.0 * SUM(CASE WHEN status_mahasiswa = 'Drop Out' THEN 1 END)
          / COUNT(*), 1) AS dropout_pct
FROM mahasiswa
GROUP BY jurusan, jenis_sekolah
ORDER BY jurusan, dropout_pct DESC;

-- 8) Efektivitas kanal marketing: pendaftar → registrasi per sumber informasi
SELECT
    sumber_informasi,
    COUNT(*)                                            AS pendaftar,
    SUM(CASE WHEN status_seleksi = 'Lulus' THEN 1 END)  AS lulus,
    SUM(CASE WHEN daftar_ulang = 'Ya' THEN 1 END)       AS registrasi,
    ROUND(100.0 * SUM(CASE WHEN daftar_ulang = 'Ya' THEN 1 END)
          / COUNT(*), 1)                                AS conversion_pct
FROM pendaftar
GROUP BY sumber_informasi
ORDER BY pendaftar DESC;

-- 9) Tren kanal marketing per tahun (siapa yang makin dominan?)
SELECT
    tahun_daftar,
    sumber_informasi,
    COUNT(*) AS pendaftar
FROM pendaftar
GROUP BY tahun_daftar, sumber_informasi
ORDER BY tahun_daftar, pendaftar DESC;

-- 10) Trajektori IP per semester per status mahasiswa (JOIN 3 tabel)
SELECT
    k.semester,
    m.status_mahasiswa,
    COUNT(*)        AS n,
    ROUND(AVG(k.ip_semester), 2) AS rata_ip,
    ROUND(AVG(k.sks_ambil), 1)   AS rata_sks
FROM khs k
JOIN mahasiswa m ON m.nim = k.nim
GROUP BY k.semester, m.status_mahasiswa
ORDER BY k.semester, m.status_mahasiswa;

-- 7) Efektivitas jalur masuk: IPK & dropout per jalur
SELECT
    jalur_masuk,
    COUNT(*)             AS jml,
    ROUND(AVG(ipk), 2)   AS rata_ipk,
    ROUND(100.0 * SUM(CASE WHEN status_mahasiswa = 'Drop Out' THEN 1 END)
          / COUNT(*), 1) AS dropout_pct
FROM mahasiswa
GROUP BY jalur_masuk
ORDER BY rata_ipk DESC;
