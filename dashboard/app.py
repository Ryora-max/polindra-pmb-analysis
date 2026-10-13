"""
Dashboard Analisis PMB Politeknik Negeri Indramayu.
Jalankan:  streamlit run dashboard/app.py
"""
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Analisis PMB Polindra",
    page_icon="🎓",
    layout="wide",
)


@st.cache_data
def load_data():
    pendaftar = pd.read_csv("data/raw/pendaftar.csv")
    mahasiswa = pd.read_csv("data/raw/mahasiswa.csv")
    return pendaftar, mahasiswa


pendaftar, mahasiswa = load_data()

st.title("🎓 Analisis Penerimaan Mahasiswa Baru — Politeknik Negeri Indramayu")
st.caption("Dataset sintetis (simulasi) berbasis struktur prodi riil Polindra · 2019–2025")

# ---------------- Sidebar filter ----------------
st.sidebar.header("Filter")
tahun_list = sorted(pendaftar["tahun_daftar"].unique())
tahun_pilih = st.sidebar.multiselect("Tahun pendaftaran", tahun_list, default=tahun_list)
jurusan_pilih = st.sidebar.multiselect(
    "Jurusan", sorted(pendaftar["jurusan"].unique()),
    default=sorted(pendaftar["jurusan"].unique()),
)
jalur_pilih = st.sidebar.multiselect(
    "Jalur masuk", sorted(pendaftar["jalur_masuk"].unique()),
    default=sorted(pendaftar["jalur_masuk"].unique()),
)

pend = pendaftar[
    pendaftar["tahun_daftar"].isin(tahun_pilih)
    & pendaftar["jurusan"].isin(jurusan_pilih)
    & pendaftar["jalur_masuk"].isin(jalur_pilih)
]
mhs = mahasiswa[
    mahasiswa["angkatan"].isin(tahun_pilih)
    & mahasiswa["jurusan"].isin(jurusan_pilih)
    & mahasiswa["jalur_masuk"].isin(jalur_pilih)
]

# ---------------- KPI ----------------
c1, c2, c3, c4 = st.columns(4)
n_pend = len(pend)
n_lulus = (pend["status_seleksi"] == "Lulus").sum()
n_reg = (pend["daftar_ulang"] == "Ya").sum()
c1.metric("Total Pendaftar", f"{n_pend:,}")
c2.metric("Lulus Seleksi", f"{n_lulus:,}", f"{100*n_lulus/max(n_pend,1):.1f}% dari pendaftar")
c3.metric("Daftar Ulang", f"{n_reg:,}", f"{100*n_reg/max(n_lulus,1):.1f}% dari lulus")
c4.metric("Rata-rata IPK", f"{mhs['ipk'].mean():.2f}" if len(mhs) else "-")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Tren & Funnel", "🏫 Prodi", "🗺️ Demografi", "📊 Akademik"]
)

# ---------------- Tab 1: Tren & funnel ----------------
with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        tren = (
            pend.groupby("tahun_daftar")
            .agg(pendaftar=("id_pendaftar", "count"),
                 lulus=("status_seleksi", lambda s: (s == "Lulus").sum()),
                 registrasi=("daftar_ulang", lambda s: (s == "Ya").sum()))
            .reset_index()
        )
        fig = px.line(tren, x="tahun_daftar", y=["pendaftar", "lulus", "registrasi"],
                      markers=True, title="Tren funnel penerimaan per tahun",
                      labels={"value": "Jumlah", "tahun_daftar": "Tahun", "variable": "Tahap"})
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        funnel = pd.DataFrame({
            "Tahap": ["Pendaftar", "Lulus Seleksi", "Daftar Ulang"],
            "Jumlah": [n_pend, n_lulus, n_reg],
        })
        fig = px.funnel(funnel, x="Jumlah", y="Tahap",
                        title="Conversion funnel pendaftar → mahasiswa")
        st.plotly_chart(fig, use_container_width=True)

    funnel_jalur = (
        pend.groupby("jalur_masuk")
        .agg(pendaftar=("id_pendaftar", "count"),
             registrasi=("daftar_ulang", lambda s: (s == "Ya").sum()))
        .assign(rate=lambda d: 100 * d["registrasi"] / d["pendaftar"])
        .reset_index()
    )
    fig = px.bar(funnel_jalur, x="jalur_masuk", y="rate",
                 title="Conversion rate pendaftar → registrasi per jalur masuk (%)",
                 labels={"rate": "Conversion (%)", "jalur_masuk": "Jalur"}, text_auto=".1f")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Tab 2: Prodi ----------------
