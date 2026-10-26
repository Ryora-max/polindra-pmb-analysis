"""
Dashboard Analisis PMB Politeknik Negeri Indramayu.
Jalankan:  streamlit run dashboard/app.py
"""
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
#  Page config                                                        #
# ------------------------------------------------------------------ #
st.set_page_config(
    page_title="PMB Polindra Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Clean minimal palette: satu aksen biru + netral ----
# Warna hanya dipakai saat bermakna (merah=risiko, hijau=positif, amber=perhatian)
C_BLUE, C_CYAN, C_TEAL = "#2563EB", "#0E7490", "#0F766E"
C_GREEN, C_AMBER, C_ORANGE = "#16A34A", "#D97706", "#475569"
C_PINK, C_PURPLE, C_RED = "#B05A78", "#1E40AF", "#DC2626"
PALETTE = ["#2563EB", "#94A3B8", "#0E7490", "#475569",
           "#1E40AF", "#A5B4FC", "#64748B", "#CBD5E1"]
JURUSAN_COLOR = {"Teknik Informatika": "#1E40AF", "Teknik": "#0E7490",
                 "Kesehatan": "#64748B"}

st.markdown("""
<style>
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1280px;}
    [data-testid="stSidebar"] {background: #F8FAFC;}
    [data-testid="stSidebar"] * {color: #334155 !important;}
    [data-testid="stSidebar"] .stMultiSelect label {font-weight: 600;}

    /* ---------- Header ---------- */
    .hero {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-left: 5px solid #2563EB;
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        margin: 0 0 1.4rem 0;
        color: #1F2937;
    }
    .hero h1 {margin: 0; font-size: 1.55rem; font-weight: 800; letter-spacing:.2px;}
    .hero p  {margin: .35rem 0 0 0; font-size: .95rem; color: #64748B;}

    /* ---------- KPI cards ---------- */
    .kpi {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-top: 3px solid #2563EB;
        border-radius: 10px;
        padding: 1rem 1.1rem .9rem 1.1rem;
        height: 100%;
    }
    .kpi .label {font-size: .74rem; font-weight: 700; color:#64748B;
                 text-transform: uppercase; letter-spacing: .6px;}
    .kpi .value {font-size: 1.7rem; font-weight: 800; color:#111827; line-height: 1.15;}
    .kpi .sub   {font-size: .78rem; color:#94A3B8; margin-top: .15rem;}

    /* ---------- Section pills & insight boxes ---------- */
    .sec-pill {
        display:inline-block; font-size:1.02rem; font-weight:800;
        color:#1F2937; margin:.6rem 0 .3rem 0;
        padding-bottom:.2rem; border-bottom:2px solid #E5E7EB;
    }
    .sec-pill::before {content:"●"; margin-right:.45rem; font-size:.85rem;}
    .insight {
        border-radius: 0 10px 10px 0;
        padding: .8rem 1rem;
        font-size: .88rem;
        margin: .6rem 0;
        background: #F8FAFC;
        border: 1px solid #E5E7EB;
        border-left: 3px solid;
        color: #334155;
    }
    .insight.blue  {border-left-color:#2563EB;}
    .insight.green {border-left-color:#16A34A;}
    .insight.amber {border-left-color:#D97706;}
    .insight b {color:#111827; font-weight:700;}

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {gap: .4rem; border-bottom:1px solid #E5E7EB;}
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        padding: .45rem .9rem; font-weight: 600; color: #64748B;
        border-bottom: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #2563EB !important;
        border-bottom: 2px solid #2563EB !important;
    }

    [data-testid="stExpander"] {background: #FFFFFF; border-radius: 10px;
        border: 1px solid #E5E7EB;}
    [data-testid="stDataFrame"] {border-radius: 10px; overflow:hidden;
        border:1px solid #E5E7EB;}
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

# ------------------------------------------------------------------ #
#  Helpers                                                            #
# ------------------------------------------------------------------ #
def titik(x):
    """Format ribuan ala Indonesia: 17900 -> '17.900'."""
    return f"{x:,.0f}".replace(",", ".")

BASE_LAYOUT = dict(
    font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#1F2937"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=46, b=10),
    title=dict(font=dict(size=15, color="#1F2937")),
    colorway=PALETTE,
)

def polish(fig, **kw):
    fig.update_layout(**{**BASE_LAYOUT, **kw})
    fig.update_xaxes(showgrid=False, zeroline=False, automargin=True)
    fig.update_yaxes(gridcolor="#EEF2F6", zeroline=False, automargin=True,
                     title_standoff=10)
    fig.update_traces(cliponaxis=False, selector=dict(type="bar"))
    fig.update_layout(uniformtext_minsize=9, uniformtext_mode="hide")
    return fig

def chart(fig):
    st.plotly_chart(fig, width="stretch")

def table(df, **kw):
    st.dataframe(df, width="stretch", hide_index=True, **kw)

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
tahun_pilih = st.sidebar.multiselect("Tahun Pendaftaran", tahun_list,
                                     default=tahun_list)
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

if pend.empty or mhs.empty:
    st.warning("Filter menghasilkan data kosong — pilih minimal satu tahun, "
               "jurusan, dan jalur masuk di sidebar.")
    st.stop()

mhs_x = mhs.merge(pend[["id_pendaftar", "nilai_rapor", "skor_seleksi"]],
                  on="id_pendaftar", how="left")
khs_x = khs.merge(mhs[["nim", "status_mahasiswa"]], on="nim", how="left")

# ------------------------------------------------------------------ #
#  Model & segmentasi — dilatih pada dataset PENUH (cached),          #
#  stabil terhadap perubahan filter sidebar                            #
# ------------------------------------------------------------------ #
@st.cache_data
def train_dropout_model():
    m_full = mahasiswa.merge(
        pendaftar[["id_pendaftar", "nilai_rapor"]],
        on="id_pendaftar", how="left").dropna(subset=["nilai_rapor"])
    ip1 = khs[khs["semester"] == 1].set_index("nim")["ip_semester"]
    m_full["ip_semester_1"] = m_full["nim"].map(ip1)
    m_full = m_full.dropna(subset=["ip_semester_1"])
    feats = pd.get_dummies(
        m_full[["nilai_rapor", "ip_semester_1", "jenis_kelamin",
                "jenis_sekolah", "jurusan", "jalur_masuk",
                "beasiswa_kip"]], drop_first=True)
    y = (m_full["status_mahasiswa"] == "Drop Out").astype(int)
    Xtr, Xte, ytr, yte = train_test_split(
        feats, y, test_size=0.3, random_state=7, stratify=y)
    rf = RandomForestClassifier(n_estimators=200, max_depth=6,
                                random_state=7, n_jobs=-1).fit(Xtr, ytr)
    prob = rf.predict_proba(Xte)[:, 1]
    auc = roc_auc_score(yte, prob)
    imp = (pd.Series(rf.feature_importances_, index=feats.columns)
           .nlargest(10).sort_values().reset_index())
    imp.columns = ["fitur", "penting"]
    return auc, imp, yte.to_numpy(), prob

@st.cache_data
def segmentasi_mahasiswa():
    m_full = mahasiswa.merge(
        pendaftar[["id_pendaftar", "nilai_rapor"]],
        on="id_pendaftar", how="left").dropna(subset=["nilai_rapor"])
    n_sem = khs.groupby("nim")["semester"].max()
    m_full["semester_tempuh"] = m_full["nim"].map(n_sem)
    m_full = m_full.dropna(subset=["semester_tempuh"])
    Xs = StandardScaler().fit_transform(
        m_full[["nilai_rapor", "ipk", "semester_tempuh"]])
    m_full["cluster"] = KMeans(n_clusters=4, random_state=7,
                               n_init=10).fit_predict(Xs)
    cent = m_full.groupby("cluster")[["nilai_rapor", "ipk"]].mean()
    order = (cent["nilai_rapor"] + cent["ipk"] * 20).sort_values()
    nama = ["🟥 Berisiko / Butuh Bimbingan", "🟧 Rata-rata",
            "🟦 Stabil", "🟩 Bintang / Unggulan"]
    m_full["persona"] = m_full["cluster"].map(
        {cid: nama[rank] for rank, cid in enumerate(order.index)})
    return m_full

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

kpis = [
    ("Total Pendaftar", titik(n_pend), f"{len(tahun_pilih)} tahun pendaftaran"),
    ("Lulus Seleksi", titik(n_lulus), f"{100*n_lulus/max(n_pend,1):.1f}% dari pendaftar"),
    ("Daftar Ulang", titik(n_reg), f"{100*n_reg/max(n_lulus,1):.1f}% dari yang lulus"),
    ("Rata-rata IPK", f"{mhs['ipk'].mean():.2f}".replace(".", ","),
     "mahasiswa terfilter"),
    ("Dropout Rate", f"{100*n_do/max(len(mhs),1):.1f}%".replace(".", ","),
     f"{titik(n_do)} mahasiswa"),
]
for col, (label, val, sub) in zip(st.columns(5), kpis):
    col.markdown(f"""
    <div class="kpi">
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
        for col, color in [("Pendaftar", C_BLUE), ("Lulus", C_GREEN),
                           ("Registrasi", C_ORANGE)]:
            fig.add_trace(go.Scatter(
                x=tren["tahun_daftar"], y=tren[col], name=col,
                mode="lines+markers",
                line=dict(width=3.5, color=color), marker=dict(size=9),
                fill="tozeroy" if col == "Pendaftar" else None,
                fillcolor="rgba(59,130,246,.10)"))
        polish(fig, legend=dict(orientation="h", y=1.14))
        chart(fig)

        sec("🔥", "Tingkat keketatan seleksi", C_RED)
        ketat_t = (pend.groupby("tahun_daftar")["status_seleksi"]
                   .apply(lambda s: 100 * (s == "Lulus").mean()).reset_index())
        fig = go.Figure(go.Scatter(
            x=ketat_t["tahun_daftar"], y=ketat_t["status_seleksi"],
            mode="lines+markers+text",
            text=ketat_t["status_seleksi"].map("{:.0f}%".format),
            textposition="top center",
            line=dict(width=3.5, color=C_RED), marker=dict(size=10),
            fill="tozeroy", fillcolor="rgba(220,38,38,.07)"))
        polish(fig, yaxis_title="% lulus seleksi")
        chart(fig)

    with c2:
        sec("🧲", "Funnel konversi", C_PURPLE)
        fig = go.Figure(go.Funnel(
            y=["Pendaftar", "Lulus Seleksi", "Daftar Ulang"],
            x=[n_pend, n_lulus, n_reg],
            textinfo="value+percent initial",
            marker=dict(color=["#1E40AF", "#3B82F6", "#93C5FD"]),
            connector=dict(line=dict(color="#E5E7EB", width=2))))
        polish(fig)
        chart(fig)

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
        chart(fig)

    sec("📣", "Kanal akuisisi pendaftar per tahun", C_ORANGE)
    kanal = (pend.groupby(["tahun_daftar", "sumber_informasi"]).size()
             .reset_index(name="n"))
    fig = px.area(kanal, x="tahun_daftar", y="n", color="sumber_informasi",
                  color_discrete_sequence=PALETTE,
                  labels={"n": "Pendaftar", "tahun_daftar": "Tahun",
                          "sumber_informasi": "Kanal"})
    polish(fig, legend=dict(orientation="h", y=-0.18))
    chart(fig)

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

    if len(tren) >= 2:
        _growth = 100 * (tren["Pendaftar"].iloc[-1] / tren["Pendaftar"].iloc[0] - 1)
        _lulus_first = 100 * tren["Lulus"].iloc[0] / tren["Pendaftar"].iloc[0]
        _lulus_last = 100 * tren["Lulus"].iloc[-1] / tren["Pendaftar"].iloc[-1]
        insight_box(
            f"Peminat tumbuh <b>{_growth:.0f}%</b> antara {tren['tahun_daftar'].iloc[0]}–"
            f"{tren['tahun_daftar'].iloc[-1]}. Keketatan naik: lulus seleksi turun dari "
            f"<b>{_lulus_first:.0f}%</b> ke <b>{_lulus_last:.0f}%</b> — peminat tumbuh "
            "jauh lebih cepat daripada daya tampung.", "blue")

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
                     color="peminat", color_continuous_scale="Blues",
                     text="peminat", labels={"prodi": "", "peminat": "Peminat"})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        chart(fig)

    with c2:
        sec("🔥", "Prodi paling kompetitif", C_ORANGE)
        ketat = (pend.groupby("prodi_pilihan_1")
                 .agg(n=("id_pendaftar", "count"),
                      acc=("status_seleksi", lambda s: (s == "Lulus").mean() * 100))
                 .query("n >= 50").nsmallest(10, "acc").sort_values("acc")
                 .reset_index())
        fig = px.bar(ketat, x="acc", y="prodi_pilihan_1", orientation="h",
                     color="acc", color_continuous_scale="Blues",
                     text=ketat["acc"].map("{:.0f}%".format),
                     labels={"acc": "% diterima", "prodi_pilihan_1": ""})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        chart(fig)

    sec("🫧", "Peminat vs tingkat diterima (bubble = total pendaftar)", C_PURPLE)
    bubble = (pend.groupby(["prodi_pilihan_1", "jurusan"])
              .agg(peminat=("id_pendaftar", "count"),
                   diterima_pct=("status_seleksi",
                                 lambda s: 100 * (s == "Lulus").mean()))
              .reset_index())
    fig = px.scatter(bubble, x="peminat", y="diterima_pct", size="peminat",
                     color="jurusan", hover_name="prodi_pilihan_1",
                     size_max=50,
                     labels={"peminat": "Total peminat",
                             "diterima_pct": "% diterima"},
                     color_discrete_map=JURUSAN_COLOR)
    polish(fig)
    chart(fig)

    sec("🗺️", "Peta peminat prodi per tahun", C_TEAL)
    heat = (pend.groupby(["tahun_daftar", "prodi_pilihan_1"]).size()
            .unstack(fill_value=0))
    fig = px.imshow(heat.T, aspect="auto", color_continuous_scale="Blues",
                    labels=dict(x="Tahun", y="", color="Peminat"),
                    text_auto=True)
    polish(fig)
    chart(fig)

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

    _top2 = pend["prodi_pilihan_1"].value_counts().head(2).index.tolist()
    insight_box(f"<b>{' & '.join(_top2)}</b> memimpin peminat — konsisten "
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
            marker=dict(colors=["#2563EB", "#64748B", "#94A3B8", "#CBD5E1"]),
            textinfo="label+percent", textposition="outside"))
        polish(fig, showlegend=False)
        chart(fig)

    with c2:
        sec("👫", "Gender per jurusan", C_PINK)
        g = mhs.groupby(["jurusan", "jenis_kelamin"]).size().reset_index(name="n")
        fig = px.bar(g, x="n", y="jurusan", color="jenis_kelamin", orientation="h",
                     barmode="stack", color_discrete_map={"L": "#2563EB",
                                                          "P": "#94A3B8"},
                     labels={"n": "", "jurusan": "", "jenis_kelamin": ""})
        polish(fig, legend=dict(orientation="h", y=1.15))
        chart(fig)

    with c3:
        sec("📍", "Top 10 kota asal mahasiswa", C_GREEN)
        kota = mhs["asal_kota"].value_counts().head(10).sort_values().reset_index()
        kota.columns = ["kota", "n"]
        fig = px.bar(kota, x="n", y="kota", orientation="h",
                     color="n", color_continuous_scale="Blues",
                     text="n", labels={"kota": "", "n": ""})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        chart(fig)

    sec("🗺️", "Peta sebaran domisili mahasiswa", C_CYAN)
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
    # scatter_geo: peta vektor bawaan Plotly — offline, tanpa request tile eksternal
    fig = px.scatter_geo(km, lat="lat", lon="lon", size="n", color="n",
                         hover_name="kota", size_max=42, scope="asia",
                         color_continuous_scale="Blues",
                         labels={"n": "Mahasiswa"})
    fig.update_geos(visible=False, resolution=50,
                    lataxis_range=[-7.8, -5.6],
                    lonaxis_range=[105.5, 110.5])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=400,
                      coloraxis_showscale=False,
                      paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Inter, Segoe UI, sans-serif",
                                size=13, color="#1E2235"))
    chart(fig)

    c4, c5 = st.columns(2, gap="large")
    with c4:
        sec("📋", "Konsentrasi domisili (tabel detail)", C_BLUE)
        kt = mhs["asal_kota"].value_counts().reset_index()
        kt.columns = ["Kota asal", "Mahasiswa"]
        kt["%"] = (100 * kt["Mahasiswa"] / len(mhs)).round(1)
        kt["% kumulatif"] = kt["%"].cumsum().round(1)
        table(kt, height=350)
    with c5:
        sec("🧩", "Jalur masuk per jurusan", C_PURPLE)
        jl = (mhs.groupby(["jurusan", "jalur_masuk"]).size()
              .reset_index(name="n"))
        fig = px.bar(jl, x="jurusan", y="n", color="jalur_masuk", barmode="stack",
                     color_discrete_sequence=PALETTE,
                     labels={"n": "Mahasiswa", "jurusan": "",
                             "jalur_masuk": "Jalur"})
        polish(fig, legend=dict(orientation="h", y=1.15))
        chart(fig)

    penjelasan("Cara membaca bagian ini", """
**Peta domisili** menampilkan kota asal sebagai gelembung di peta Jawa —
gelembung makin besar = makin banyak mahasiswa. Peta ini memakai peta vektor
bawaan Plotly sehingga tidak memuat tile eksternal.

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

    _top_kota = kt.iloc[0]
    insight_box(f"<b>{_top_kota['Kota asal']} sendirian menyumbang "
                f"{_top_kota['%']:.0f}% mahasiswa</b> — Polindra sangat "
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
        for jur, sub in mhs.groupby("jurusan"):
            warna = JURUSAN_COLOR.get(jur, C_BLUE)
            fig.add_trace(go.Violin(
                x=sub["ipk"], name=jur, line_color=warna,
                fillcolor=warna, opacity=0.55, meanline_visible=True,
                orientation="h", box_visible=True))
        polish(fig, showlegend=False)
        fig.update_xaxes(range=[0.8, 4.1], title="IPK")
        chart(fig)

        sec("🌡️", "Heatmap dropout rate (jurusan × sekolah)", C_RED)
        do_h = (mhs.groupby(["jurusan", "jenis_sekolah"])["status_mahasiswa"]
                .apply(lambda s: 100 * (s == "Drop Out").mean()).unstack())
        fig = px.imshow(do_h, aspect="auto", text_auto=".1f",
                        color_continuous_scale="Reds",
                        labels=dict(x="Jenis sekolah", y="", color="DO %"))
        polish(fig)
        chart(fig)

    with c2:
        sec("🔬", "Korelasi: nilai rapor masuk → IPK", C_PURPLE)
        samp = mhs_x.dropna(subset=["nilai_rapor", "ipk"])
        corr = samp["nilai_rapor"].corr(samp["ipk"])
        fig = px.scatter(samp.sample(min(2000, len(samp)), random_state=7),
                         x="nilai_rapor", y="ipk", color="jurusan",
                         opacity=0.5, trendline="ols", trendline_scope="overall",
                         labels={"nilai_rapor": "Nilai rapor saat mendaftar",
                                 "ipk": "IPK saat ini", "jurusan": ""},
                         color_discrete_map=JURUSAN_COLOR)
        polish(fig, legend=dict(orientation="h", y=1.15))
        chart(fig)
        st.caption(f"Korelasi Pearson r = {corr:.2f} — semakin dekat ke ±1 "
                   "semakin kuat hubungannya")

        sec("⭐", "Rata-rata IPK per prodi", C_AMBER)
        ipk_p = mhs.groupby("prodi")["ipk"].mean().sort_values().reset_index()
        fig = px.bar(ipk_p, x="ipk", y="prodi", orientation="h",
                     color="ipk", color_continuous_scale="Blues",
                     text=ipk_p["ipk"].map("{:.2f}".format),
                     labels={"prodi": "", "ipk": ""})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        fig.update_xaxes(range=[2.5, 3.8])
        chart(fig)

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
    chart(fig)

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
        if len(tren_f) >= 3:
            X = sm.add_constant(tren_f["tahun_daftar"].astype(float))
            ols = sm.OLS(tren_f["n"].astype(float), X).fit()
            fut = pd.DataFrame({"tahun_daftar": [2026., 2027., 2028.]})
            pred = (ols.get_prediction(sm.add_constant(fut))
                    .summary_frame(alpha=0.1))
            fut["pred"] = pred["mean"].round(0).astype(int)
            fut["lo"], fut["hi"] = pred["obs_ci_lower"], pred["obs_ci_upper"]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tren_f["tahun_daftar"], y=tren_f["n"],
                                     mode="lines+markers", name="Aktual",
                                     line=dict(color=C_BLUE, width=3.5),
                                     marker=dict(size=9)))
            fig.add_trace(go.Scatter(
                x=pd.concat([fut["tahun_daftar"],
                             fut["tahun_daftar"][::-1]]),
                y=pd.concat([fut["hi"], fut["lo"][::-1]]),
                fill="toself", fillcolor="rgba(37,99,235,.12)",
                line=dict(width=0), name="Interval 90%", hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=fut["tahun_daftar"], y=fut["pred"],
                                     mode="lines+markers", name="Proyeksi",
                                     line=dict(color=C_PURPLE, width=3,
                                               dash="dash"),
                                     marker=dict(size=9, symbol="diamond")))
            polish(fig, legend=dict(orientation="h", y=1.14),
                   yaxis_title="Pendaftar")
            chart(fig)
            st.caption("Model: regresi linier OLS pada tren historis (filter ikut "
                       "aktif) — proyeksi berguna sebagai baseline, bukan kepastian.")
        else:
            st.info("Butuh minimal 3 tahun data untuk proyeksi — perluas filter "
                    "tahun di sidebar.")

        sec("🤖", "Faktor paling memprediksi dropout (Random Forest)", C_RED)
        auc, imp, y_true, y_prob = train_dropout_model()
        fig = px.bar(imp, x="penting", y="fitur", orientation="h",
                     color="penting", color_continuous_scale="Blues",
                     text=imp["penting"].map("{:.2f}".format),
                     labels={"fitur": "", "penting": "Feature importance"})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        chart(fig)
        st.caption(f"ROC-AUC test set: **{auc:.2f}** — model dilatih pada dataset "
                   "penuh (stabil terhadap filter), hanya dari fitur yang tersedia "
                   "di akhir semester 1 (skenario early-warning nyata).")

        sec("🎚️", "Evaluasi model: geser threshold, lihat trade-off", C_AMBER)
        thr = st.slider("Threshold klasifikasi DO", 0.10, 0.90, 0.50, 0.05,
                        help="Di atas threshold → diprediksi Drop Out. "
                             "Turunkan untuk menangkap lebih banyak calon DO "
                             "(recall naik, tapi false alarm ikut naik).")
        y_hat = (y_prob >= thr).astype(int)
        tp = int(((y_hat == 1) & (y_true == 1)).sum())
        fp = int(((y_hat == 1) & (y_true == 0)).sum())
        fn = int(((y_hat == 0) & (y_true == 1)).sum())
        tn = int(((y_hat == 0) & (y_true == 0)).sum())
        prec = tp / max(tp + fp, 1)
        rec = tp / max(tp + fn, 1)
        f1 = 2 * prec * rec / max(prec + rec, 1e-9)

        m1, m2, m3 = st.columns(3)
        m1.metric("Recall (DO tertangkap)", f"{100*rec:.0f}%")
        m2.metric("Precision (flag tepat)", f"{100*prec:.0f}%")
        m3.metric("F1-score", f"{f1:.2f}")

        cm = pd.DataFrame(
            [[tn, fp], [fn, tp]],
            index=["Aktual: bukan DO", "Aktual: DO"],
            columns=["Prediksi: bukan DO", "Prediksi: DO"])
        fig = px.imshow(cm, text_auto=True, aspect="auto",
                        color_continuous_scale="Blues",
                        labels=dict(color="n"))
        fig.update_layout(height=270)
        polish(fig, coloraxis_showscale=False)
        chart(fig)

    with c2:
        sec("🧩", "Segmentasi mahasiswa (K-Means, 4 persona)", C_TEAL)
        seg = segmentasi_mahasiswa()
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
        chart(fig)

        prof = (seg.groupby("persona")
                .agg(n=("nim", "count"), rapor=("nilai_rapor", "mean"),
                     ipk=("ipk", "mean"),
                     do_pct=("status_mahasiswa",
                             lambda s: 100 * (s == "Drop Out").mean()))
                .round(2).reset_index())
        prof.columns = ["Persona", "Jumlah", "Rata rapor", "Rata IPK", "% DO"]
        table(prof)

    penjelasan("Cara membaca bagian ini", """
**Forecast (OLS + interval 90%)** memproyeksikan tren historis ke depan.
Interval lebar di tahun-tahun berikutnya = ketidakpastian tumbuh — wajar,
model hanya "melanjutkan pola", tidak tahu kebijakan masa depan (prodi baru,
kuota, dsb.). Dipakai sebagai *baseline* perencanaan daya tampung.

**Random Forest feature importance** menjawab "faktor mana yang paling
menentukan dropout?" — pelengkap regresi logistik (notebook 02): logistik
lebih interpretable (odds ratio), RF menangkap pola non-linier. ROC-AUC
mengukur kemampuan model membedakan DO vs bukan DO.

**Threshold slider + confusion matrix** menunjukkan trade-off nyata:
threshold rendah → recall tinggi (hampir semua calon DO ter-flag) tapi
banyak false alarm (mahasiswa aman ikut ter-flag). Threshold tinggi →
kebalikannya. Di konteks early-warning, recall biasanya lebih diutamakan —
lebih baik berlebih membina daripada kecolongan mahasiswa yang DO.
Ini keputusan *bisnis*, bukan cuma statistik.

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
        metrik = st.selectbox("Metrik", ["Jumlah baris",
                                         "Rata-rata skor_seleksi",
                                         "Rata-rata IPK", "% Drop Out"])

    if dims:
        g = base.groupby(dims)
        col_ada = {"Rata-rata skor_seleksi": "skor_seleksi",
                   "Rata-rata IPK": "ipk",
                   "% Drop Out": "status_mahasiswa"}
        need = col_ada.get(metrik)
        res = None
        if need is not None and need not in base.columns:
            st.warning(f"Kolom `{need}` tidak ada di tabel {tabel_pilih}.")
        elif metrik == "Jumlah baris":
            res = g.size().reset_index(name="jumlah")
        elif metrik == "% Drop Out":
            res = (g["status_mahasiswa"]
                   .apply(lambda s: round(100 * (s == "Drop Out").mean(), 1))
                   .reset_index(name="dropout_pct"))
        else:
            res = g[need].mean().round(2).reset_index(name=f"rata_{need}")
        if res is not None:
            table(res)
            st.download_button("⬇️ Download hasil (CSV)",
                               res.to_csv(index=False),
                               "hasil_eksplorasi.csv", "text/csv")

    st.divider()
    sec("🗃️", "Pratinjau data mentah", C_TEAL)
    pv1, pv2 = st.columns(2)
    with pv1:
        st.markdown("**pendaftar** (100 baris pertama)")
        table(pend.head(100), height=300)
    with pv2:
        st.markdown("**mahasiswa** (100 baris pertama)")
        table(mhs.head(100), height=300)

    penjelasan("Tentang dataset ini", """
Dataset terdiri dari **3 tabel relasional**:

- `pendaftar` (±17,9 ribu baris): satu baris = satu pendaftar PMB.
  Memuat jalur masuk, pilihan prodi, demografi, nilai rapor/ujian,
  dan status tiap tahap funnel (lulus → daftar ulang).
- `mahasiswa` (±6,3 ribu baris): subset yang daftar ulang — memuat
  NIM, prodi final, beasiswa KIP, IPK, dan status akademik.
- `khs` (±27 ribu baris): IP per semester tiap mahasiswa — data
  longitudinal untuk analisis trajektori akademik.

**Relasi:** `mahasiswa.id_pendaftar → pendaftar.id_pendaftar` (one-to-one),
`khs.nim → mahasiswa.nim` (many-to-one).

**Sumber:** data **sintetis** yang digenerate programatik
(`src/generate_data.py`, seed=42) menggunakan struktur prodi riil Polindra
(polindra.ac.id), proporsi demografi wilayah Ciayumajakuning (BPS), dan
mekanisme seleksi per-kuota-jalur yang meniru kebijakan nyata: SNMPN/SBMPN
(2019–2023) → SNBP/SNBT (2024–2025) sesuai Permendikbudristek 48/2022.
""")
