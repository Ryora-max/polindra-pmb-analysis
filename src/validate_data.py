"""Validasi kualitas dataset — assertion checks ala data-quality pipeline.
Jalankan setiap kali data diregenerasi: python src/validate_data.py
Exit code 0 jika semua lolos, 1 jika ada kegagalan."""
import sys
import pandas as pd

FAIL = []

def check(nama, kondisi, detail=""):
    status = "PASS" if kondisi else "FAIL"
    if not kondisi:
        FAIL.append(nama)
    print(f"  [{status}] {nama}" + (f" — {detail}" if detail and not kondisi else ""))

pendaftar = pd.read_csv("data/raw/pendaftar.csv")
mahasiswa = pd.read_csv("data/raw/mahasiswa.csv")
khs = pd.read_csv("data/raw/khs.csv")

print("== Struktur & kelengkapan ==")
check("id_pendaftar unik", pendaftar["id_pendaftar"].is_unique)
check("nim unik", mahasiswa["nim"].is_unique)
kolom_wajib = ["id_pendaftar", "tahun_daftar", "jalur_masuk", "prodi_pilihan_1",
               "jurusan", "status_seleksi", "daftar_ulang", "sumber_informasi"]
check("tidak ada null di kolom wajib pendaftar",
      not pendaftar[kolom_wajib].isna().any().any())
check("tidak ada null di tabel mahasiswa", not mahasiswa.isna().any().any())

print("\n== Rentang nilai ==")
check("nilai_rapor 0-100", pendaftar["nilai_rapor"].between(0, 100).all())
check("nilai_ujian 0-100 / NaN",
      pendaftar["nilai_ujian"].dropna().between(0, 100).all())
check("ipk 0-4", mahasiswa["ipk"].between(0, 4).all())
check("tahun_daftar 2019-2025",
      pendaftar["tahun_daftar"].between(2019, 2025).all())

print("\n== Konsistensi logika bisnis ==")
ujian_cols = pendaftar[pendaftar["nilai_ujian"].notna()]["jalur_masuk"].unique()
check("nilai_ujian hanya di jalur ber-tes",
      set(ujian_cols) <= {"SBMPN", "SNBT", "Mandiri"}, f"ada di: {ujian_cols}")
rapor_cols = pendaftar[pendaftar["nilai_ujian"].isna()]["jalur_masuk"].unique()
check("jalur rapor tidak punya nilai_ujian",
      set(rapor_cols) <= {"SNMPN", "SNBP", "Prestasi"}, f"ada di: {rapor_cols}")

lulus = pendaftar["status_seleksi"] == "Lulus"
check("semua yg lulus punya prodi_diterima",
      pendaftar.loc[lulus, "prodi_diterima"].notna().all())
check("prodi_diterima hanya untuk yang lulus",
      pendaftar.loc[~lulus, "prodi_diterima"].isna().all())
check("daftar_ulang='Ya' hanya subset yang lulus",
      (pendaftar.loc[pendaftar["daftar_ulang"] == "Ya", "status_seleksi"] == "Lulus").all())
pilihan = pendaftar.loc[lulus]
check("prodi_diterima selalu salah satu pilihan",
      ((pilihan["prodi_diterima"] == pilihan["prodi_pilihan_1"])
       | (pilihan["prodi_diterima"] == pilihan["prodi_pilihan_2"])).all())

print("\n== Integritas relasional ==")
check("semua mahasiswa ada di pendaftar",
      mahasiswa["id_pendaftar"].isin(pendaftar["id_pendaftar"]).all())
check("mahasiswa = pendaftar yang daftar_ulang",
      set(mahasiswa["id_pendaftar"]) ==
      set(pendaftar.loc[pendaftar["daftar_ulang"] == "Ya", "id_pendaftar"]))
check("era jalur benar (SNMPN/SBMPN <=2023, SNBP/SNBT >=2024)",
      (pendaftar.loc[pendaftar["tahun_daftar"] <= 2023, "jalur_masuk"]
       .isin(["SNMPN", "SBMPN", "Mandiri", "Prestasi"]).all())
      and (pendaftar.loc[pendaftar["tahun_daftar"] >= 2024, "jalur_masuk"]
           .isin(["SNBP", "SNBT", "Mandiri", "Prestasi"]).all()))

print("\n== Tabel khs (longitudinal) ==")
check("semua NIM khs ada di mahasiswa", khs["nim"].isin(mahasiswa["nim"]).all())
check("ip_semester 0-4", khs["ip_semester"].between(0, 4).all())
check("semester >= 1", (khs["semester"] >= 1).all())
check("sks_ambil 10-24", khs["sks_ambil"].between(10, 24).all())
check("tidak ada duplikat nim+semester",
      not khs.duplicated(["nim", "semester"]).any())
# mahasiswa lulus harus punya semester lengkap
m_lulus = mahasiswa[mahasiswa["status_mahasiswa"] == "Lulus"]
sem_lulus = khs[khs["nim"].isin(m_lulus["nim"])].groupby("nim").size()
check("lulusan punya >=6 semester",
      (sem_lulus >= 6).all(), f"min={sem_lulus.min()}")

print(f"\n{'='*40}")
if FAIL:
    print(f"[GAGAL] {len(FAIL)} check tidak lolos: {FAIL}")
    sys.exit(1)
print(f"[OK] Semua check lolos ({pendaftar.shape[0]} pendaftar, {mahasiswa.shape[0]} mahasiswa)")
