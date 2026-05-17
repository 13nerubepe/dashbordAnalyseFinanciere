import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ── Config ─────────────────────────────────────────────────────────────────
# st.set_page_config(
#     page_title="House Analytics Dashboard",
#     page_icon="🏠",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

st.set_page_config(layout="wide")

# ───────────────── STYLE GLOBAL ─────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    section[data-testid="stSidebar"] { background: #1B2A4A !important; }
    section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: white !important; }
    section[data-testid="stSidebar"] label { color: #94A3B8 !important; font-size:0.72rem !important; }

    .main .block-container { background:#F1F5F9; padding:1.2rem 1.8rem; max-width:100%; }

    .dash-header { background:white; border-radius:8px; padding:0.9rem 1.4rem;
                   margin-bottom:0.8rem; border-bottom:3px solid #1B2A4A; }
    .dash-header h2 { font-size:1rem; font-weight:700; color:#1B2A4A; margin:0;
                      text-transform:uppercase; letter-spacing:1px; }
    .dash-header p  { font-size:0.72rem; color:#94A3B8; margin:0.2rem 0 0; }

    .kpi { background:white; border-radius:8px; padding:0.7rem 0.8rem;
           text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.07); }
    .kpi-icon { font-size:1.3rem; }
    .kpi-val  { font-size:1.5rem; font-weight:700; color:#1B2A4A; line-height:1.1; }
    .kpi-lbl  { font-size:0.62rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.5px; }
    .kpi-sub  { font-size:0.65rem; color:#64748B; }

    .chart-card { background:white; border-radius:8px; padding:0.6rem 0.7rem;
                  box-shadow:0 1px 3px rgba(0,0,0,0.06); margin-bottom:0.7rem; }
    .ct { font-size:0.65rem; font-weight:600; color:#64748B;
          text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px; }

    .takeaway { background:#1B2A4A; border-radius:8px; padding:0.9rem 1.2rem; margin-top:0.3rem; }
    .takeaway h4 { color:white; font-size:0.75rem; margin:0 0 0.7rem;
                   text-transform:uppercase; letter-spacing:1px; }
    .tk-grid { display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:0.5rem; }
    .tk-item { background:rgba(255,255,255,0.08); border-radius:6px; padding:0.5rem 0.7rem; }
    .tk-item p { color:#CBD5E1; font-size:0.68rem; margin:0; line-height:1.5; }
</style>
""", unsafe_allow_html=True)

# ── Data ───────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("House-Data.csv")
    df["date"]        = pd.to_datetime(df["date"], format="%Y%m%dT%H%M%S")
    df["floors"]      = df["floors"].astype(int)
    df                = df[(df["bedrooms"] > 0) & (df["bedrooms"] <= 15)]
    df["house_age"]   = df["date"].dt.year - df["yr_built"]
    df["price_au_m2"] = (df["price"] / df["sqft_living"]).round(2)
    df["renovated"]   = df["yr_renovated"].apply(lambda x: "Rénové" if x > 0 else "Non rénové")
    df["month"]       = df["date"].dt.to_period("M").astype(str)
    df["quarter"]     = df["date"].dt.quarter.apply(lambda x: f"Q{x}")
    df["cat_prix"]    = pd.cut(df["price"], bins=[0,300000,600000,1000000,8000000],
                               labels=["Bas","Moyen","Élevé","Luxe"])
    df["cat_age"]     = pd.cut(df["house_age"], bins=[0,20,40,60,80,120],
                               labels=["0-20","21-40","41-60","61-80","80+"])
    df["wf_label"]    = df["waterfront"].map({1:"Vue eau", 0:"Sans vue"})
    return df

df = load_data()

BLUE  = "#1B2A4A"
GOLD  = "#D4A017"
TEAL  = "#2196A6"
LBLUE = "#4A90D9"

def mini_fig(h=2.6):
    fig, ax = plt.subplots(figsize=(3.5, h))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.spines[["top","right","left","bottom"]].set_visible(False)
    ax.tick_params(labelsize=6.5, colors="#64748B")
    return fig, ax

# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏠\n### HOUSE ANALYTICS\n**DASHBOARD**")
    st.markdown("---")
    st.caption("A comprehensive overview of King County real estate and key housing metrics.")
    st.markdown("---")

    sel_year = st.selectbox("📅 Year", ["All"] + [str(y) for y in sorted(df["date"].dt.year.unique())])
    sel_q    = st.selectbox("📆 Quarter", ["All","Q1","Q2","Q3","Q4"])
    sel_wf   = st.selectbox("🌊 Waterfront", ["All","Vue eau","Sans vue"])
    sel_ren  = st.selectbox("🔨 Renovation", ["All","Rénové","Non rénové"])
    price_max = st.slider("💰 Max Price ($)", 100000, 8000000, 2000000, 100000)

    st.markdown("---")
    st.caption("Data as of Dec 2015")

# ── FILTER ─────────────────────────────────────────────────────────────────
dff = df.copy()
if sel_year != "All": dff = dff[dff["date"].dt.year == int(sel_year)]
if sel_q    != "All": dff = dff[dff["quarter"] == sel_q]
if sel_wf   != "All": dff = dff[dff["wf_label"] == sel_wf]
if sel_ren  != "All": dff = dff[dff["renovated"] == sel_ren]
dff = dff[dff["price"] <= price_max]

# ── HEADER ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
  <h2> King County — House Sales Overview</h2>
  <p>Key metrics that provide a snapshot of the real estate market &nbsp;·&nbsp; {len(dff):,} properties selected</p>
</div>""", unsafe_allow_html=True)

# ── KPIs ───────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5 = st.columns(5)
avg_p  = dff["price"].mean()
med_p  = dff["price"].median()
n_ren  = (dff["renovated"]=="Rénové").sum()
pct_wf = (dff["waterfront"]==1).mean()*100
tot_v  = dff["price"].sum()/1e6

for col, icon, val, lbl, sub in [
    (k1,"🏠",f"{len(dff):,}","Total Properties",f"King County"),
    (k2,"💰",f"${avg_p/1e3:.0f}K","Avg Price",f"Median ${med_p/1e3:.0f}K"),
    (k3,"🔨",f"{n_ren:,}","Renovated",f"{n_ren/len(dff)*100:.1f}% of total"),
    (k4,"🌊",f"{pct_wf:.2f}%","Waterfront Rate","Premium properties"),
    (k5,"💵",f"${tot_v:.0f}M","Sum of Sales","Total market value"),
]:
    col.markdown(f"""<div class="kpi">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-val">{val}</div>
      <div class="kpi-lbl">{lbl}</div>
      <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── ROW 1 ──────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)

with c1:
    st.markdown('<div class="chart-card"><div class="ct">By Renovation</div>', unsafe_allow_html=True)
    rc = dff["renovated"].value_counts()
    fig, ax = mini_fig()
    ax.pie(rc, labels=rc.index, autopct="%1.0f%%",
           colors=[BLUE, GOLD], wedgeprops=dict(width=0.55),
           startangle=90, textprops=dict(fontsize=6.5))
    st.pyplot(fig); plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="chart-card"><div class="ct">Count by Education — Grade</div>', unsafe_allow_html=True)
    g = dff.groupby("grade")["price"].count()
    fig, ax = mini_fig()
    cols = [GOLD if v==g.max() else BLUE for v in g.values]
    ax.bar(g.index, g.values, color=cols, width=0.7)
    ax.yaxis.set_visible(False)
    ax.set_xlabel("Grade", fontsize=6)
    st.pyplot(fig); plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="chart-card"><div class="ct">Count by Bedrooms</div>', unsafe_allow_html=True)
    bed = dff["bedrooms"].value_counts().sort_index()
    fig, ax = mini_fig()
    cols = [GOLD if v==bed.max() else TEAL for v in bed.values]
    ax.barh(bed.index.astype(str), bed.values, color=cols, height=0.65)
    ax.xaxis.set_visible(False)
    for i,v in enumerate(bed.values):
        ax.text(v+5, i, str(v), va="center", fontsize=5.5, color="#64748B")
    st.pyplot(fig); plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="chart-card"><div class="ct">Price Category</div>', unsafe_allow_html=True)
    cat = dff["cat_prix"].value_counts()
    fig, ax = mini_fig()
    cols = [GOLD,BLUE,TEAL,LBLUE][:len(cat)]
    bars = ax.bar(cat.index, cat.values, color=cols, width=0.65)
    ax.yaxis.set_visible(False)
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+20,
                str(int(b.get_height())), ha="center", fontsize=5.5, color="#64748B")
    ax.tick_params(axis="x", labelsize=6)
    st.pyplot(fig); plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

with c5:
    st.markdown('<div class="chart-card"><div class="ct">Count by House Age</div>', unsafe_allow_html=True)
    age_c = dff["cat_age"].value_counts().sort_index()
    fig, ax = mini_fig()
    ax.barh(age_c.index.astype(str), age_c.values, color=BLUE, height=0.65)
    ax.xaxis.set_visible(False)
    for i,v in enumerate(age_c.values):
        ax.text(v+5, i, str(v), va="center", fontsize=5.5, color="#64748B")
    st.pyplot(fig); plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

# ── ROW 2 ──────────────────────────────────────────────────────────────────
r1,r2,r3,r4,r5 = st.columns(5)

with r1:
    st.markdown('<div class="chart-card"><div class="ct">Sales by Quarter</div>', unsafe_allow_html=True)
    qc = dff.groupby("quarter")["price"].count()
    fig, ax = mini_fig()
    cols = [GOLD if v==qc.max() else BLUE for v in qc.values]
    bars = ax.bar(qc.index, qc.values, color=cols, width=0.6)
    ax.yaxis.set_visible(False)
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+10,
                str(int(b.get_height())), ha="center", fontsize=5.5, color="#64748B")
    st.pyplot(fig); plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

with r2:
    st.markdown('<div class="chart-card"><div class="ct">Sales by Month</div>', unsafe_allow_html=True)
    mp = dff.groupby("month")["price"].count()
    fig, ax = mini_fig()
    x = range(len(mp))
    ax.plot(x, mp.values, color=TEAL, lw=1.5, marker="o", markersize=2.5)
    ax.fill_between(x, mp.values, alpha=0.1, color=TEAL)
    ax.yaxis.set_visible(False)
    ax.set_xticks(list(range(0,len(mp),3)))
    ax.set_xticklabels([mp.index[i][-5:] for i in range(0,len(mp),3)], fontsize=5.5, rotation=45)
    st.pyplot(fig); plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

with r3:
    st.markdown('<div class="chart-card"><div class="ct">Avg Price by Month ($K)</div>', unsafe_allow_html=True)
    mpp = dff.groupby("month")["price"].mean()/1000
    fig, ax = mini_fig()
    x = range(len(mpp))
    ax.plot(x, mpp.values, color=GOLD, lw=1.5, marker="o", markersize=2.5)
    ax.fill_between(x, mpp.values, alpha=0.1, color=GOLD)
    ax.yaxis.set_visible(False)
    ax.set_xticks(list(range(0,len(mpp),3)))
    ax.set_xticklabels([mpp.index[i][-5:] for i in range(0,len(mpp),3)], fontsize=5.5, rotation=45)
    st.pyplot(fig); plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

with r4:
    st.markdown('<div class="chart-card"><div class="ct">Avg Price by Waterfront</div>', unsafe_allow_html=True)
    wf_avg = dff.groupby("wf_label")["price"].mean()/1000
    fig, ax = mini_fig()
    bars = ax.bar(wf_avg.index, wf_avg.values, color=[BLUE,GOLD], width=0.5)
    ax.yaxis.set_visible(False)
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+3,
                f"${b.get_height():.0f}K", ha="center", fontsize=6, color="#64748B")
    ax.tick_params(axis="x", labelsize=6.5)
    st.pyplot(fig); plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

with r5:
    st.markdown('<div class="chart-card"><div class="ct">Avg Price by Renovation</div>', unsafe_allow_html=True)
    ren_avg = dff.groupby("renovated")["price"].mean()/1000
    fig, ax = mini_fig()
    labels = ["Non rén.", "Rénové"]
    vals   = [ren_avg.get("Non rénové",0), ren_avg.get("Rénové",0)]
    bars = ax.bar(labels, vals, color=[BLUE,GOLD], width=0.5)
    ax.yaxis.set_visible(False)
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+2,
                f"${b.get_height():.0f}K", ha="center", fontsize=6, color="#64748B")
    ax.tick_params(axis="x", labelsize=6.5)
    st.pyplot(fig); plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

# ── KEY TAKEAWAYS ──────────────────────────────────────────────────────────
wf_p   = ((dff[dff["waterfront"]==1]["price"].mean() / dff[dff["waterfront"]==0]["price"].mean()-1)*100) if (dff["waterfront"]==1).any() else 0
ren_p  = ((dff[dff["renovated"]=="Rénové"]["price"].mean() / dff[dff["renovated"]=="Non rénové"]["price"].mean()-1)*100) if (dff["renovated"]=="Rénové").any() else 0
top_g  = dff.groupby("grade")["price"].mean().idxmax()
top_z  = dff.groupby("zipcode")["price"].mean().idxmax()

st.markdown(f"""
<div class="takeaway">
  <h4>🔑 Key Takeaways</h4>
  <div class="tk-grid">
    <div class="tk-item"><p>🌊 <b>Waterfront Premium</b><br>Vue sur l'eau = prix supérieur de <b>{wf_p:.0f}%</b></p></div>
    <div class="tk-item"><p>🔨 <b>Renovation Impact</b><br>Rénovation augmente le prix de <b>{ren_p:.0f}%</b></p></div>
    <div class="tk-item"><p>⭐ <b>Top Grade : {top_g}</b><br>Grade avec le prix moyen le plus élevé du marché</p></div>
    <div class="tk-item"><p>📍 <b>Top ZIP : {top_z}</b><br>Quartier le plus cher du comté de King</p></div>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
csv = dff.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Télécharger les données filtrées",
                   data=csv, file_name="House-Data-filtered.csv", mime="text/csv")