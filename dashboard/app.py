"""
Dashboard Analisis PMB Politeknik Negeri Indramayu.
Jalankan:  streamlit run dashboard/app.py
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------ #
#  Page config & theme                                                #
# ------------------------------------------------------------------ #
st.set_page_config(
    page_title="PMB Polindra Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

BLUE, TEAL, AMBER, RED, PURPLE = "#1B5DBF", "#0EA5A4", "#F59E0B", "#E15554", "#7C5CBF"
PALETTE = [BLUE, TEAL, AMBER, RED, PURPLE, "#3B82C4", "#F2C14E", "#4C9F70"]

st.markdown("""
<style>
    /* ---------- Global ---------- */
    .block-container {padding-top: 0rem; padding-bottom: 2rem; max-width: 1250px;}
    [data-testid="stSidebar"] {background: linear-gradient(180deg,#10294F 0%,#16386E 100%);}
    [data-testid="stSidebar"] * {color: #E8EEF8 !important;}
    [data-testid="stSidebar"] .stMultiSelect label {font-weight: 600;}

    /* ---------- Hero banner ---------- */
    .hero {
        background: linear-gradient(120deg, #0F2B5B 0%, #1B5DBF 55%, #0EA5A4 130%);
        border-radius: 18px;
        padding: 2.2rem 2.4rem 1.8rem 2.4rem;
        margin: 1rem 0 1.4rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(15,43,91,.25);
    }
    .hero h1 {margin: 0; font-size: 1.9rem; font-weight: 800; letter-spacing:.3px;}
    .hero p  {margin: .55rem 0 0 0; font-size: 1rem; opacity: .92;}

    /* ---------- KPI cards ---------- */
    .kpi {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.05rem 1.15rem .95rem 1.15rem;
        box-shadow: 0 3px 14px rgba(22,35,59,.07);
        border-top: 4px solid var(--accent, #1B5DBF);
        height: 100%;
    }
    .kpi .label {font-size: .82rem; font-weight: 700; color: #5B6B8C;
                 text-transform: uppercase; letter-spacing: .6px;}
    .kpi .value {font-size: 1.85rem; font-weight: 800; color: #16233B; line-height: 1.15;}
    .kpi .sub   {font-size: .8rem; color: #8A97B2; margin-top: .15rem;}

    /* ---------- Section titles & insight boxes ---------- */
    .sec-title {font-size: 1.12rem; font-weight: 800; color: #16233B;
                margin: .4rem 0 .2rem 0;}
    .insight {
        background: #EBF3FF;
        border-left: 4px solid #1B5DBF;
        border-radius: 0 10px 10px 0;
        padding: .75rem 1rem;
        font-size: .88rem;
        color: #25406E;
        margin-top: .4rem;
    }
    .insight b {color: #1B5DBF;}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {gap: .4rem;}
    .stTabs [data-baseweb="tab"] {
        background: #E8EEF8; border-radius: 10px 10px 0 0;
        padding: .45rem 1.1rem; font-weight: 700; color: #44557A;
    }
    .stTabs [aria-selected="true"] {background: #1B5DBF !important; color: white !important;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------ #
#  Data                                                               #
# ------------------------------------------------------------------ #
@st.cache_data
def load_data():
    return (pd.read_csv("data/raw/pendaftar.csv"),
            pd.read_csv("data/raw/mahasiswa.csv"))

pendaftar, mahasiswa = load_data()

def titik(x):
    """Format ribuan ala Indonesia: 17900 -> '17.900'."""
    return f"{x:,.0f}".replace(",", ".")

BASE_LAYOUT = dict(
    font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#16233B"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=46, b=10),
    title=dict(font=dict(size=15, color="#16233B")),
    colorway=PALETTE,
)

def polish(fig, **kw):
    fig.update_layout(**{**BASE_LAYOUT, **kw})
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#E7EDF7", zeroline=False)
    return fig

def insight_box(text):
    st.markdown(f'<div class="insight">💡 {text}</div>', unsafe_allow_html=True)

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
st.sidebar.caption("📊 Dataset sintetis · simulasi berbasis struktur prodi riil Polindra")

pend = pendaftar[pendaftar["tahun_daftar"].isin(tahun_pilih)
                 & pendaftar["jurusan"].isin(jurusan_pilih)
                 & pendaftar["jalur_masuk"].isin(jalur_pilih)]
mhs = mahasiswa[mahasiswa["angkatan"].isin(tahun_pilih)
                & mahasiswa["jurusan"].isin(jurusan_pilih)
                & mahasiswa["jalur_masuk"].isin(jalur_pilih)]

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

k1, k2, k3, k4 = st.columns(4)
kpis = [
    ("📥 Total Pendaftar", titik(n_pend), f"{len(tahun_pilih)} tahun pendaftaran", BLUE),
    ("✅ Lulus Seleksi", titik(n_lulus), f"{100*n_lulus/max(n_pend,1):.1f}% dari pendaftar", TEAL),
    ("📝 Daftar Ulang", titik(n_reg), f"{100*n_reg/max(n_lulus,1):.1f}% dari yang lulus", AMBER),
    ("📊 Rata-rata IPK", f"{mhs['ipk'].mean():.2f}".replace(".", ",") if len(mhs) else "-",
     "seluruh mahasiswa terfilter", PURPLE),
]
for col, (label, val, sub, color) in zip([k1, k2, k3, k4], kpis):
    col.markdown(f"""
    <div class="kpi" style="--accent:{color}">
        <div class="label">{label}</div>
        <div class="value">{val}</div>
        <div class="sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

st.write("")
tab1, tab2, tab3, tab4 = st.tabs(["📈 Tren & Funnel", "🏫 Program Studi",
                                "🗺️ Demografi", "📊 Akademik"])

# ------------------------------------------------------------------ #
#  TAB 1 — Tren & funnel                                              #
# ------------------------------------------------------------------ #
with tab1:
    c1, c2 = st.columns([3, 2], gap="large")

    with c1:
        st.markdown('<div class="sec-title">Pertumbuhan funnel 2019–2025</div>',
                    unsafe_allow_html=True)
        tren = (pend.groupby("tahun_daftar")
                .agg(Pendaftar=("id_pendaftar", "count"),
                     Lulus=("status_seleksi", lambda s: (s == "Lulus").sum()),
                     Registrasi=("daftar_ulang", lambda s: (s == "Ya").sum()))
                .reset_index())
        fig = go.Figure()
        for col, color in [("Pendaftar", BLUE), ("Lulus", TEAL), ("Registrasi", AMBER)]:
            fig.add_trace(go.Scatter(
                x=tren["tahun_daftar"], y=tren[col], name=col, mode="lines+markers",
                line=dict(width=3, color=color), marker=dict(size=8),
                fill="tozeroy" if col == "Pendaftar" else None,
                fillcolor="rgba(27,93,191,.08)"))
        polish(fig, legend=dict(orientation="h", y=1.14))
        st.plotly_chart(fig, use_container_width=True)
        insight_box("Peminat tumbuh <b>~170%</b> dalam 6 tahun — lonjakan 2022 berbarengan "
                    "dibukanya prodi S1 Terapan baru. Daya tampung flat → seleksi makin ketat.")

    with c2:
        st.markdown('<div class="sec-title">Funnel konversi</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Funnel(
            y=["Pendaftar", "Lulus Seleksi", "Daftar Ulang"],
            x=[n_pend, n_lulus, n_reg],
            textinfo="value+percent initial",
            marker=dict(color=[BLUE, TEAL, AMBER]),
            connector=dict(line=dict(color="#C7D4EA", width=2))))
        polish(fig)
        st.plotly_chart(fig, use_container_width=True)

        jalur_f = (pend.groupby("jalur_masuk")
                   .agg(n=("id_pendaftar", "count"),
                        reg=("daftar_ulang", lambda s: (s == "Ya").sum()))
                   .assign(rate=lambda d: 100 * d["reg"] / d["n"]).reset_index())
        fig = px.bar(jalur_f, x="rate", y="jalur_masuk", orientation="h",
                     color="rate", color_continuous_scale=["#Bcd2f2", BLUE],
                     text=jalur_f["rate"].map("{:.1f}%".format),
                     labels={"rate": "", "jalur_masuk": ""})
        fig.update_traces(textposition="outside")
        polish(fig, showlegend=False, coloraxis_showscale=False,
               title=dict(text="Conversion ke mahasiswa per jalur", font=dict(size=13)))
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------ #
#  TAB 2 — Program studi                                              #
# ------------------------------------------------------------------ #
with tab2:
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown('<div class="sec-title">Prodi paling diminati</div>',
                    unsafe_allow_html=True)
        peminat = (pend["prodi_pilihan_1"].value_counts().head(10)
                   .sort_values().reset_index())
        peminat.columns = ["prodi", "peminat"]
        fig = px.bar(peminat, x="peminat", y="prodi", orientation="h",
                     color="peminat", color_continuous_scale=["#9CC0EE", BLUE],
                     text="peminat", labels={"prodi": "", "peminat": "Peminat"})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-title">Prodi paling kompetitif</div>',
                    unsafe_allow_html=True)
        ketat = (pend.groupby("prodi_pilihan_1")
                 .agg(n=("id_pendaftar", "count"),
                      acc=("status_seleksi", lambda s: (s == "Lulus").mean() * 100))
                 .query("n >= 50").nsmallest(10, "acc").sort_values("acc").reset_index())
        fig = px.bar(ketat, x="acc", y="prodi_pilihan_1", orientation="h",
                     color="acc", color_continuous_scale=[AMBER, "#F6D9A8"],
                     text=ketat["acc"].map("{:.0f}%".format),
                     labels={"acc": "% diterima", "prodi_pilihan_1": ""})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    insight_box("TI & Kesehatan mendominasi peminat tapi tingkat diterimanya paling rendah. "
                "Strategi <b>pilihan ke-2</b> jadi penentu peluang lolos calon mahasiswa.")

    st.markdown('<div class="sec-title">Peta peminat prodi per tahun</div>',
                unsafe_allow_html=True)
    heat = (pend.groupby(["tahun_daftar", "prodi_pilihan_1"]).size()
            .unstack(fill_value=0))
    fig = px.imshow(heat.T, aspect="auto", color_continuous_scale=["#FFFFFF", BLUE],
                    labels=dict(x="Tahun", y="", color="Peminat"))
    polish(fig, title=dict(text=""))
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------ #
#  TAB 3 — Demografi                                                  #
# ------------------------------------------------------------------ #
with tab3:
    c1, c2, c3 = st.columns([2, 2, 3], gap="large")

    with c1:
        st.markdown('<div class="sec-title">Jenis sekolah asal</div>',
                    unsafe_allow_html=True)
        sekolah = mhs["jenis_sekolah"].value_counts()
        fig = go.Figure(go.Pie(
            labels=sekolah.index, values=sekolah.values, hole=0.58,
            marker=dict(colors=[TEAL, BLUE, AMBER, "#C7D4EA"]),
            textinfo="label+percent", textposition="outside"))
        polish(fig, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-title">Gender per jurusan</div>',
                    unsafe_allow_html=True)
        g = mhs.groupby(["jurusan", "jenis_kelamin"]).size().reset_index(name="n")
        fig = px.bar(g, x="n", y="jurusan", color="jenis_kelamin", orientation="h",
                     barmode="stack", color_discrete_map={"L": BLUE, "P": "#F1919B"},
                     labels={"n": "", "jurusan": "", "jenis_kelamin": ""})
        polish(fig, legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig, use_container_width=True)

    with c3:
        st.markdown('<div class="sec-title">Top 10 kota asal mahasiswa</div>',
                    unsafe_allow_html=True)
        kota = mhs["asal_kota"].value_counts().head(10).sort_values().reset_index()
        kota.columns = ["kota", "n"]
        fig = px.bar(kota, x="n", y="kota", orientation="h",
                     color="n", color_continuous_scale=["#9CC0EE", TEAL],
                     text="n", labels={"kota": "", "n": ""})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    insight_box("<b>Kab. Indramayu sendirian menyumbang ~1/3 mahasiswa</b> — Polindra sangat "
                "lokal. Teknik didominasi lulusan SMK + laki-laki; Kesehatan didominasi "
                "SMA/MA + perempuan. Peluang besar: ekspansi brand ke luar Ciayumajakuning.")

# ------------------------------------------------------------------ #
#  TAB 4 — Akademik                                                   #
# ------------------------------------------------------------------ #
with tab4:
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown('<div class="sec-title">Distribusi IPK per jurusan</div>',
                    unsafe_allow_html=True)
        fig = go.Figure()
        colors_j = dict(zip(sorted(mhs["jurusan"].unique()), [BLUE, TEAL, AMBER]))
        for jur, sub in mhs.groupby("jurusan"):
            fig.add_trace(go.Violin(
                x=sub["ipk"], name=jur, line_color=colors_j[jur],
                fillcolor=colors_j[jur], opacity=0.55, meanline_visible=True,
                orientation="h", box_visible=True))
        polish(fig, showlegend=False)
        fig.update_xaxes(range=[0.8, 4.1], title="IPK")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="sec-title">Heatmap dropout rate</div>',
                    unsafe_allow_html=True)
        do_h = (mhs.groupby(["jurusan", "jenis_sekolah"])["status_mahasiswa"]
                .apply(lambda s: 100 * (s == "Drop Out").mean()).unstack())
        fig = px.imshow(do_h, aspect="auto", text_auto=".1f",
                        color_continuous_scale=["#FFFFFF", RED],
                        labels=dict(x="Jenis sekolah", y="", color="DO %"))
        polish(fig)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-title">Rata-rata IPK per prodi</div>',
                    unsafe_allow_html=True)
        ipk_p = mhs.groupby("prodi")["ipk"].mean().sort_values().reset_index()
        fig = px.bar(ipk_p, x="ipk", y="prodi", orientation="h",
                     color="ipk", color_continuous_scale=["#C7D4EA", PURPLE],
                     text=ipk_p["ipk"].map("{:.2f}".format),
                     labels={"prodi": "", "ipk": ""})
        fig.update_traces(textposition="outside")
        polish(fig, coloraxis_showscale=False)
        fig.update_xaxes(range=[2.5, 3.8])
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="sec-title">Komposisi status mahasiswa</div>',
                    unsafe_allow_html=True)
        status = mhs["status_mahasiswa"].value_counts()
        fig = go.Figure(go.Pie(
            labels=status.index, values=status.values, hole=0.58,
            marker=dict(colors=[TEAL, BLUE, AMBER, RED]),
            textinfo="label+percent", textposition="outside"))
        polish(fig, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    insight_box("Mahasiswa jalur <b>SNMPN ber-IPK tertinggi (3,40)</b> — nilai rapor "
                "terbukti prediktor performa akademik yang baik. Dropout terkonsentrasi "
                "di angkatan muda → 2 tahun pertama adalah periode kritis retensi.")

st.markdown("---")
st.caption("🎓 PMB Polindra Analytics · dataset sintetis untuk portofolio · "
           "Streamlit + Plotly")
