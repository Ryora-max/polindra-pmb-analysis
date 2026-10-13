"""Load CSV mentah ke database SQLite (database/polindra.db)."""
import sqlite3
import pandas as pd

DB_PATH = "database/polindra.db"

def main():
    conn = sqlite3.connect(DB_PATH)

    pendaftar = pd.read_csv("data/raw/pendaftar.csv")
    mahasiswa = pd.read_csv("data/raw/mahasiswa.csv")

    pendaftar.to_sql("pendaftar", conn, if_exists="replace", index=False)
    mahasiswa.to_sql("mahasiswa", conn, if_exists="replace", index=False)

    for t in ("pendaftar", "mahasiswa"):
        n = pd.read_sql(f"SELECT COUNT(*) AS n FROM {t}", conn)["n"][0]
        print(f"Tabel {t}: {n:,} baris")

    conn.close()
    print(f"\nDatabase tersimpan di {DB_PATH}")

if __name__ == "__main__":
    main()