with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        peminat = pend["prodi_pilihan_1"].value_counts().head(10).reset_index()
        peminat.columns = ["prodi", "peminat"]
        fig = px.bar(peminat, y="prodi", x="peminat", orientation="h",
                     title="10 prodi paling diminati", labels={"prodi": "", "peminat": "Peminat"})
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        ketat = (
            pend.groupby("prodi_pilihan_1")
            .agg(pendaftar=("id_pendaftar", "count"),
                 diterima=("status_seleksi", lambda s: (s == "Lulus").sum()))
            .assign(rate=lambda d: 100 * d["diterima"] / d["pendaftar"])
            .query("pendaftar >= 50")
            .nsmallest(10, "rate").reset_index()
        )
        fig = px.bar(ketat, y="prodi_pilihan_1", x="rate", orientation="h",
                     title="10 prodi paling ketat (% diterima, min. 50 pendaftar)",
                     labels={"rate": "% diterima", "prodi_pilihan_1": ""})
        fig.update_layout(yaxis={"categoryorder": "total descending"})
        st.plotly_chart(fig, use_container_width=True)

# ---------------- Tab 3: Demografi ----------------
with tab3:
    col_a, col_b = st.columns(2)
    with col_a:
        asal = mhs["asal_kota"].value_counts().head(10).reset_index()
        asal.columns = ["kota", "jumlah"]
        fig = px.bar(asal, y="kota", x="jumlah", orientation="h",
                     title="Top 10 kota asal mahasiswa", labels={"kota": "", "jumlah": "Mahasiswa"})
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        fig = px.sunburst(mhs, path=["jurusan", "jenis_sekolah"],
                          title="Komposisi jenis sekolah asal per jurusan")
        st.plotly_chart(fig, use_container_width=True)

    gender = mhs.groupby(["jurusan", "jenis_kelamin"]).size().reset_index(name="n")
    fig = px.bar(gender, x="jurusan", y="n", color="jenis_kelamin", barmode="group",
                 title="Komposisi gender per jurusan",
                 labels={"n": "Mahasiswa", "jurusan": "Jurusan"})
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Tab 4: Akademik ----------------
with tab4:
    col_a, col_b = st.columns(2)
    with col_a:
        ipk_prodi = mhs.groupby("prodi")["ipk"].mean().sort_values().reset_index()
        fig = px.bar(ipk_prodi, y="prodi", x="ipk", orientation="h",
                     title="Rata-rata IPK per prodi", labels={"prodi": "", "ipk": "IPK"},
                     range_x=[0, 4])
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        do = (
            mhs.groupby("prodi")["status_mahasiswa"]
            .apply(lambda s: 100 * (s == "Drop Out").sum() / len(s))
            .sort_values(ascending=False).head(10).reset_index(name="dropout_pct")
        )
        fig = px.bar(do, y="prodi", x="dropout_pct", orientation="h",
                     title="Dropout rate per prodi (%)",
                     labels={"prodi": "", "dropout_pct": "%"})
        fig.update_layout(yaxis={"categoryorder": "total descending"})
        st.plotly_chart(fig, use_container_width=True)

    fig = px.histogram(mhs, x="ipk", color="jurusan", nbins=30, barmode="overlay",
                       opacity=0.6, title="Distribusi IPK per jurusan",
                       labels={"ipk": "IPK"})
    st.plotly_chart(fig, use_container_width=True)

st.caption("Built with Streamlit + Plotly · Data sintetis untuk keperluan portofolio")
