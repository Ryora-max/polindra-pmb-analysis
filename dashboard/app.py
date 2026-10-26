"""
Dashboard Analisis PMB Politeknik Negeri Indramayu.
Jalankan:  streamlit run dashboard/app.py
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# ------------------------------------------------------------------ #
#  Page config & theme                                                #
# ------------------------------------------------------------------ #
st.set_page_config(
    page_title="PMB Polindra Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Vibrant modern palette ----
C_BLUE, C_CYAN, C_TEAL = "#3B82F6", "#06B6D4", "#14B8A6"
C_GREEN, C_AMBER, C_ORANGE = "#22C55E", "#F59E0B", "#F97316"
C_PINK, C_PURPLE, C_RED = "#EC4899", "#8B5CF6", "#EF4444"
PALETTE = [C_BLUE, C_CYAN, C_GREEN, C_AMBER, C_PINK, C_PURPLE, C_ORANGE, C_TEAL]

st.markdown("""
<style>
    .block-container {padding-top: 0rem; padding-bottom: 2rem; max-width: 1280px;}
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,#312E81 0%,#4C1D95 55%,#701A75 100%);}
    [data-testid="stSidebar"] * {color: #F1EEFF !important;}
    [data-testid="stSidebar"] .stMultiSelect label {font-weight: 600;}

    /* ---------- Hero ---------- */
    .hero {
        background: linear-gradient(115deg, #4F46E5 0%, #7C3AED 38%,
                    #DB2777 75%, #F59E0B 120%);
        border-radius: 20px;
        padding: 2.3rem 2.4rem 1.9rem 2.4rem;
        margin: 1rem 0 1.5rem 0;
        color: white;
        box-shadow: 0 14px 34px rgba(124,58,237,.28);
        position: relative; overflow: hidden;
    }
    .hero::after {
        content:""; position:absolute; right:-70px; top:-70px;
        width:230px; height:230px; border-radius:50%;
        background: rgba(255,255,255,.14);
    }
    .hero::before {
        content:""; position:absolute; right:60px; bottom:-90px;
        width:170px; height:170px; border-radius:50%;
        background: rgba(255,255,255,.10);
    }
    .hero h1 {margin: 0; font-size: 2rem; font-weight: 900; letter-spacing:.3px;}
    .hero p  {margin: .55rem 0 0 0; font-size: 1rem; opacity: .93;}

    /* ---------- Gradient KPI tiles ---------- */
    .kpi {
        border-radius: 16px;
        padding: 1.1rem 1.2rem 1rem 1.2rem;
        box-shadow: 0 6px 18px rgba(30,34,53,.12);
        height: 100%; color: white;
        position: relative; overflow: hidden;
    }
    .kpi::after {content:""; position:absolute; right:-30px; top:-30px;
        width:90px; height:90px; border-radius:50%;
        background: rgba(255,255,255,.18);}
    .kpi .label {font-size: .76rem; font-weight: 700; opacity:.92;
                 text-transform: uppercase; letter-spacing: .7px;}
    .kpi .value {font-size: 1.8rem; font-weight: 900; line-height: 1.15;}
    .kpi .sub   {font-size: .8rem; opacity:.88; margin-top: .15rem;}

    /* ---------- Section pills & insight boxes ---------- */
    .sec-pill {
        display:inline-block; font-size:1.05rem; font-weight:800;
        color:#1E2235; margin:.5rem 0 .3rem 0;
        padding:.15rem .8rem .15rem 0;
    }
    .sec-pill::before {
        content:"●"; margin-right:.45rem; font-size:.9rem;
    }
    .insight {
        border-radius: 0 12px 12px 0;
        padding: .8rem 1rem;
        font-size: .88rem;
        margin: .6rem 0;
    }
    .insight.blue  {background:#EAF2FF; border-left:4px solid #3B82F6; color:#274C8E;}
    .insight.green {background:#E9F9F0; border-left:4px solid #22C55E; color:#166534;}
    .insight.amber {background:#FFF6E5; border-left:4px solid #F59E0B; color:#92580A;}
    .insight b {color: inherit; font-weight:800;}

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {gap: .45rem;}
    .stTabs [data-baseweb="tab"] {
        background: #ECECF6; border-radius: 10px 10px 0 0;
        padding: .45rem 1.1rem; font-weight: 700; color: #5A5F7E;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(120deg,#7C3AED,#DB2777) !important;
        color: white !important;
    }

    [data-testid="stExpander"] {background: #FFFFFF; border-radius: 12px;
        border: 1px solid #E6E8F2;}
    [data-testid="stDataFrame"] {border-radius: 12px; overflow:hidden;
        border:1px solid #E6E8F2;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------ #
#  Data                                                               #
# ------------------------------------------------------------------ #
@st.cache_data
def load_data():
    return (pd.read_csv("data/raw/pendaftar.csv"),
            pd.read_csv("data/raw/mahasiswa.csv"),
            pd.read_csv("data/raw/khs.csv"))

pendaftar, mahasiswa, khs = load_data()

def titik(x):
    """Format ribuan ala Indonesia: 17900 -> '17.900'."""
    return f"{x:,.0f}".replace(",", ".")

BASE_LAYOUT = dict(
    font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#1E2235"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=46, b=10),
    title=dict(font=dict(size=15, color="#1E2235")),
    colorway=PALETTE,
)

def polish(fig, **kw):
    fig.update_layout(**{**BASE_LAYOUT, **kw})
    # automargin: sumbu otomatis melebar agar label panjang tidak terpotong
    fig.update_xaxes(showgrid=False, zeroline=False, automargin=True)
    fig.update_yaxes(gridcolor="#ECECF6", zeroline=False, automargin=True,
                     title_standoff=10)
    # label di ujung bar boleh melampaui area plot (tidak kepotong)
    fig.update_traces(cliponaxis=False, selector=dict(type="bar"))
    # seragamkan & sembunyikan label terlalu kecil (anti-tumpuk di pie)
    fig.update_layout(uniformtext_minsize=9, uniformtext_mode="hide")
    return fig

def insight_box(text, tone="blue"):
    st.markdown(f'<div class="insight {tone}">💡 {text}</div>',
                unsafe_allow_html=True)

def sec(icon, label, color):
    st.markdown(
        f'<div class="sec-pill" style="color:{color}">{icon} '
        f'<span style="color:#1E2235">{label}</span></div>',
        unsafe_allow_html=True)

def penjelasan(judul, isi_md):
    with st.expander(f"📖 {judul}"):
        st.markdown(isi_md)

# ------------------------------------------------------------------ #
#  Sidebar filters                                                    #
# ------------------------------------------------------------------ #
st.sidebar.markdown("## 🎛️ Filter Data")
st.sidebar.caption("Semua visual mengikuti filter ini")

tahun_list = sorted(pendaftar["tahun_daftar"].unique())
tahun_pilih = st.sidebar.multiselect("Tahun Pendaftaran", tahun_list, default=tahun_list)
jurusan_pilih = st.sidebar.multiselect(
    "Jurusan", sorted(pendaftar["jurusan"].unique()),
    default=sorted(pendaftar["jurusan"].unique()))
jalur_pilih = st.sidebar.multiselect(
    "Jalur Masuk", sorted(pendaftar["jalur_masuk"].unique()),
    default=sorted(pendaftar["jalur_masuk"].unique()))

st.sidebar.divider()
st.sidebar.caption("📊 Dataset sintetis · simulasi terkalibrasi data riil Polindra")

pend = pendaftar[pendaftar["tahun_daftar"].isin(tahun_pilih)
                 & pendaftar["jurusan"].isin(jurusan_pilih)
                 & pendaftar["jalur_masuk"].isin(jalur_pilih)]
mhs = mahasiswa[mahasiswa["angkatan"].isin(tahun_pilih)
                & mahasiswa["jurusan"].isin(jurusan_pilih)
                & mahasiswa["jalur_masuk"].isin(jalur_pilih)]

mhs_x = mhs.merge(
    pend[["id_pendaftar", "nilai_rapor", "skor_seleksi"]],
    on="id_pendaftar", how="left")
khs_x = khs.merge(mhs[["nim", "status_mahasiswa"]], on="nim", how="left")

# ------------------------------------------------------------------ #
#  Hero + KPI                                                         #
# ------------------------------------------------------------------ #
st.markdown("""
<div class="hero">
  <h1>🎓 PMB Polindra Analytics</h1>
  <p>Analisis funnel Penerimaan Mahasiswa Baru Politeknik Negeri Indramayu · 2019–2025</p>
</div>
""", unsafe_allow_html=True)

n_pend, n_lulus = len(pend), (pend["status_seleksi"] == "Lulus").sum()
n_reg = (pend["daftar_ulang"] == "Ya").sum()
n_do = (mhs["status_mahasiswa"] == "Drop Out").sum()

GRAD = {
    "blue":   "linear-gradient(135deg,#3B82F6 0%,#2563EB 100%)",
    "teal":   "linear-gradient(135deg,#14B8A6 0%,#0D9488 100%)",
    "amber":  "linear-gradient(135deg,#F59E0B 0%,#F97316 100%)",
    "purple": "linear-gradient(135deg,#8B5CF6 0%,#7C3AED 100%)",
    "pink":   "linear-gradient(135deg,#EC4899 0%,#EF4444 120%)",
}
kpis = [
    ("📥 Total Pendaftar", titik(n_pend), f"{len(tahun_pilih)} tahun pendaftaran", GRAD["blue"]),
    ("✅ Lulus Seleksi", titik(n_lulus), f"{100*n_lulus/max(n_pend,1):.1f}% dari pendaftar", GRAD["teal"]),
    ("📝 Daftar Ulang", titik(n_reg), f"{100*n_reg/max(n_lulus,1):.1f}% dari yang lulus", GRAD["amber"]),
    ("📊 Rata-rata IPK", f"{mhs['ipk'].mean():.2f}".replace(".", ",") if len(mhs) else "-",
     "mahasiswa terfilter", GRAD["purple"]),
    ("⚠️ Dropout Rate", f"{100*n_do/max(len(mhs),1):.1f}%".replace(".", ","),
     f"{titik(n_do)} mahasiswa", GRAD["pink"]),
]
for col, (label, val, sub, grad) in zip(st.columns(5), kpis):
    col.markdown(f"""
    <div class="kpi" style="background:{grad}">
        <div class="label">{label}</div>
        <div class="value">{val}</div>
        <div class="sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

st.write("")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📈 Tren & Funnel", "🏫 Program Studi", "🗺️ Demografi",
     "📊 Akademik", "🔮 Prediktif & Segmen", "🔍 Eksplorasi Data"])

# ------------------------------------------------------------------ #
#  TAB 1 — Tren & funnel                                              #
# ------------------------------------------------------------------ #
with tab1:
    c1, c2 = st.columns([3, 2], gap="large")

    with c1:
        sec("📈", "Pertumbuhan funnel 2019–2025", C_BLUE)
        tren = (pend.groupby("tahun_daftar")
                .agg(Pendaftar=("id_pendaftar", "count"),
                     Lulus=("status_seleksi", lambda s: (s == "Lulus").sum()),
                     Registrasi=("daftar_ulang", lambda s: (s == "Ya").sum()))
                .reset_index())
        fig = go.Figure()
        for col, color in [("Pendaftar", C_BLUE), ("Lulus", C_GREEN), ("Registrasi", C_ORANGE)]:
            fig.add_trace(go.Scatter(
                x=tren["tahun_daftar"], y=tren[col], name=col, mode="lines+markers",
                line=dict(width=3.5, color=color), marker=dict(size=9),
                fill="tozeroy" if col == "Pendaftar" else None,
                fillcolor="rgba(59,130,246,.10)"))
        polish(fig, legend=dict(orientation="h", y=1.14))
        st.plotly_chart(fig, use_container_width=True)

        sec("🔥", "Tingkat keketatan seleksi", C_RED)
        ketat_t = (pend.groupby("tahun_daftar")["status_seleksi"]
                   .apply(lambda s: 100 * (s == "Lulus").mean()).reset_index())
        fig = go.Figure(go.Scatter(
            x=ketat_t["tahun_daftar"], y=ketat_t["status_seleksi"],
            mode="lines+markers+text",
            text=ketat_t["status_seleksi"].map("{:.0f}%".format),
            textposition="top center",
            line=dict(width=3.5, color=C_PINK), marker=dict(size=10),
            fill="tozeroy", fillcolor="rgba(236,72,153,.10)"))
        polish(fig, yaxis_title="% lulus seleksi")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        sec("🧲", "Funnel konversi", C_PURPLE)
        fig = go.Figure(go.Funnel(
            y=["Pendaftar", "Lulus Seleksi", "Daftar Ulang"],
            x=[n_pend, n_lulus, n_reg],
            textinfo="value+percent initial",
            marker=dict(color=[C_BLUE, C_CYAN, C_AMBER]),
            connector=dict(line=dict(color="#D6D8F0", width=2))))
        polish(fig)
        st.plotly_chart(fig, use_container_width=True)

        sec("🎯", "Conversion per jalur masuk", C_TEAL)
        jalur_f = (pend.groupby("jalur_masuk")
                   .agg(n=("id_pendaftar", "count"),
                        reg=("daftar_ulang", lambda s: (s == "Ya").sum()))
                   .assign(rate=lambda d: 100 * d["reg"] / d["n"])
                   .sort_values("rate").reset_index())
        fig = px.bar(jalur_f, x="rate", y="jalur_masuk", orientation="h",
                     color="jalur_masuk", color_discrete_sequence=PALETTE,
                     text=jalur_f["rate"].map("{:.1f}%".format),
                     labels={"rate": "", "jalur_masuk": ""})
        fig.update_traces(textposition="outside")
        polish(fig, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    sec("📣", "Kanal akuisisi pendaftar per tahun", C_ORANGE)
    kanal = (pend.groupby(["tahun_daftar", "sumber_informasi"]).size()
             .reset_index(name="n"))
    fig = px.area(kanal, x="tahun_daftar", y="n", color="sumber_informasi",
                  color_discrete_sequence=PALETTE,
                  labels={"n": "Pendaftar", "tahun_daftar": "Tahun",
                          "sumber_informasi": "Kanal"})
    polish(fig, legend=dict(orientation="h", y=-0.18))
    st.plotly_chart(fig, use_container_width=True)

    penjelasan("Cara membaca bagian ini", """
**Grafik funnel (atas kiri)** menelusuri perjalanan pendaftar melalui 3 tahap:
mendaftar → lulus seleksi → daftar ulang (resmi jadi mahasiswa). Jarak antar garis
= berapa banyak yang "gugur" di tiap tahap.

**Grafik keketatan** menunjukkan % pendaftar yang lulus per tahun. Tren **turun**
(dari ~58% ke ~32%) berarti makin sulit masuk — peminat tumbuh lebih cepat
daripada daya tampung. Ini indikator reputasi kampus yang membaik.

**Funnel & conversion per jalur** menunjukkan jalur mana yang paling efektif
menghasilkan mahasiswa baru. Perhatikan dua hal berbeda: (1) *pass rate* —
seberapa sulit lulus di jalur itu (tergantung kuota jalur vs peminat), dan
(2) *yield* — dari yang lulus, berapa yang benar-benar registrasi.
Jalur Mandiri punya yield paling rendah karena pendaftar mandiri biasanya
punya opsi PTN lain.

**Kanal akuisisi** menunjukkan *dari mana pendaftar tahu Polindra*. Perhatikan
pergeseran: TikTok/IG melesat pasca-2021 (generasi digital native), sementara
kanal tradisional (guru BK, pameran) melandai — data seperti ini dipakai tim
marketing untuk alokasi budget promosi.

⚠️ **Catatan:** data sintetis — polanya dimodelkan realistis, angkanya simulasi.
""")

    insight_box("Peminat tumbuh <b>~170%</b> dalam 6 tahun — lonjakan 2022 berbarengan "
                "dibukanya prodi S1 Terapan baru. Keketatan naik: hanya <b>~32%</b> "
                "pendaftar lulus di 2025 vs ~58% di 2019.", "blue")

# ------------------------------------------------------------------ #
#  TAB 2 — Program studi                                              #
# ------------------------------------------------------------------ #
with tab2:
    c1, c2 = st.columns(2, gap="large")

    with c1:
        sec("🏆", "Prodi paling diminati", C_BLUE)
        peminat = (pend["prodi_pilihan_1"].value_counts().head(10)
                   .sort_values().reset_index())
        peminat.columns = ["prodi", "peminat"]
        fig = px.bar(peminat, x="peminat", y="prodi", orientation="h",
                     color="peminat", color_continuous_scale="Viridis",
                     text="peminat", labels={"prodi": "", "peminat": "Peminat"})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        sec("🔥", "Prodi paling kompetitif", C_ORANGE)
        ketat = (pend.groupby("prodi_pilihan_1")
                 .agg(n=("id_pendaftar", "count"),
                      acc=("status_seleksi", lambda s: (s == "Lulus").mean() * 100))
                 .query("n >= 50").nsmallest(10, "acc").sort_values("acc").reset_index())
        fig = px.bar(ketat, x="acc", y="prodi_pilihan_1", orientation="h",
                     color="acc", color_continuous_scale="Sunset",
                     text=ketat["acc"].map("{:.0f}%".format),
                     labels={"acc": "% diterima", "prodi_pilihan_1": ""})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    sec("🫧", "Peminat vs tingkat diterima (bubble = total pendaftar)", C_PURPLE)
    bubble = (pend.groupby(["prodi_pilihan_1", "jurusan"])
              .agg(peminat=("id_pendaftar", "count"),
                   diterima_pct=("status_seleksi", lambda s: 100 * (s == "Lulus").mean()))
              .reset_index())
    fig = px.scatter(bubble, x="peminat", y="diterima_pct", size="peminat",
                     color="jurusan", hover_name="prodi_pilihan_1",
                     size_max=50,
                     labels={"peminat": "Total peminat",
                             "diterima_pct": "% diterima"},
                     color_discrete_map={"Teknik Informatika": C_PURPLE,
                                         "Teknik": C_CYAN, "Kesehatan": C_PINK})
    polish(fig)
    st.plotly_chart(fig, use_container_width=True)

    sec("🗺️", "Peta peminat prodi per tahun", C_TEAL)
    heat = (pend.groupby(["tahun_daftar", "prodi_pilihan_1"]).size()
            .unstack(fill_value=0))
    fig = px.imshow(heat.T, aspect="auto", color_continuous_scale="Turbo",
                    labels=dict(x="Tahun", y="", color="Peminat"),
                    text_auto=True)
    polish(fig)
    st.plotly_chart(fig, use_container_width=True)

    penjelasan("Cara membaca bagian ini", """
**Bubble chart** adalah ringkasan paling kaya: sumbu-X = jumlah peminat,
sumbu-Y = % diterima, ukuran gelembung = volume. Posisi ideal sebuah prodi
secara "kesehatan seleksi" adalah kanan-bawah (banyak peminat, ketat) —
tanda prodi unggulan. Kiri-atas = sepi peminat tapi mudah masuk —
kandidat untuk promosi atau evaluasi daya tampung.

**Heatmap tahun × prodi** menunjukkan evolusi demand. Baris yang "menyala"
setelah tahun tertentu = prodi baru yang langsung diminati (contoh: prodi
S1 Terapan 2022–2023).

**Cara pakai sebagai calon mahasiswa:** bandingkan "diminati" vs "kompetitif" —
selisihnya menunjukkan betapa padat persaingan. Pilihan ke-2 yang cerdas
= prodi dengan peminat moderat tapi daya tampung cukup.
""")

    insight_box("D3 Keperawatan & D3 Teknik Informatika memimpin peminat — konsisten "
                "dengan data riil peminat SNBT 2025 Polindra. Tingkat diterima prodi "
                "populer jauh lebih rendah → strategi <b>pilihan ke-2</b> jadi penentu.", "amber")

# ------------------------------------------------------------------ #
#  TAB 3 — Demografi                                                  #
# ------------------------------------------------------------------ #
with tab3:
    c1, c2, c3 = st.columns([2, 2, 3], gap="large")

    with c1:
        sec("🏫", "Jenis sekolah asal", C_TEAL)
        sekolah = mhs["jenis_sekolah"].value_counts()
        fig = go.Figure(go.Pie(
            labels=sekolah.index, values=sekolah.values, hole=0.58,
            marker=dict(colors=[C_TEAL, C_BLUE, C_AMBER, C_PURPLE]),
            textinfo="label+percent", textposition="outside"))
        polish(fig, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        sec("👫", "Gender per jurusan", C_PINK)
        g = mhs.groupby(["jurusan", "jenis_kelamin"]).size().reset_index(name="n")
        fig = px.bar(g, x="n", y="jurusan", color="jenis_kelamin", orientation="h",
                     barmode="stack", color_discrete_map={"L": C_BLUE, "P": C_PINK},
                     labels={"n": "", "jurusan": "", "jenis_kelamin": ""})
        polish(fig, legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig, use_container_width=True)

    with c3:
        sec("📍", "Top 10 kota asal mahasiswa", C_GREEN)
        kota = mhs["asal_kota"].value_counts().head(10).sort_values().reset_index()
        kota.columns = ["kota", "n"]
        fig = px.bar(kota, x="n", y="kota", orientation="h",
                     color="n", color_continuous_scale="Emrld",
                     text="n", labels={"kota": "", "n": ""})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div class="sec-pill" style="color:#06B6D4">🗺️ '
        '<span style="color:#1E2235">Peta sebaran domisili</span></div>',
        unsafe_allow_html=True)
    KOORD = {
        "Kab. Indramayu": (-6.335, 108.319), "Kab. Cirebon": (-6.850, 108.560),
        "Kota Cirebon": (-6.730, 108.552), "Kab. Majalengka": (-6.830, 108.227),
        "Kab. Kuningan": (-6.980, 108.483), "Kab. Subang": (-6.571, 107.759),
        "Kab. Sumedang": (-6.851, 107.921), "Kab. Karawang": (-6.305, 107.300),
        "Kota Bandung": (-6.914, 107.609), "Kab. Bandung": (-7.023, 107.529),
        "Kota Bekasi": (-6.238, 106.992), "Kab. Bekasi": (-6.238, 107.148),
        "DKI Jakarta": (-6.208, 106.845), "Kab. Brebes": (-6.873, 109.043),
        "Kab. Tegal": (-6.879, 109.140),
    }
    km = mhs["asal_kota"].value_counts().reset_index()
    km.columns = ["kota", "n"]
    km = km[km["kota"].isin(KOORD)].copy()
    km["lat"] = km["kota"].map(lambda k: KOORD[k][0])
    km["lon"] = km["kota"].map(lambda k: KOORD[k][1])
    fig = px.scatter_map(km, lat="lat", lon="lon", size="n", color="n",
                         hover_name="kota", size_max=38, zoom=7.2,
                         center=dict(lat=-6.72, lon=108.28),
                         map_style="open-street-map",
                         color_continuous_scale="Turbo",
                         labels={"n": "Mahasiswa"})
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=430,
                      coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    c4, c5 = st.columns(2, gap="large")
    with c4:
        sec("📋", "Konsentrasi domisili (tabel detail)", C_BLUE)
        kt = mhs["asal_kota"].value_counts().reset_index()
        kt.columns = ["Kota asal", "Mahasiswa"]
        kt["%"] = (100 * kt["Mahasiswa"] / len(mhs)).round(1)
        kt["% kumulatif"] = kt["%"].cumsum().round(1)
        st.dataframe(kt, use_container_width=True, hide_index=True, height=350)
    with c5:
        sec("🧩", "Jalur masuk per jurusan", C_PURPLE)
        jl = (mhs.groupby(["jurusan", "jalur_masuk"]).size()
              .reset_index(name="n"))
        fig = px.bar(jl, x="jurusan", y="n", color="jalur_masuk", barmode="stack",
                     color_discrete_sequence=PALETTE,
                     labels={"n": "Mahasiswa", "jurusan": "", "jalur_masuk": "Jalur"})
        polish(fig, legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig, use_container_width=True)

    penjelasan("Cara membaca bagian ini", """
**Kolom "% kumulatif"** di tabel domisili menunjukkan konsentrasi geografis:
berapa % total mahasiswa yang tercakup oleh N kota teratas. Jika 3 kota
teratas sudah mencakup >50%, kampus sangat bergantung pada satu wilayah —
risiko jika demografi lokal menyusut.

**Donut jenis sekolah** menunjukkan "feeders" utama kampus. Dominasi SMK di
teknik adalah pola khas politeknik vokasi (kesinambungan keahlian);
kesehatan didominasi SMA/MA yang sesuai requirement dasar sains.

**Gender per jurusan** merefleksikan segregasi gender klasik bidang studi:
teknik mesin/pendingin mayoritas laki-laki, keperawatan mayoritas perempuan.
""")

    insight_box("<b>Kab. Indramayu sendirian menyumbang ~1/3 mahasiswa</b> — Polindra sangat "
                "lokal. Teknik didominasi lulusan SMK + laki-laki; Kesehatan didominasi "
                "SMA/MA + perempuan. Peluang besar: ekspansi brand ke luar Ciayumajakuning.", "green")

# ------------------------------------------------------------------ #
#  TAB 4 — Akademik                                                   #
# ------------------------------------------------------------------ #
with tab4:
    c1, c2 = st.columns(2, gap="large")

    with c1:
        sec("🎻", "Distribusi IPK per jurusan", C_BLUE)
        fig = go.Figure()
        colors_j = dict(zip(sorted(mhs["jurusan"].unique()),
                            [C_BLUE, C_PINK, C_TEAL]))
        for jur, sub in mhs.groupby("jurusan"):
            fig.add_trace(go.Violin(
                x=sub["ipk"], name=jur, line_color=colors_j[jur],
                fillcolor=colors_j[jur], opacity=0.55, meanline_visible=True,
                orientation="h", box_visible=True))
        polish(fig, showlegend=False)
        fig.update_xaxes(range=[0.8, 4.1], title="IPK")
        st.plotly_chart(fig, use_container_width=True)

        sec("🌡️", "Heatmap dropout rate (jurusan × sekolah)", C_RED)
        do_h = (mhs.groupby(["jurusan", "jenis_sekolah"])["status_mahasiswa"]
                .apply(lambda s: 100 * (s == "Drop Out").mean()).unstack())
        fig = px.imshow(do_h, aspect="auto", text_auto=".1f",
                        color_continuous_scale="RdYlGn_r",
                        labels=dict(x="Jenis sekolah", y="", color="DO %"))
        polish(fig)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        sec("🔬", "Korelasi: nilai rapor masuk → IPK", C_PURPLE)
        samp = mhs_x.dropna(subset=["nilai_rapor", "ipk"])
        corr = samp["nilai_rapor"].corr(samp["ipk"])
        fig = px.scatter(samp.sample(min(2000, len(samp)), random_state=7),
                         x="nilai_rapor", y="ipk", color="jurusan",
                         opacity=0.5, trendline="ols", trendline_scope="overall",
                         labels={"nilai_rapor": "Nilai rapor saat mendaftar",
                                 "ipk": "IPK saat ini", "jurusan": ""},
                         color_discrete_map={"Teknik Informatika": C_PURPLE,
                                             "Teknik": C_CYAN, "Kesehatan": C_PINK})
        polish(fig, legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Korelasi Pearson r = {corr:.2f} — semakin dekat ke ±1 semakin kuat hubungannya")

        sec("⭐", "Rata-rata IPK per prodi", C_AMBER)
        ipk_p = mhs.groupby("prodi")["ipk"].mean().sort_values().reset_index()
        fig = px.bar(ipk_p, x="ipk", y="prodi", orientation="h",
                     color="ipk", color_continuous_scale="Purp",
                     text=ipk_p["ipk"].map("{:.2f}".format),
                     labels={"prodi": "", "ipk": ""})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        fig.update_xaxes(range=[2.5, 3.8])
        st.plotly_chart(fig, use_container_width=True)

    sec("📉", "Trajektori IP per semester per status mahasiswa", C_RED)
    traj = (khs_x.groupby(["semester", "status_mahasiswa"])["ip_semester"]
            .mean().reset_index())
    fig = px.line(traj, x="semester", y="ip_semester", color="status_mahasiswa",
                  markers=True, labels={"semester": "Semester",
                                        "ip_semester": "Rata-rata IP",
                                        "status_mahasiswa": "Status"},
                  color_discrete_map={"Lulus": C_GREEN, "Aktif": C_BLUE,
                                      "Cuti": C_AMBER, "Drop Out": C_RED})
    fig.update_traces(line=dict(width=3.5), marker=dict(size=8))
    polish(fig, legend=dict(orientation="h", y=1.15))
    st.plotly_chart(fig, use_container_width=True)

    penjelasan("Cara membaca bagian ini", """
**Violin plot** = distribusi IPK penuh per jurusan. Lebar "biola" = seberapa
banyak mahasiswa di rentang IPK itu; garis tengah = median; kotak = rentang
kuartil (IQR). Lebih kaya dari rata-rata tunggal — kelihatan ekor panjang
(mahasiswa ber-IPK rendah) di tiap jurusan.

**Scatter rapor → IPK** menjawab pertanyaan strategis: *apakah nilai masuk
memprediksi performa di kampus?* Garis tren (OLS) menunjukkan arah hubungan.
r positif → nilai rapor memang berkorelasi dengan IPK, meski lemah-sedang
(banyak faktor lain menentukan IPK).

**Heatmap dropout** menunjukkan kombinasi jurusan × asal sekolah paling
berisiko. Perhatikan misalnya lulusan MA di prodi teknik — background
keahlian yang kurang sesuai bisa memperbesar risiko DO.

**Trajektori IP per semester** adalah analisis longitudinal: garis mahasiswa
**Drop Out menurun tajam sejak semester 1** — mereka tidak "tiba-tiba DO",
sinyalnya sudah kelihatan jauh sebelumnya. Inilah dasar sistem early-warning:
flag mahasiswa dengan IP semester 1 < 2,5 untuk pembinaan dini.

⚠️ **Caveat penting:** korelasi ≠ kausalitas. Dan pada data sintetis, pola
ini sengaja dimodelkan — di data riil, kekuatan hubungannya bisa beda.
""")

    insight_box("Mahasiswa jalur <b>SNMPN (seleksi rapor) ber-IPK tertinggi</b> — "
                "nilai rapor terbukti prediktor performa akademik yang baik. Dropout "
                "terkonsentrasi di angkatan muda → 2 tahun pertama periode kritis retensi.", "blue")

# ------------------------------------------------------------------ #
#  TAB 5 — Prediktif & Segmen                                         #
# ------------------------------------------------------------------ #
with tab5:
    c1, c2 = st.columns(2, gap="large")

    with c1:
        sec("📈", "Proyeksi pendaftar 2026–2028", C_PURPLE)
        tren_f = pend.groupby("tahun_daftar").size().reset_index(name="n")
        X = sm.add_constant(tren_f["tahun_daftar"])
        ols = sm.OLS(tren_f["n"], X).fit()
        fut = pd.DataFrame({"tahun_daftar": [2026, 2027, 2028]})
        pred = ols.get_prediction(sm.add_constant(fut)).summary_frame(alpha=0.1)
        fut["pred"], fut["lo"], fut["hi"] = (pred["mean"].round(0).astype(int),
                                           pred["obs_ci_lower"], pred["obs_ci_upper"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tren_f["tahun_daftar"], y=tren_f["n"],
                                 mode="lines+markers", name="Aktual",
                                 line=dict(color=C_BLUE, width=3.5),
                                 marker=dict(size=9)))
        fig.add_trace(go.Scatter(
            x=list(fut["tahun_daftar"]) + list(fut["tahun_daftar"])[::-1],
            y=list(fut["hi"]) + list(fut["lo"])[::-1], fill="toself",
            fillcolor="rgba(139,92,246,.15)", line=dict(width=0),
            name="Interval 90%", hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=fut["tahun_daftar"], y=fut["pred"],
                                 mode="lines+markers", name="Proyeksi",
                                 line=dict(color=C_PURPLE, width=3, dash="dash"),
                                 marker=dict(size=9, symbol="diamond")))
        polish(fig, legend=dict(orientation="h", y=1.14),
               yaxis_title="Pendaftar")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Model: regresi linier OLS pada tren 2019–2025 (filter ikut aktif) "
                   "— proyeksi berguna sebagai baseline, bukan kepastian.")

        sec("🤖", "Faktor paling memprediksi dropout (Random Forest)", C_RED)
        df_m = mhs_x.dropna(subset=["nilai_rapor"]).copy()
        df_m["do"] = (df_m["status_mahasiswa"] == "Drop Out").astype(int)
        # fitur yang tersedia di akhir semester 1 — skenario early-warning nyata
        ip_smt1 = khs[khs["semester"] == 1].set_index("nim")["ip_semester"]
        df_m["ip_semester_1"] = df_m["nim"].map(ip_smt1)
        df_m = df_m.dropna(subset=["ip_semester_1"])
        feats = pd.get_dummies(
            df_m[["nilai_rapor", "ip_semester_1", "jenis_kelamin", "jenis_sekolah",
                  "jurusan", "jalur_masuk", "beasiswa_kip"]], drop_first=True)
        Xtr, Xte, ytr, yte = train_test_split(
            feats, df_m["do"], test_size=0.3, random_state=7,
            stratify=df_m["do"])
        rf = RandomForestClassifier(n_estimators=200, max_depth=6,
                                    random_state=7, n_jobs=-1)
        rf.fit(Xtr, ytr)
        auc = roc_auc_score(yte, rf.predict_proba(Xte)[:, 1])
        imp = (pd.Series(rf.feature_importances_, index=feats.columns)
               .nlargest(10).sort_values().reset_index())
        imp.columns = ["fitur", "penting"]
        fig = px.bar(imp, x="penting", y="fitur", orientation="h",
                     color="penting", color_continuous_scale="Sunset",
                     text=imp["penting"].map("{:.2f}".format),
                     labels={"fitur": "", "penting": "Feature importance"})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"ROC-AUC test set: **{auc:.2f}** — model dilatih hanya dari fitur "
                   "yang tersedia di akhir semester 1 (skenario early-warning nyata). "
                   "Semester-1 IP biasanya prediktor terkuat.")

    with c2:
        sec("🧩", "Segmentasi mahasiswa (K-Means, 4 persona)", C_TEAL)
        seg = mhs_x.dropna(subset=["nilai_rapor"]).copy()
        n_sem = khs_x.groupby("nim")["semester"].max()
        seg["semester_tempuh"] = seg["nim"].map(n_sem)
        Xs = StandardScaler().fit_transform(
            seg[["nilai_rapor", "ipk", "semester_tempuh"]])
        seg["cluster"] = KMeans(n_clusters=4, random_state=7,
                                n_init=10).fit_predict(Xs)
        cent = seg.groupby("cluster")[["nilai_rapor", "ipk"]].mean()
        order = (cent["nilai_rapor"] + cent["ipk"] * 20).sort_values()
        persona_map = {}
        for rank, cid in enumerate(order.index):
            persona_map[cid] = ["🟥 Berisiko / Butuh Bimbingan", "🟧 Rata-rata",
                                "🟦 Stabil", "🟩 Bintang / Unggulan"][rank]
        seg["persona"] = seg["cluster"].map(persona_map)

        fig = px.scatter(seg.sample(min(2200, len(seg)), random_state=7),
                         x="nilai_rapor", y="ipk", color="persona",
                         opacity=0.55,
                         color_discrete_map={"🟩 Bintang / Unggulan": C_GREEN,
                                             "🟦 Stabil": C_BLUE,
                                             "🟧 Rata-rata": C_AMBER,
                                             "🟥 Berisiko / Butuh Bimbingan": C_RED},
                         labels={"nilai_rapor": "Nilai rapor saat masuk",
                                 "ipk": "IPK saat ini", "persona": ""})
        polish(fig, legend=dict(orientation="h", y=1.16))
        st.plotly_chart(fig, use_container_width=True)

        prof = (seg.groupby("persona")
                .agg(n=("nim", "count"), rapor=("nilai_rapor", "mean"),
                     ipk=("ipk", "mean"),
                     do_pct=("status_mahasiswa",
                             lambda s: 100 * (s == "Drop Out").mean()))
                .round(2).reset_index())
        prof.columns = ["Persona", "Jumlah", "Rata rapor", "Rata IPK", "% DO"]
        st.dataframe(prof, use_container_width=True, hide_index=True)

    penjelasan("Cara membaca bagian ini", """
**Forecast (OLS + interval 90%)** memproyeksikan tren historis ke depan.
Interval lebar di tahun-tahun berikutnya = ketidakpastian tumbuh — wajar,
model hanya "melanjutkan pola", tidak tahu kebijakan masa depan (prodi baru,
kuota, dsb.). Dipakai sebagai *baseline* perencanaan daya tampung.

**Random Forest feature importance** menjawab "faktor mana yang paling
menentukan dropout?" — pelengkap regresi logistik (notebook 02): logistik
lebih interpretable (odds ratio), RF menangkap pola non-linier. ROC-AUC
mengukur kemampuan model membedakan DO vs bukan DO.

**K-Means segmentation** mengelompokkan mahasiswa jadi 4 persona berdasarkan
nilai rapor, IPK, dan semester tempuh — teknik yang sama dipakai untuk
segmentasi customer/produk di industri. Persona bisa dipakai untuk program
berbeda per segmen (beasiswa untuk "Bintang", mentoring untuk "Berisiko").
""")

    insight_box("Ini tab paling 'next level': <b>forecast → prediksi demand</b>, "
                "<b>ML → siapa yang berisiko DO</b>, <b>clustering → segmen mahasiswa</b>. "
                "Tiga skill ini yang membedakan 'analyst yang bikin chart' dari "
                "'analyst yang bikin keputusan'.", "green")

# ------------------------------------------------------------------ #
#  TAB 6 — Eksplorasi Data                                            #
# ------------------------------------------------------------------ #
with tab6:
    sec("🔍", "Eksplorasi data interaktif", C_PURPLE)
    st.caption("Bangun tabel analisis sendiri: pilih tabel, dimensi, dan metrik.")

    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        tabel_pilih = st.selectbox("Tabel", ["pendaftar", "mahasiswa"])
    with ec2:
        base = pend if tabel_pilih == "pendaftar" else mhs
        dims = st.multiselect("Dimensi (group by)", base.columns.tolist(),
                              default=["jurusan"])
    with ec3:
        metrik = st.selectbox("Metrik", ["Jumlah baris", "Rata-rata skor_seleksi",
                                         "Rata-rata IPK", "% Drop Out"])

    if dims:
        g = base.groupby(dims)
        if metrik == "Jumlah baris":
            res = g.size().reset_index(name="jumlah")
        elif metrik == "Rata-rata skor_seleksi":
            res = g["skor_seleksi"].mean().round(2).reset_index(
                name="rata_skor") if "skor_seleksi" in base.columns else None
            if res is None:
                st.warning("Kolom skor_seleksi tidak ada di tabel mahasiswa.")
                res = g.size().reset_index(name="jumlah")
        elif metrik == "Rata-rata IPK":
            res = g["ipk"].mean().round(2).reset_index(
                name="rata_ipk") if "ipk" in base.columns else None
            if res is None:
                st.warning("Kolom ipk tidak ada di tabel pendaftar.")
                res = g.size().reset_index(name="jumlah")
        else:
            res = (g["status_mahasiswa"]
                   .apply(lambda s: round(100 * (s == "Drop Out").mean(), 1))
                   .reset_index(name="dropout_pct")) \
                if "status_mahasiswa" in base.columns else \
                g.size().reset_index(name="jumlah")
        st.dataframe(res, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download hasil (CSV)", res.to_csv(index=False),
                           "hasil_eksplorasi.csv", "text/csv")

    st.divider()
    sec("🗃️", "Pratinjau data mentah", C_TEAL)
    pv1, pv2 = st.columns(2)
    with pv1:
        st.markdown("**pendaftar** (100 baris pertama)")
        st.dataframe(pend.head(100), use_container_width=True, height=300,
                     hide_index=True)
    with pv2:
        st.markdown("**mahasiswa** (100 baris pertama)")
        st.dataframe(mhs.head(100), use_container_width=True, height=300,
                     hide_index=True)

    penjelasan("Tentang dataset ini", """
Dataset terdiri dari **2 tabel relasional**:

- `pendaftar` (±17,9 ribu baris): satu baris = satu pendaftar PMB.
  Memuat jalur masuk, pilihan prodi, demografi, nilai rapor/ujian,
  dan status tiap tahap funnel (lulus → daftar ulang).
- `mahasiswa` (±6,3 ribu baris): subset yang daftar ulang — memuat
  NIM, prodi final, beasiswa KIP, IPK, dan status akademik.

**Relasi:** `mahasiswa.id_pendaftar → pendaftar.id_pendaftar` (one-to-one,
karena setiap mahasiswa lahir dari satu pendaftar).

**Sumber:** data **sintetis** yang digenerate programatik
(`src/generate_data.py`, seed=42) menggunakan struktur prodi riil Polindra
(polindra.ac.id), proporsi demografi wilayah Ciayumajakuning (BPS), dan
mekanisme seleksi per-kuota-jalur yang meniru kebijakan nyata: SNMPN/SBMPN
era 2019–2023 → SNBP/SNBT era 2024–2025 (transisi SNPMB).
Detail per kolom: `docs/DATA_DICTIONARY.md`. Daftar sumber: `docs/SUMBER_DATA.md`.
""")

st.markdown("---")
st.caption("🎓 PMB Polindra Analytics · dataset sintetis untuk portofolio · "
           "Streamlit + Plotly")
