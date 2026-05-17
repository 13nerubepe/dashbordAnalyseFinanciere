import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(page_title="Tableau de Bord Immobilier", page_icon="🏠",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base typographie ─────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif;
    font-size: 13px;
    line-height: 1.55;
    color: #1E293B;
    -webkit-font-smoothing: antialiased;
}

/* ── Sidebar ──────────────────────────────────────────────────── */
section[data-testid="stSidebar"] { background: #1B2A4A !important; }
section[data-testid="stSidebar"] * {
    color: #CBD5E1 !important;
    font-family: 'Inter', sans-serif !important;
}
section[data-testid="stSidebar"] label {
    color: #94A3B8 !important;
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.2px !important;
}
section[data-testid="stSidebar"] > div:first-child { padding-top: 0.5rem !important; }

/* Sliders dorés */
section[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {
    background: #D4A017 !important; border-color: #D4A017 !important; }
section[data-testid="stSidebar"] [data-baseweb="slider"] div[class*="Track"] > div:nth-child(2) {
    background: #D4A017 !important; }
section[data-testid="stSidebar"] .stSlider > div > div > div > div {
    background: #D4A017 !important; }

/* ── Zone principale ──────────────────────────────────────────── */
.main .block-container { background: #F1F5F9; padding: 1rem 1.5rem; max-width: 100%; }

/* ── Titres de section (main) ─────────────────────────────────── */
.sec {
    font-family: 'Inter', sans-serif;
    font-size: 0.6rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 0.3rem 0;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 0.6rem;
}

/* ── Titres de section (sidebar) ──────────────────────────────── */
.sb-sec {
    font-family: 'Inter', sans-serif;
    font-size: 0.58rem;
    font-weight: 600;
    color: #D4A017;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 0.7rem;
    margin-bottom: 0.35rem;
    padding-bottom: 0.25rem;
    border-bottom: 1px solid rgba(212,160,23,0.25);
}

/* ── Chart cards ──────────────────────────────────────────────── */
.chart-card {
    background: white;
    border-radius: 8px;
    padding: 0.8rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 0 0 1px rgba(0,0,0,0.04);
    margin-bottom: 0.6rem;
}

/* ── Titres de graphique ──────────────────────────────────────── */
.ct {
    font-family: 'Inter', sans-serif;
    font-size: 0.58rem;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-left: 2px solid #D4A017;
    padding-left: 0.5rem;
    margin-bottom: 0.4rem;
}

/* ── KPI cards ────────────────────────────────────────────────── */
.kpi-box {
    background: white;
    border-radius: 8px;
    padding: 0.6rem 0.75rem;
    margin-bottom: 0.4rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 0 0 1px rgba(0,0,0,0.04);
    border-left: 3px solid #ccc;
    display: flex;
    align-items: center;
    gap: 0.55rem;
}
.kpi-lbl {
    font-size: 0.5rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.kpi-val {
    font-size: 1rem;
    font-weight: 700;
    line-height: 1.15;
    letter-spacing: -0.3px;
}
.kpi-sub {
    font-size: 0.48rem;
    font-weight: 400;
    color: #94A3B8;
}
</style>
""", unsafe_allow_html=True)

BLUE="#1B2A4A"; GOLD="#D4A017"; TEAL="#2196A6"; GREEN="#27AE60"; RED="#E53E3E"
PL = dict(paper_bgcolor="white", plot_bgcolor="white",
          font=dict(family="Inter, system-ui, sans-serif", size=11, color="#64748B"),
          margin=dict(l=8, r=8, t=22, b=8))

lbl_carte = {
    "price"      : "Prix ($)",
    "grade"      : "Grade",
    "bedrooms"   : "Chambres",
    "house_age"  : "Âge (ans)",
    "price_au_m2": "Prix/sqft ($)"
}

def hr():
    st.markdown("<hr style='border:1px solid rgba(255,255,255,0.1);margin:0.4rem 0;'>",
                unsafe_allow_html=True)

def sb_title(icon, label):
    st.markdown(f'<div class="sb-sec">{icon} {label}</div>', unsafe_allow_html=True)

# ── Chargement & nettoyage ────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("House-Data.csv")
    df["date"]        = pd.to_datetime(df["date"], format="%Y%m%dT%H%M%S")
    df["floors"]      = df["floors"].astype(int)
    df                = df[(df["bedrooms"] > 0) & (df["bedrooms"] <= 15)]
    df["house_age"]   = df["date"].dt.year - df["yr_built"]
    df["price_au_m2"] = (df["price"] / df["sqft_living"]).round(2)
    df["renovated"]   = df["yr_renovated"].apply(lambda x: "Rénové" if x > 0 else "Non rénové")
    df["sous_sol"]    = df["sqft_basement"].apply(lambda x: "Oui" if x > 0 else "Non")
    df["month"]       = df["date"].dt.to_period("M").astype(str)
    df["year"]        = df["date"].dt.year
    df["quarter"]     = df["date"].dt.quarter.apply(lambda x: f"Q{x}")
    df["saison"]      = df["date"].dt.month.map({
        12:"Hiver",  1:"Hiver",  2:"Hiver",
        3:"Printemps",4:"Printemps",5:"Printemps",
        6:"Été",     7:"Été",    8:"Été",
        9:"Automne", 10:"Automne",11:"Automne"})
    df["cat_prix"]    = pd.cut(df["price"], bins=[0,300000,600000,1000000,8000000],
                               labels=["Bas","Moyen","Élevé","Luxe"])
    df["wf_label"]    = df["waterfront"].map({1:"Vue eau", 0:"Sans vue"})
    df["bathrooms"]   = df["bathrooms"].astype(float)
    return df

data = load_data()

# ── Groupes salles de bain ────────────────────────────────────────────────────
bath_groups = {
    "🚿 Basique  — ≤ 1 bain (0.5 à 1.0)"     : (0.0,  1.0),
    "🛁 Standard — 1 à 2 bains (1.25 à 2.0)"  : (1.25, 2.0),
    "🏠 Confort  — 2 à 3 bains (2.25 à 3.0)"  : (2.25, 3.0),
    "✨ Luxe     — 3+ bains (3.25 et plus)"    : (3.25, 99.),
}

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0.2rem 0 0.7rem;">
        <div style="font-size:2.8rem;line-height:1;">🏠</div>
        <div style="font-size:0.52rem;font-weight:700;color:#94A3B8;
                    text-transform:uppercase;letter-spacing:2.5px;margin-top:0.25rem;">
            Analyse Immobilière</div>
        <div style="font-size:1rem;font-weight:800;color:white;line-height:1.2;">TABLEAU DE BORD</div>
        <div style="width:25px;height:3px;background:#D4A017;border-radius:2px;margin-top:0.3rem;"></div>
    </div>""", unsafe_allow_html=True)
    st.caption("Comté de King · Seattle WA · 2014-2015")
    hr()

    sb_title("📅", "Période")
    sel_year = st.selectbox("Année",
                ["Toutes"] + [str(y) for y in sorted(data["year"].unique())])
    data_y = data[data["year"] == int(sel_year)] if sel_year != "Toutes" else data.copy()
    trimestres_dispo = ["Tous"] + sorted(data_y["quarter"].unique().tolist())
    sel_q    = st.selectbox("Trimestre", trimestres_dispo)
    data_yq  = data_y[data_y["quarter"] == sel_q] if sel_q != "Tous" else data_y.copy()
    month_map        = data_yq[["month","date"]].drop_duplicates().sort_values("month")
    month_map["lbl"] = month_map["date"].dt.strftime("%b %Y")
    month_dict       = dict(zip(month_map["lbl"], month_map["month"]))
    mois_dispo       = list(month_dict.keys())
    sel_mois_lbl     = st.multiselect("Mois", mois_dispo, default=mois_dispo)
    sel_months       = [month_dict[m] for m in sel_mois_lbl]
    hr()

    sb_title("💰", "Prix")
    sel_cat = st.multiselect("Catégorie", options=["Bas","Moyen","Élevé","Luxe"],
                             default=["Bas","Moyen","Élevé","Luxe"])
    hr()

    sb_title("🛏️", "Chambres & Salles de bain")
    bed_dispo    = sorted(data["bedrooms"].unique().tolist())
    sel_bed      = st.multiselect("Chambres", bed_dispo,
                                  format_func=lambda x: f"{x} ch.", default=bed_dispo)
    sel_bath_grp = st.multiselect("Salles de bain",
                                  options=list(bath_groups.keys()),
                                  default=list(bath_groups.keys()))
    hr()

    sb_title("📐", "Superficie & Étages")
    sqft_min    = int(data["sqft_living"].min())
    sqft_max    = int(data["sqft_living"].max())
    sel_sqft    = st.slider("Superficie intérieure (sqft)",
                            sqft_min, sqft_max, (sqft_min, sqft_max), step=100)
    floor_dispo = sorted(data["floors"].unique().tolist())
    sel_floors  = st.multiselect("Étages", floor_dispo,
                                 format_func=lambda x: f"{x} étage(s)", default=floor_dispo)
    hr()

    sb_title("⭐", "Grade & Condition")
    sel_grade = st.select_slider("Grade (qualité)", options=list(range(1,14)), value=(1,13))
    sel_cond  = st.select_slider("Condition (état)", options=[1,2,3,4,5], value=(1,5))
    hr()

    sb_title("🏗️", "Équipements")
    sel_ss     = st.selectbox("Sous-sol",      ["Tous","Oui","Non"])
    sel_wf     = st.selectbox("Vue sur l'eau", ["Tous","Vue eau","Sans vue"])
    sel_ren    = st.selectbox("Rénovation",    ["Tous","Rénové","Non rénové"])
    view_dispo = sorted(data["view"].unique().tolist())
    sel_view   = st.multiselect("Qualité de la vue (0-4)", view_dispo, default=view_dispo)
    hr()

    sb_title("🗺️", "Carte")
    color_by = st.selectbox("Colorer par", list(lbl_carte.keys()),
                            format_func=lambda x: lbl_carte[x])
    hr()
    st.caption("📅 Mai 2014 — Mai 2015")

# ── FILTRES ───────────────────────────────────────────────────────────────────
dff = data.copy()
if sel_year  != "Toutes": dff = dff[dff["year"]    == int(sel_year)]
if sel_q     != "Tous":   dff = dff[dff["quarter"] == sel_q]
if sel_months:            dff = dff[dff["month"].isin(sel_months)]
dff = dff[dff["cat_prix"].notna()]
if sel_cat:               dff = dff[dff["cat_prix"].isin(sel_cat)]
if sel_bed:               dff = dff[dff["bedrooms"].isin(sel_bed)]
if sel_bath_grp:
    ranges = [bath_groups[g] for g in sel_bath_grp]
    mask   = pd.concat([(dff["bathrooms"] >= lo) & (dff["bathrooms"] <= hi)
                        for lo, hi in ranges], axis=1).any(axis=1)
    dff = dff[mask]
dff = dff[(dff["sqft_living"] >= sel_sqft[0]) & (dff["sqft_living"] <= sel_sqft[1])]
if sel_floors:            dff = dff[dff["floors"].isin(sel_floors)]
dff = dff[(dff["grade"]     >= sel_grade[0]) & (dff["grade"]     <= sel_grade[1])]
dff = dff[(dff["condition"] >= sel_cond[0])  & (dff["condition"] <= sel_cond[1])]
if sel_ss  != "Tous":     dff = dff[dff["sous_sol"]  == sel_ss]
if sel_wf  != "Tous":     dff = dff[dff["wf_label"]  == sel_wf]
if sel_ren != "Tous":     dff = dff[dff["renovated"] == sel_ren]
if sel_view:              dff = dff[dff["view"].isin(sel_view)]

# ── HEADER ────────────────────────────────────────────────────────────────────
nb_prop   = len(dff)
prix_moy  = dff["price"].mean()  / 1e3 if nb_prop > 0 else 0
prix_med  = dff["price"].median()/ 1e3 if nb_prop > 0 else 0
vol_total = dff["price"].sum()   / 1e9 if nb_prop > 0 else 0

components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  *{{margin:0;padding:0;box-sizing:border-box;font-family:'Inter',system-ui,sans-serif;}}
  body{{background:transparent;}}
  .header{{background:linear-gradient(90deg,#1B2A4A 0%,#2A3F6F 50%,#1B2A4A 100%);
           padding:0.7rem 2rem;border-radius:10px;display:flex;align-items:center;
           justify-content:space-between;border-bottom:3px solid #D4A017;
           box-shadow:0 4px 15px rgba(27,42,74,0.3);}}
  .titre-sub{{font-size:0.52rem;font-weight:700;color:#D4A017;text-transform:uppercase;letter-spacing:3px;}}
  .titre-main{{font-size:1.3rem;font-weight:800;color:white;line-height:1.1;}}
  .stats{{display:flex;gap:1.5rem;text-align:center;align-items:center;}}
  .stat-val{{font-size:1.05rem;font-weight:800;}}
  .stat-lbl{{font-size:0.45rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.5px;}}
  .sep{{width:1px;height:28px;background:rgba(255,255,255,0.15);}}
  .badge{{background:rgba(212,160,23,0.15);border:1px solid #D4A017;
          border-radius:8px;padding:0.4rem 0.9rem;text-align:center;}}
  .badge-lbl{{font-size:0.42rem;color:#94A3B8;text-transform:uppercase;}}
  .badge-val{{font-size:0.8rem;font-weight:800;color:#D4A017;line-height:1.3;}}
</style></head><body>
<div class="header">
  <div style="display:flex;align-items:center;gap:1rem;">
    <div style="font-size:2.2rem;">🏠</div>
    <div>
      <div class="titre-sub">Analyse Immobilière · Comté de King</div>
      <div class="titre-main">Tableau De Bord Des Ventes De Maisons</div>
    </div>
  </div>
  <div class="stats">
    <div><div class="stat-val" style="color:#D4A017;">{nb_prop:,}</div><div class="stat-lbl">Propriétés</div></div>
    <div class="sep"></div>
    <div><div class="stat-val" style="color:white;">${prix_moy:.0f}K</div><div class="stat-lbl">Prix Moyen</div></div>
    <div class="sep"></div>
    <div><div class="stat-val" style="color:white;">${prix_med:.0f}K</div><div class="stat-lbl">Prix Médian</div></div>
    <div class="sep"></div>
    <div><div class="stat-val" style="color:white;">${vol_total:.1f}B</div><div class="stat-lbl">Volume Total</div></div>
  </div>
  <div class="badge">
    <div class="badge-lbl">Période</div>
    <div class="badge-val">Mai 2014<br>Mai 2015</div>
  </div>
</div>
</body></html>
""", height=85)

if nb_prop == 0:
    st.warning(" Aucune propriété ne correspond aux filtres sélectionnés.")
    st.stop()

# ── LAYOUT ────────────────────────────────────────────────────────────────────
col_main, col_kpi = st.columns([3.2, 0.8])

# ── KPIs ──────────────────────────────────────────────────────────────────────
with col_kpi:
    avg_ren  = dff[dff["renovated"]=="Rénové"]["price"].mean()
    avg_nren = dff[dff["renovated"]=="Non rénové"]["price"].mean()
    avg_wf   = dff[dff["waterfront"]==1]["price"].mean() if (dff["waterfront"]==1).any() else 0
    avg_nwf  = dff[dff["waterfront"]==0]["price"].mean()
    avg_gtp  = dff[dff["grade"]>=10]["price"].mean() if (dff["grade"]>=10).any() else 0
    avg_gr   = dff[dff["sqft_living"]>=2000]["price"].mean()
    avg_pt   = dff[dff["sqft_living"]<2000]["price"].mean()

    st.markdown('<div class="sec">💰 Indicateurs de Prix</div>', unsafe_allow_html=True)
    for color, icon, lbl, val, sub in [
        (GOLD,  "🔨", "Prix Rénové",    f"${avg_ren/1e3:.0f}K", f"vs ${avg_nren/1e3:.0f}K non rén."),
        (TEAL,  "🌊", "Prix Vue Eau",   f"${avg_wf/1e3:.0f}K",  f"vs ${avg_nwf/1e3:.0f}K sans vue"),
        (GREEN, "⭐", "Top Grade ≥ 10", f"${avg_gtp/1e3:.0f}K", "Prix moyen"),
        (RED,   "📐", "Grande Maison",  f"${avg_gr/1e3:.0f}K",  f"vs ${avg_pt/1e3:.0f}K <2000sqft"),
    ]:
        st.markdown(f"""
        <div class="kpi-box" style="border-left-color:{color};">
            <div style="font-size:1rem;">{icon}</div>
            <div>
                <div class="kpi-lbl">{lbl}</div>
                <div class="kpi-val" style="color:{color};">{val}</div>
                <div class="kpi-sub">{sub}</div>
            </div>
        </div>""", unsafe_allow_html=True)

# ── GRAPHES ───────────────────────────────────────────────────────────────────
with col_main:

    # ── ROW 1 — Ventes & Prix ─────────────────────────────────────────
    st.markdown('<div class="sec">📈 Ventes & Prix</div>', unsafe_allow_html=True)
    g1a, g1b = st.columns([2, 1])

    with g1a:
        st.markdown('<div class="chart-card"><div class="ct">Ventes & Prix moyen par mois</div>',
                    unsafe_allow_html=True)
        monthly      = dff.groupby("month").agg(nb=("price","count"), prix=("price","mean")).reset_index()
        monthly["ms"] = monthly["month"].str[-5:]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly["ms"], y=monthly["nb"], name="Nb ventes",
            marker_color=BLUE, opacity=0.85, yaxis="y1",
            text=monthly["nb"], textposition="outside", textfont=dict(size=7)))
        fig.add_trace(go.Scatter(
            x=monthly["ms"], y=monthly["prix"]/1000, name="Prix moyen ($K)",
            line=dict(color=GOLD, width=2.5), marker=dict(size=5),
            yaxis="y2", mode="lines+markers"))
        fig.update_layout(
            **PL, height=240,
            yaxis =dict(showgrid=False, showticklabels=False),
            yaxis2=dict(overlaying="y", side="right", showgrid=False,
                        tickfont=dict(color=GOLD, size=9)),
            xaxis =dict(tickangle=-35, tickfont=dict(size=8)),
            legend=dict(orientation="h", y=1.12, x=0, font=dict(size=9)),
            bargap=0.3)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with g1b:
        st.markdown('<div class="chart-card"><div class="ct">Ventes par trimestre</div>',
                    unsafe_allow_html=True)
        qc = dff.groupby("quarter").agg(nb=("price","count"), prix=("price","mean")).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=qc["quarter"], y=qc["nb"], name="Nb ventes",
            marker_color=BLUE, opacity=0.85,
            text=qc["nb"], textposition="outside", textfont=dict(size=8)))
        fig.add_trace(go.Scatter(
            x=qc["quarter"], y=qc["prix"]/1000, name="Prix moyen ($K)",
            line=dict(color=GOLD, width=2.5), marker=dict(size=7),
            yaxis="y2", mode="lines+markers"))
        fig.update_layout(
            **PL, height=240,
            yaxis =dict(showgrid=False, showticklabels=False),
            yaxis2=dict(overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=1.12, font=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 2 — Répartition & Performance ────────────────────────────
    st.markdown('<div class="sec">🏆 Répartition & Performance</div>', unsafe_allow_html=True)
    g2a, g2b, g2c = st.columns([1.3, 0.8, 0.9])

    with g2a:
        lbl_top = lbl_carte.get(color_by, color_by)
        st.markdown(f'<div class="chart-card"><div class="ct">Top 5 Quartiers — {lbl_top}</div>',
                    unsafe_allow_html=True)
        tz = (dff.groupby("zipcode")[color_by].mean()
                 .sort_values(ascending=True).tail(5).reset_index())
        tz.columns  = ["zipcode", "valeur"]
        tz["zipcode"] = tz["zipcode"].astype(str)
        n = len(tz)
        colors = [GOLD if i == n-1 else (TEAL if i >= n-3 else BLUE) for i in range(n)]
        fig = go.Figure()
        # Tiges
        fig.add_trace(go.Scatter(
            x=tz["valeur"], y=tz["zipcode"],
            mode="lines",
            line=dict(color="#E2E8F0", width=2),
            showlegend=False))
        # Dots + valeurs
        fig.add_trace(go.Scatter(
            x=tz["valeur"], y=tz["zipcode"],
            mode="markers+text",
            marker=dict(size=14, color=colors, line=dict(color="white", width=2)),
            text=[f"{v:,.0f}" for v in tz["valeur"]],
            textposition="middle right",
            textfont=dict(size=9, color=BLUE),
            showlegend=False))
        fig.update_layout(
            **PL, height=280,
            xaxis=dict(showgrid=False, showticklabels=False, title=lbl_top,
                       range=[0, tz["valeur"].max() * 1.3]),
            yaxis=dict(tickfont=dict(size=9)),
            showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with g2b:
        st.markdown('<div class="chart-card"><div class="ct">Catégories de Prix</div>',
                    unsafe_allow_html=True)
        cat = dff["cat_prix"].value_counts()
        fig = go.Figure(go.Pie(
            labels=cat.index, values=cat.values, hole=0.55,
            marker_colors=[GOLD,BLUE,TEAL,GREEN], textfont=dict(size=9)))
        fig.update_layout(
            **PL, height=280, showlegend=True,
            legend=dict(orientation="h", y=-0.2, font=dict(size=8)),
            annotations=[dict(text=f"<b>{len(dff):,}</b><br>Biens",
                              x=0.5, y=0.5, showarrow=False,
                              font=dict(size=10, color=BLUE))])
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with g2c:
        st.markdown('<div class="chart-card"><div class="ct">Prix Moyen par Grade</div>',
                    unsafe_allow_html=True)
        ga = dff.groupby("grade")["price"].mean()/1000
        fig = go.Figure(go.Bar(
            x=ga.index, y=ga.values,
            marker_color=[GOLD if v==ga.max() else BLUE for v in ga.values],
            text=[f"${v:.0f}K" for v in ga.values],
            textposition="outside", textfont=dict(size=7)))
        fig.update_layout(
            **PL, height=280,
            xaxis=dict(title="Grade", tickfont=dict(size=9)),
            yaxis=dict(showgrid=False, showticklabels=False),
            showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 3 — Facteurs ─────────────────────────────────────────────
    st.markdown('<div class="sec">🔍 Facteurs qui Influencent le Prix</div>', unsafe_allow_html=True)
    g3a, g3b, g3c, g3d = st.columns(4)

    with g3a:
        st.markdown('<div class="chart-card"><div class="ct">Distribution des Prix</div>',
                    unsafe_allow_html=True)
        fig = go.Figure(go.Histogram(x=dff["price"]/1000, nbinsx=40,
                                     marker_color=BLUE, opacity=0.85))
        fig.update_layout(
            **PL, height=250,
            xaxis=dict(title="Prix ($K)", tickfont=dict(size=9)),
            yaxis=dict(title="Effectifs", gridcolor="#F0F2F6"),
            showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with g3b:
        st.markdown('<div class="chart-card"><div class="ct">Prix vs Superficie</div>',
                    unsafe_allow_html=True)
        smp = dff.sample(min(3000, len(dff)), random_state=42)
        fig = px.scatter(
            smp, x="sqft_living", y="price", color=color_by,
            color_continuous_scale="RdYlGn", opacity=0.5,
            labels={"sqft_living":"Superficie (sqft)", "price":"Prix ($)",
                    color_by: lbl_carte.get(color_by, color_by)},
            hover_data=["bedrooms","grade","bathrooms"])
        fig.update_layout(
            **PL, height=250, showlegend=False,
            coloraxis_colorbar=dict(title=lbl_carte.get(color_by, color_by),
                                    thickness=10, len=0.7))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with g3c:
        st.markdown('<div class="chart-card"><div class="ct">Prix selon Rénovation</div>',
                    unsafe_allow_html=True)
        fig = go.Figure()
        for grp, color, name in [("Non rénové", BLUE, "Non rénové"),
                                  ("Rénové",     GOLD, "Rénové")]:
            vals = dff[dff["renovated"]==grp]["price"]/1000
            fig.add_trace(go.Box(y=vals, name=name, marker_color=color,
                                 line_color=color, boxmean=True,
                                 fillcolor=color, opacity=0.7))
        fig.update_layout(
            **PL, height=250,
            yaxis=dict(title="Prix ($K)", gridcolor="#F0F2F6"),
            legend=dict(orientation="h", y=1.12, font=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with g3d:
        st.markdown('<div class="chart-card"><div class="ct">Corrélation avec le Prix</div>',
                    unsafe_allow_html=True)
        corr = (dff.corr(numeric_only=True)["price"]
                   .drop("price").sort_values(ascending=True))
        fig = go.Figure(go.Bar(
            x=corr.values, y=corr.index, orientation="h",
            marker_color=[GREEN if v > 0 else RED for v in corr.values],
            text=[f"{v:.2f}" for v in corr.values],
            textposition="outside", textfont=dict(size=7)))
        fig.add_vline(x=0, line_color="black", line_width=0.8)
        fig.update_layout(
            **PL, height=250,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(tickfont=dict(size=8)),
            showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 4 — Maisons revendues ─────────────────────────────────────
    st.markdown('<div class="sec">📊 Évolution — Maisons Revendues</div>', unsafe_allow_html=True)
    g4a, g4b = st.columns(2)

    with g4a:
        st.markdown('<div class="chart-card"><div class="ct">Distribution des variations de prix</div>',
                    unsafe_allow_html=True)
        ventes_mult = data[data.duplicated(subset=["id"], keep=False)].sort_values(["id","date"])
        evol = ventes_mult.groupby("id")["price"].agg(["first","last"])
        evol["variation_pct"] = ((evol["last"] - evol["first"]) / evol["first"] * 100).round(1)
        fig = go.Figure(go.Histogram(x=evol["variation_pct"], nbinsx=30,
                                     marker_color=BLUE, opacity=0.85))
        fig.add_vline(x=0, line_color=RED, line_width=1.5,
                      annotation_text="0%", annotation_position="top")
        fig.update_layout(
            **PL, height=250,
            xaxis=dict(title="Variation du prix (%)", tickfont=dict(size=9)),
            yaxis=dict(title="Nb maisons", gridcolor="#F0F2F6"),
            showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with g4b:
        st.markdown('<div class="chart-card"><div class="ct">Top 5 — Plus fortes hausses de prix</div>',
                    unsafe_allow_html=True)
        top5 = evol.sort_values("variation_pct", ascending=False).head(5).reset_index()
        for i, row in top5.iterrows():
            st.markdown(f"""
            <div style="background:white;padding:0.55rem 0.8rem;border-radius:8px;
                        margin-bottom:0.35rem;
                        border-left:4px solid {'#D4A017' if i==0 else '#2196A6'};
                        box-shadow:0 1px 4px rgba(0,0,0,0.05);
                        display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:0.52rem;color:#94A3B8;text-transform:uppercase;">
                        Maison #{str(int(row['id']))[-6:]}</div>
                    <div style="font-size:0.9rem;font-weight:800;color:#1B2A4A;">
                        +{row['variation_pct']:.1f}%</div>
                    <div style="font-size:0.52rem;color:#64748B;">
                        ${row['first']/1e3:.0f}K → ${row['last']/1e3:.0f}K</div>
                </div>
                <div style="background:rgba(39,174,96,0.12);color:#27AE60;
                            padding:0.2rem 0.5rem;border-radius:6px;
                            font-size:0.65rem;font-weight:700;">#{i+1}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 5 — CARTE ─────────────────────────────────────────────────
    st.markdown('<div class="sec">🗺️ Carte Interactive — Comté de King, Seattle</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="chart-card"><div class="ct">Carte des prix — Comté de King</div>',
                unsafe_allow_html=True)
    smp_c = dff.sample(min(6000, len(dff)), random_state=42)
    fig_map = px.scatter_mapbox(
        smp_c, lat="lat", lon="long",
        color=color_by, color_continuous_scale="RdYlGn_r",
        size="price", size_max=12, zoom=9,
        center={"lat":47.5, "lon":-122.0},
        mapbox_style="carto-positron",
        hover_data={"price":":$,.0f","bedrooms":True,"grade":True,
                    "sqft_living":True,"month":True,"lat":False,"long":False},
        labels={color_by: lbl_carte.get(color_by, color_by)},
        opacity=0.7, height=420)
    fig_map.update_layout(
        paper_bgcolor="white", margin=dict(l=0,r=0,t=0,b=0),
        coloraxis_colorbar=dict(title=lbl_carte.get(color_by, color_by),
                                thickness=12, len=0.7))
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── CONCLUSIONS CLÉS ──────────────────────────────────────────────────────────
wf_p  = ((dff[dff["waterfront"]==1]["price"].mean() /
           dff[dff["waterfront"]==0]["price"].mean()-1)*100) if (dff["waterfront"]==1).any() else 0
ren_p = ((dff[dff["renovated"]=="Rénové"]["price"].mean() /
           dff[dff["renovated"]=="Non rénové"]["price"].mean()-1)*100) if (dff["renovated"]=="Rénové").any() else 0
top_g = dff.groupby("grade")["price"].mean().idxmax()
top_z = dff.groupby("zipcode")["price"].mean().idxmax()

st.markdown(f"""
<div style="background:#1B2A4A;border-radius:10px;padding:0.9rem 1.5rem;margin-top:0.4rem;">
  <div style="font-size:0.62rem;font-weight:700;color:#D4A017;text-transform:uppercase;
              letter-spacing:1px;margin-bottom:0.5rem;">🔑 Conclusions Clés</div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:0.5rem;">
    <div style="background:rgba(255,255,255,0.07);border-left:3px solid #D4A017;
                border-radius:6px;padding:0.5rem 0.7rem;">
      <p style="color:#CBD5E1;font-size:0.63rem;margin:0;line-height:1.5;">
        🌊 <b>Prime Vue Eau</b><br>Vue sur l'eau = <b>+{wf_p:.0f}%</b> vs sans vue</p></div>
    <div style="background:rgba(255,255,255,0.07);border-left:3px solid #2196A6;
                border-radius:6px;padding:0.5rem 0.7rem;">
      <p style="color:#CBD5E1;font-size:0.63rem;margin:0;line-height:1.5;">
        🔨 <b>Impact Rénovation</b><br>Maison rénovée = <b>+{ren_p:.0f}%</b> en moyenne</p></div>
    <div style="background:rgba(255,255,255,0.07);border-left:3px solid #27AE60;
                border-radius:6px;padding:0.5rem 0.7rem;">
      <p style="color:#CBD5E1;font-size:0.63rem;margin:0;line-height:1.5;">
        ⭐ <b>Meilleur Grade : {top_g}</b><br>Grade avec le prix moyen le plus élevé</p></div>
    <div style="background:rgba(255,255,255,0.07);border-left:3px solid #E53E3E;
                border-radius:6px;padding:0.5rem 0.7rem;">
      <p style="color:#CBD5E1;font-size:0.63rem;margin:0;line-height:1.5;">
        📍 <b>Meilleur Quartier : {top_z}</b><br>Quartier le plus cher du comté</p></div>
  </div>
</div>""", unsafe_allow_html=True)
