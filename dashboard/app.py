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
    .block-container {padding-top: 0rem; padding-bottom: 2rem; max-width: 1250px;}
    [data-testid="stSidebar"] {background: linear-gradient(180deg,#10294F 0%,#16386E 100%);}
    [data-testid="stSidebar"] * {color: #E8EEF8 !important;}
    [data-testid="stSidebar"] .stMultiSelect label {font-weight: 600;}

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

    .kpi {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.05rem 1.15rem .95rem 1.15rem;
        box-shadow: 0 3px 14px rgba(22,35,59,.07);
        border-top: 4px solid var(--accent, #1B5DBF);
        height: 100%;
    }
    .kpi .label {font-size: .78rem; font-weight: 700; color: #5B6B8C;
                 text-transform: uppercase; letter-spacing: .6px;}
    .kpi .value {font-size: 1.75rem; font-weight: 800; color: #16233B; line-height: 1.15;}
    .kpi .sub   {font-size: .8rem; color: #8A97B2; margin-top: .15rem;}

    .sec-title {font-size: 1.12rem; font-weight: 800; color: #16233B;
                margin: .4rem 0 .2rem 0;}
    .insight {
        background: #EBF3FF;
        border-left: 4px solid #1B5DBF;
        border-radius: 0 10px 10px 0;
        padding: .75rem 1rem;
        font-size: .88rem;
        color: #25406E;
        margin: .6rem 0;
    }
    .insight b {color: #1B5DBF;}

    .stTabs [data-baseweb="tab-list"] {gap: .4rem;}
    .stTabs [data-baseweb="tab"] {
        background: #E8EEF8; border-radius: 10px 10px 0 0;
        padding: .45rem 1.1rem; font-weight: 700; color: #44557A;
    }
    .stTabs [aria-selected="true"] {background: #1B5DBF !important; color: white !important;}

    [data-testid="stExpander"] {background: #FFFFFF; border-radius: 12px;
        border: 1px solid #E2E9F4;}
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
st.sidebar.caption("📊 Dataset sintetis · simulasi berbasis struktur prodi riil Polindra")

pend = pendaftar[pendaftar["tahun_daftar"].isin(tahun_pilih)
                 & pendaftar["jurusan"].isin(jurusan_pilih)
                 & pendaftar["jalur_masuk"].isin(jalur_pilih)]
mhs = mahasiswa[mahasiswa["angkatan"].isin(tahun_pilih)
                & mahasiswa["jurusan"].isin(jurusan_pilih)
                & mahasiswa["jalur_masuk"].isin(jalur_pilih)]

# gabungkan skor masuk ke mahasiswa utk analisis korelasi
mhs_x = mhs.merge(
    pend[["id_pendaftar", "nilai_rapor", "skor_seleksi"]],
    on="id_pendaftar", how="left")

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
    ("📥 Total Pendaftar", titik(n_pend), f"{len(tahun_pilih)} tahun pendaftaran", BLUE),
    ("✅ Lulus Seleksi", titik(n_lulus), f"{100*n_lulus/max(n_pend,1):.1f}% dari pendaftar", TEAL),
    ("📝 Daftar Ulang", titik(n_reg), f"{100*n_reg/max(n_lulus,1):.1f}% dari yang lulus", AMBER),
    ("📊 Rata-rata IPK", f"{mhs['ipk'].mean():.2f}".replace(".", ",") if len(mhs) else "-",
     "mahasiswa terfilter", PURPLE),
    ("⚠️ Dropout Rate", f"{100*n_do/max(len(mhs),1):.1f}%".replace(".", ","),
     f"{titik(n_do)} mahasiswa", RED),
]
for col, (label, val, sub, color) in zip(st.columns(5), kpis):
    col.markdown(f"""
    <div class="kpi" style="--accent:{color}">
        <div class="label">{label}</div>
        <div class="value">{val}</div>
        <div class="sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

st.write("")
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Tren & Funnel", "🏫 Program Studi", "🗺️ Demografi",
     "📊 Akademik", "🔍 Eksplorasi Data"])

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

        st.markdown('<div class="sec-title">Tingkat keketatan seleksi</div>',
                    unsafe_allow_html=True)
        ketat_t = (pend.groupby("tahun_daftar")["status_seleksi"]
                   .apply(lambda s: 100 * (s == "Lulus").mean()).reset_index())
        fig = go.Figure(go.Scatter(
            x=ketat_t["tahun_daftar"], y=ketat_t["status_seleksi"],
            mode="lines+markers+text",
            text=ketat_t["status_seleksi"].map("{:.0f}%".format),
            textposition="top center",
            line=dict(width=3, color=RED), marker=dict(size=9),
            fill="tozeroy", fillcolor="rgba(225,85,84,.08)"))
        polish(fig, yaxis_title="% lulus seleksi",
               title=dict(text="", font=dict(size=13)))
        st.plotly_chart(fig, use_container_width=True)

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

        st.markdown('<div class="sec-title">Conversion per jalur masuk</div>',
                    unsafe_allow_html=True)
        jalur_f = (pend.groupby("jalur_masuk")
                   .agg(n=("id_pendaftar", "count"),
                        reg=("daftar_ulang", lambda s: (s == "Ya").sum()))
                   .assign(rate=lambda d: 100 * d["reg"] / d["n"])
                   .sort_values("rate").reset_index())
        fig = px.bar(jalur_f, x="rate", y="jalur_masuk", orientation="h",
                     color="rate", color_continuous_scale=["#Bcd2f2", BLUE],
                     text=jalur_f["rate"].map("{:.1f}%".format),
                     labels={"rate": "", "jalur_masuk": ""})
        fig.update_traces(textposition="outside")
        polish(fig, showlegend=False, coloraxis_showscale=False)
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

⚠️ **Catatan:** data sintetis — polanya dimodelkan realistis, angkanya simulasi.
""")

    insight_box("Peminat tumbuh <b>~170%</b> dalam 6 tahun — lonjakan 2022 berbarengan "
                "dibukanya prodi S1 Terapan baru. Keketatan naik: hanya <b>~32%</b> "
                "pendaftar lulus di 2025 vs ~58% di 2019.")

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

    st.markdown('<div class="sec-title">Peminat vs tingkat diterima (bubble = total pendaftar)</div>',
                unsafe_allow_html=True)
    bubble = (pend.groupby(["prodi_pilihan_1", "jurusan"])
              .agg(peminat=("id_pendaftar", "count"),
                   diterima_pct=("status_seleksi", lambda s: 100 * (s == "Lulus").mean()),
                   skor_med=("skor_seleksi", "median"))
              .reset_index())
    fig = px.scatter(bubble, x="peminat", y="diterima_pct", size="peminat",
                     color="jurusan", hover_name="prodi_pilihan_1",
                     size_max=48, labels={"peminat": "Total peminat",
                                          "diterima_pct": "% diterima"},
                     color_discrete_map={"Teknik Informatika": BLUE,
                                         "Teknik": TEAL, "Kesehatan": RED})
    polish(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sec-title">Peta peminat prodi per tahun</div>',
                unsafe_allow_html=True)
    heat = (pend.groupby(["tahun_daftar", "prodi_pilihan_1"]).size()
            .unstack(fill_value=0))
    fig = px.imshow(heat.T, aspect="auto", color_continuous_scale=["#FFFFFF", BLUE],
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

    insight_box("TI & Kesehatan mendominasi peminat tapi tingkat diterimanya paling rendah. "
                "Strategi <b>pilihan ke-2</b> jadi penentu peluang lolos calon mahasiswa.")

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

    c4, c5 = st.columns(2, gap="large")
    with c4:
        st.markdown('<div class="sec-title">Konsentrasi domisili (tabel detail)</div>',
                    unsafe_allow_html=True)
        kt = mhs["asal_kota"].value_counts().reset_index()
        kt.columns = ["Kota asal", "Mahasiswa"]
        kt["%"] = (100 * kt["Mahasiswa"] / len(mhs)).round(1)
        kt["% kumulatif"] = kt["%"].cumsum().round(1)
        st.dataframe(kt, use_container_width=True, hide_index=True, height=350)
    with c5:
        st.markdown('<div class="sec-title">Jalur masuk per jurusan</div>',
                    unsafe_allow_html=True)
        jl = (mhs.groupby(["jurusan", "jalur_masuk"]).size()
              .reset_index(name="n"))
        fig = px.bar(jl, x="jurusan", y="n", color="jalur_masuk", barmode="stack",
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

        st.markdown('<div class="sec-title">Heatmap dropout rate (jurusan × sekolah)</div>',
                    unsafe_allow_html=True)
        do_h = (mhs.groupby(["jurusan", "jenis_sekolah"])["status_mahasiswa"]
                .apply(lambda s: 100 * (s == "Drop Out").mean()).unstack())
        fig = px.imshow(do_h, aspect="auto", text_auto=".1f",
                        color_continuous_scale=["#FFFFFF", RED],
                        labels=dict(x="Jenis sekolah", y="", color="DO %"))
        polish(fig)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-title">Korelasi: nilai rapor masuk → IPK</div>',
                    unsafe_allow_html=True)
        samp = mhs_x.dropna(subset=["nilai_rapor", "ipk"])
        corr = samp["nilai_rapor"].corr(samp["ipk"])
        fig = px.scatter(samp.sample(min(2000, len(samp)), random_state=7),
                         x="nilai_rapor", y="ipk", color="jurusan",
                         opacity=0.45, trendline="ols", trendline_scope="overall",
                         labels={"nilai_rapor": "Nilai rapor saat mendaftar",
                                 "ipk": "IPK saat ini", "jurusan": ""})
        polish(fig, legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Korelasi Pearson r = {corr:.2f} — semakin dekat ke ±1 semakin kuat hubungannya")

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

⚠️ **Caveat penting:** korelasi ≠ kausalitas. Dan pada data sintetis, pola
ini sengaja dimodelkan — di data riil, kekuatan hubungannya bisa beda.
""")

    insight_box("Mahasiswa jalur <b>SNMPN (seleksi rapor) ber-IPK tertinggi</b> — "
                "nilai rapor terbukti prediktor performa akademik yang baik. Dropout "
                "terkonsentrasi di angkatan muda → 2 tahun pertama periode kritis retensi.")

# ------------------------------------------------------------------ #
#  TAB 5 — Eksplorasi Data                                            #
# ------------------------------------------------------------------ #
with tab5:
    st.markdown('<div class="sec-title">Eksplorasi data interaktif</div>',
                unsafe_allow_html=True)
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
    st.markdown('<div class="sec-title">Pratinjau data mentah</div>',
                unsafe_allow_html=True)
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
