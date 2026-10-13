"""Eksekusi seluruh query di database/queries.sql, tampilkan & export hasilnya
ke outputs/sql_results/*.csv — bukti SQL pipeline benar-benar berjalan."""
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = "database/polindra.db"
SQL_PATH = Path("database/queries.sql")
OUT_DIR = Path("outputs/sql_results")


def split_queries(sql_text: str):
    """Pecah file .sql per statement (dipisah ';' di akhir blok komentar)."""
    statements, buffer = [], []
    for line in sql_text.splitlines():
        if line.strip().startswith("--") and buffer:
            statements.append("\n".join(buffer).strip())
            buffer = []
            continue
        buffer.append(line)
        if line.strip().endswith(";"):
            statements.append("\n".join(buffer).strip())
            buffer = []
    if buffer:
        tail = "\n".join(buffer).strip()
        if tail:
            statements.append(tail)
    return [s for s in statements if s and "SELECT" in s.upper()]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    queries = split_queries(SQL_PATH.read_text(encoding="utf-8"))

    for i, q in enumerate(queries, start=1):
        df = pd.read_sql(q, conn)
        out = OUT_DIR / f"q{i}.csv"
        df.to_csv(out, index=False)
        print(f"\n===== Query {i} -> {out} ({len(df)} baris) =====")
        print(df.head(10).to_string(index=False))

    conn.close()
    print(f"\n{len(queries)} query dieksekusi, hasil tersimpan di {OUT_DIR}/")


if __name__ == "__main__":
    main()
