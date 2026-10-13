"""
Generator dataset sintetis Penerimaan Mahasiswa Baru (PMB) Politeknik Negeri Indramayu.

Menghasilkan 2 tabel relasional:
  - pendaftar.csv : funnel pendaftaran -> seleksi -> daftar ulang
  - mahasiswa.csv : status akademik mahasiswa yang daftar ulang

CATATAN: Seluruh data SINTETIS (hasil simulasi), bukan data riil Polindra.
Struktur prodi/jurusan mengacu pada informasi publik di polindra.ac.id.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# ---------------------------------------------------------------
# Referensi prodi riil Polindra (polindra.ac.id) + tahun dibuka
# (jenjang, jurusan, tahun_buka, daya_tampung_per_tahun, bobot_peminat)
# Bobot peminat dikalibrasi ke angka riil peminat SNBT 2025
# (Kep 556, TI 480, TM 327, SIKC 154, RPL 156, PM 147, TPTU 133,
#  TRIK 106, TRK 76 — sumber: sidata SNPMB via min.co.id)
# ---------------------------------------------------------------
PRODI = {
    # Jurusan Teknik Informatika
    "D3 Teknik Informatika":                    ("D3", "Teknik Informatika", 2015, 96, 0.86),
    "S1T Rekayasa Perangkat Lunak":             ("S1T", "Teknik Informatika", 2016, 96, 0.28),
    "S1T Sistem Informasi Kota Cerdas":         ("S1T", "Teknik Informatika", 2022, 48, 0.28),
    "S1T Teknologi Rekayasa Komputer":          ("S1T", "Teknik Informatika", 2023, 48, 0.14),
    # Jurusan Teknik
    "D3 Teknik Mesin":                          ("D3", "Teknik", 2015, 64, 0.59),
    "D3 Teknik Pendingin & Tata Udara":         ("D3", "Teknik", 2015, 48, 0.24),
    "S1T Perancangan Manufaktur":               ("S1T", "Teknik", 2016, 48, 0.26),
    "S1T Teknologi Rekayasa Instrumen & Kontrol": ("S1T", "Teknik", 2022, 48, 0.19),
    # Jurusan Kesehatan
    "D3 Keperawatan":                           ("D3", "Kesehatan", 2016, 96, 1.00),
    "S1T Teknologi Laboratorium Medis":         ("S1T", "Kesehatan", 2020, 48, 0.25),
    "S1T Teknologi Rekayasa Elektro-Medis":     ("S1T", "Kesehatan", 2022, 32, 0.15),
}

# Jalur seleksi mengikuti kebijakan nasional yang sebenarnya:
# era 2019-2023: jalur khusus politeknik (SNMPN rapor + SBMPN ujian) — FDPNI
# era 2024-2025: SNPMB (Permendikbudristek 48/2022) — SNBP rapor + SNBT UTBK
JALUR_ERA_A = ["SNMPN", "SBMPN", "Mandiri", "Prestasi"]
JALUR_PA = [0.35, 0.35, 0.25, 0.05]
JALUR_ERA_B = ["SNBP", "SNBT", "Mandiri", "Prestasi"]
JALUR_PB = [0.30, 0.42, 0.26, 0.02]
JALUR_RAPOR = {"SNMPN", "SNBP", "Prestasi"}       # seleksi tanpa ujian tulis
JALUR_UJIAN = {"SBMPN", "SNBT", "Mandiri"}        # seleksi berbasis tes

# Channel akuisisi pendaftar — tren media sosial naik, jalur tradisional turun
KANAL = ["TikTok/Instagram", "Guru BK", "Alumni/Keluarga", "Website",
         "Pameran Kampus", "Teman"]
def kanal_p(tahun):
    """Proporsi kanal per tahun — TikTok/IG melesat pasca-2021."""
    base = {
        2019: [0.10, 0.28, 0.24, 0.12, 0.16, 0.10],
        2021: [0.24, 0.24, 0.20, 0.12, 0.10, 0.10],
        2023: [0.38, 0.18, 0.16, 0.11, 0.08, 0.09],
        2025: [0.46, 0.14, 0.14, 0.10, 0.06, 0.10],
    }
    tahun_keys = sorted(base)
    lo = max(k for k in tahun_keys if k <= tahun)
    hi = min(k for k in tahun_keys if k >= tahun)
    if lo == hi:
        return base[lo]
    w = (tahun - lo) / (hi - lo)
    return [(1 - w) * a + w * b for a, b in zip(base[lo], base[hi])]

# Asal domisili pendaftar — mayoritas Indramayu & Ciayumajakuning
KOTA = ["Kab. Indramayu", "Kab. Cirebon", "Kota Cirebon", "Kab. Majalengka",
        "Kab. Kuningan", "Kab. Subang", "Kab. Sumedang", "Kab. Karawang",
        "Kota Bandung", "Kab. Bandung", "Kota Bekasi", "Kab. Bekasi",
        "DKI Jakarta", "Kab. Brebes", "Kab. Tegal", "Lainnya"]
KOTA_P = [0.34, 0.10, 0.07, 0.09, 0.08, 0.06, 0.05, 0.03,
          0.02, 0.02, 0.02, 0.02, 0.02, 0.03, 0.02, 0.03]

SEKOLAH = ["SMA", "SMK", "MA", "Lainnya"]

TAHUN = list(range(2019, 2026))
# Pertumbuhan pendaftar per tahun (Polindra makin dikenal + prodi baru)
N_PENDAFTAR = {2019: 1400, 2020: 1700, 2021: 2000, 2022: 2600,
               2023: 3000, 2024: 3400, 2025: 3800}

# Proporsi jenis sekolah per jurusan (SMK dominan di teknik, SMA/MA di kesehatan)
SEKOLAH_P = {
    "Teknik Informatika": [0.35, 0.55, 0.07, 0.03],
    "Teknik":             [0.30, 0.60, 0.06, 0.04],
    "Kesehatan":          [0.55, 0.05, 0.38, 0.02],
}

# Proporsi jenis kelamin per jurusan
GENDER_P = {
    "Teknik Informatika": [0.62, 0.38],
    "Teknik":             [0.85, 0.15],
    "Kesehatan":          [0.20, 0.80],
}


def prodi_tersedia(tahun):
    """Prodi yang sudah dibuka pada tahun tertentu."""
    return [p for p, v in PRODI.items() if v[2] <= tahun]


def buat_pendaftar() -> pd.DataFrame:
    rows = []
    pid = 1
    for tahun in TAHUN:
        n = N_PENDAFTAR[tahun]
        avail = prodi_tersedia(tahun)
        # bobot peminat dinormalisasi; prodi baru biasanya langsung diminati
        weights = np.array([PRODI[p][4] for p in avail])
        weights /= weights.sum()
        pilihan1 = rng.choice(avail, size=n, p=weights)

        for p1 in pilihan1:
            _, jurusan, _, _, _ = PRODI[p1]
            # pilihan 2: 70% jurusan sama, 30% jurusan lain
            if rng.random() < 0.7:
                pool = [p for p in avail if PRODI[p][1] == jurusan and p != p1]
            else:
                pool = [p for p in avail if p != p1]
            p2 = rng.choice(pool) if pool else p1

            jk = rng.choice(["L", "P"], p=GENDER_P[jurusan])
            sekolah = rng.choice(SEKOLAH, p=SEKOLAH_P[jurusan])
            nilai_rapor = np.clip(rng.normal(80, 5), 65, 98)
            jalur_list, jalur_p = (JALUR_ERA_A, JALUR_PA) if tahun <= 2023 \
                else (JALUR_ERA_B, JALUR_PB)

            rows.append({
                "id_pendaftar": f"PMB{tahun}{pid:05d}",
                "tahun_daftar": tahun,
                "jalur_masuk": rng.choice(jalur_list, p=jalur_p),
                "prodi_pilihan_1": p1,
                "prodi_pilihan_2": p2,
                "jurusan": jurusan,
                "jenis_kelamin": jk,
                "asal_kota": rng.choice(KOTA, p=KOTA_P),
                "jenis_sekolah": sekolah,
                "sumber_informasi": rng.choice(KANAL, p=kanal_p(tahun)),
                "nilai_rapor": round(nilai_rapor, 1),
            })
            pid += 1

    df = pd.DataFrame(rows)

    # Nilai ujian hanya ada di jalur berbasis tes; jalur rapor pakai rapor
    df["nilai_ujian"] = np.where(
        df["jalur_masuk"].isin(JALUR_UJIAN),
        np.clip(rng.normal(65, 12, len(df)), 20, 100).round(1),
        np.nan,
    )

    # ---- Skor seleksi ----
    # SMK dapat bonus skor di jurusan teknik; SMA/MA unggul di kesehatan
    bonus = np.where(
        (df["jurusan"].isin(["Teknik", "Teknik Informatika"])) & (df["jenis_sekolah"] == "SMK"), 3.0,
        np.where((df["jurusan"] == "Kesehatan") & (df["jenis_sekolah"].isin(["SMA", "MA"])), 3.0, 0.0),
    )
    skor = df["nilai_rapor"] * 0.6 + df["nilai_ujian"].fillna(df["nilai_rapor"]) * 0.4 + bonus
    df["skor_seleksi"] = skor.round(2)

    # ---- Seleksi per prodi x tahun x jalur: tiap jalur punya kuota sendiri ----
    # (realistis: tiap jalur adalah gelombang seleksi terpisah;
    #  era SNPMB: SNBP >=20% & SNBT >=40% daya tampung per Permendikbudristek 48/2022)
    KUOTA_ERA_A = {"SNMPN": 0.30, "SBMPN": 0.40, "Mandiri": 0.27, "Prestasi": 0.03}
    KUOTA_ERA_B = {"SNBP": 0.20, "SNBT": 0.40, "Mandiri": 0.38, "Prestasi": 0.02}

    df["status_seleksi"] = "Tidak Lulus"
    df["prodi_diterima"] = pd.Series(pd.NA, index=df.index, dtype="object")
    for tahun in TAHUN:
        kuota = KUOTA_ERA_A if tahun <= 2023 else KUOTA_ERA_B
        for prodi in prodi_tersedia(tahun):
            for jalur, frac in kuota.items():
                daya = round(PRODI[prodi][3] * 1.8 * frac)
                mask = (
                    (df["tahun_daftar"] == tahun)
                    & (df["status_seleksi"] == "Tidak Lulus")
                    & (df["jalur_masuk"] == jalur)
                    & ((df["prodi_pilihan_1"] == prodi) | (df["prodi_pilihan_2"] == prodi))
                )
                cand = df[mask].nlargest(daya, "skor_seleksi")
                df.loc[cand.index, "status_seleksi"] = "Lulus"
                # diterima di prodi pilihan 1 jika masuk kandidat p1, else p2
                df.loc[cand.index, "prodi_diterima"] = np.where(
                    cand["prodi_pilihan_1"] == prodi, cand["prodi_pilihan_1"], prodi
                )

    # ---- Daftar ulang: ~85% dari yang lulus (jalur Mandiri lebih rendah) ----
    lulus = df["status_seleksi"] == "Lulus"
    p_du = np.where(df["jalur_masuk"] == "Mandiri", 0.78, 0.88)
    df["daftar_ulang"] = np.where(lulus & (rng.random(len(df)) < p_du), "Ya", "Tidak")

    return df


def buat_mahasiswa(df_pendaftar: pd.DataFrame) -> pd.DataFrame:
    """Mahasiswa = pendaftar yang lulus seleksi & daftar ulang."""
    m = df_pendaftar[df_pendaftar["daftar_ulang"] == "Ya"].copy()
    m = m.reset_index(drop=True)

    m["nim"] = [
        f"{int(tahun) % 100:02d}{abs(hash(p)) % 900 + 100}{i:03d}"
        for i, (tahun, p) in enumerate(zip(m["tahun_daftar"], m["prodi_diterima"]))
    ]
    m["id_pendaftar"] = m["id_pendaftar"].values
    m["prodi"] = m["prodi_diterima"]
    m["angkatan"] = m["tahun_daftar"]

    # Beasiswa KIP-Kuliah ~20%, lebih banyak dari luar Indramayu
    m["beasiswa_kip"] = np.where(
        rng.random(len(m)) < np.where(m["asal_kota"] == "Kab. Indramayu", 0.15, 0.25),
        "Ya", "Tidak",
    )

    # ---- IPK: distribusi per jurusan, mahasiswa KIP sedikit lebih rajin ----
    base_mu = {"Teknik Informatika": 3.35, "Teknik": 3.15, "Kesehatan": 3.45}
    mu = (m["jurusan"].map(base_mu)
          + np.where(m["beasiswa_kip"] == "Ya", 0.08, 0.0)
          + np.where(m["jalur_masuk"].isin(["SNMPN", "SNBP"]), 0.05, 0.0))
    m["ipk"] = np.clip(rng.normal(mu, 0.35), 1.5, 4.0).round(2)

    # ---- Status mahasiswa ----
    # Angkatan lama sudah banyak lulus; DO dominan di 2 tahun pertama
    status = []
    for _, r in m.iterrows():
        usia = 2025 - r["angkatan"]
        jenjang = PRODI[r["prodi"]][0]
        lulus_min = 3 if jenjang == "D3" else 4
        if usia >= lulus_min:
            s = rng.choice(["Lulus", "Aktif", "Drop Out"], p=[0.80, 0.14, 0.06])
        elif usia >= 2:
            # belum bisa lulus — masa studi minimum belum tercapai
            s = rng.choice(["Aktif", "Cuti", "Drop Out"], p=[0.84, 0.07, 0.09])
        else:
            s = rng.choice(["Aktif", "Cuti", "Drop Out"], p=[0.88, 0.05, 0.07])
        status.append(s)
    m["status_mahasiswa"] = status

    # Lulusan tepat waktu cenderung IPK lebih tinggi — realistis, koreksi halus
    m.loc[m["status_mahasiswa"] == "Lulus", "ipk"] = np.clip(
        m.loc[m["status_mahasiswa"] == "Lulus", "ipk"] + 0.15, 1.5, 4.0
    ).round(2)
    m.loc[m["status_mahasiswa"] == "Drop Out", "ipk"] = np.clip(
        m.loc[m["status_mahasiswa"] == "Drop Out", "ipk"] - 0.6, 0.5, 4.0
    ).round(2)

    cols = ["nim", "id_pendaftar", "angkatan", "prodi", "jurusan", "jenis_kelamin",
            "asal_kota", "jenis_sekolah", "jalur_masuk", "beasiswa_kip", "ipk",
            "status_mahasiswa"]
    return m[cols]


def buat_khs(df_m: pd.DataFrame) -> pd.DataFrame:
    """IP per semester tiap mahasiswa — data longitudinal.

    Pola realistis:
    - Lulus   : IP naik tipis, selesai full jenjang (6 smt D3 / 8 smt S1T)
    - Drop Out: IP menurun tajam lalu berhenti (semester 1-4)
    - Aktif/Cuti: berfluktuasi di sekitar IPK akhir
    """
    rows = []
    for _, r in df_m.iterrows():
        usia = 2025 - r["angkatan"]
        jenjang_max = 6 if PRODI[r["prodi"]][0] == "D3" else 8
        n_sem = int(min(max(usia * 2, 1), jenjang_max))
        st = r["status_mahasiswa"]
        if st == "Drop Out":
            n_sem = int(rng.integers(1, min(4, n_sem) + 1))
            trend = np.linspace(r["ipk"] + 0.45, max(r["ipk"], 1.0), n_sem)
        elif st == "Lulus":
            trend = np.linspace(r["ipk"] - 0.15, r["ipk"] + 0.12, n_sem)
        else:
            trend = np.full(n_sem, r["ipk"])
        ip_s = np.clip(trend + rng.normal(0, 0.12, n_sem), 0.5, 4.0)
        for s, v in enumerate(ip_s, 1):
            rows.append({
                "nim": r["nim"],
                "semester": s,
                "ip_semester": round(float(v), 2),
                "sks_ambil": int(rng.integers(15, 25)) if st == "Drop Out"
                else int(rng.integers(18, 25)),
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    pendaftar = buat_pendaftar()
    mahasiswa = buat_mahasiswa(pendaftar)
    khs = buat_khs(mahasiswa)

    pendaftar.to_csv("data/raw/pendaftar.csv", index=False)
    mahasiswa.to_csv("data/raw/mahasiswa.csv", index=False)
    khs.to_csv("data/raw/khs.csv", index=False)

    print(f"pendaftar.csv : {len(pendaftar):,} baris x {pendaftar.shape[1]} kolom")
    print(f"mahasiswa.csv : {len(mahasiswa):,} baris x {mahasiswa.shape[1]} kolom")
    print(f"khs.csv       : {len(khs):,} baris x {khs.shape[1]} kolom")
    print("\nContoh pendaftar:")
    print(pendaftar.head(3).to_string())
    print("\nDistribusi status seleksi:")
    print(pendaftar["status_seleksi"].value_counts(normalize=True).round(3))
