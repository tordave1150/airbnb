import streamlit as st
# pyrefly: ignore [missing-import]
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Reviews & Ratings · Airbnb", page_icon="⭐", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  h1,h2,h3 { font-family: 'Syne', sans-serif !important; }
  .page-header { background: linear-gradient(135deg, #F5A623 0%, #E87722 100%);
    color: white; padding: 1.5rem 2rem; border-radius: 14px; margin-bottom: 1.5rem; }
  .page-header h1 { color: white !important; font-size: 2rem; margin: 0; }
  .page-header p  { color: rgba(255,255,255,0.85); margin: 0.3rem 0 0; }
  .kpi { background: white; border-radius: 12px; padding: 1.2rem 1.4rem;
    border: 1px solid #f0f0f0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align:center; }
  .kv  { font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:700; color:#F5A623; }
  .kl  { color:#717171; font-size:0.82rem; margin-top:0.2rem; }
  .sh  { font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700;
    color:#222; margin:1.8rem 0 0.8rem; border-left:4px solid #F5A623; padding-left:0.7rem; }
  .star-row { display:flex; align-items:center; gap:8px; margin-bottom:6px; }
  .star-label { width:140px; font-size:0.85rem; color:#555; }
  .star-bar { flex:1; height:12px; background:#f0f0f0; border-radius:6px; overflow:hidden; }
  .star-fill { height:100%; border-radius:6px; background: linear-gradient(90deg, #F5A623, #E87722); }
  .star-score { width:40px; font-size:0.85rem; font-weight:600; color:#333; text-align:right; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return pymongo.MongoClient(st.secrets["mongo"]["uri"])

@st.cache_data(ttl=300)
def load_data():
    col = get_client()["sample_airbnb"]["listingsAndReviews"]
    docs = list(col.find({}, {
        "name":1,"property_type":1,"room_type":1,"price":1,
        "number_of_reviews":1,"review_scores":1,"host":1,
        "address":1,"amenities":1,"first_review":1,"last_review":1,
        "cancellation_policy":1,
    }))
    rows = []
    for d in docs:
        rv   = d.get("review_scores",{})
        host = d.get("host",{})
        addr = d.get("address",{})
        rows.append({
            "name": d.get("name",""),
            "property_type": d.get("property_type","Other"),
            "room_type": d.get("room_type","Other"),
            "price": float(d.get("price",0) or 0),
            "num_reviews": int(d.get("number_of_reviews",0) or 0),
            "rating":         float(rv.get("review_scores_rating",0) or 0),
            "accuracy":       float(rv.get("review_scores_accuracy",0) or 0),
            "cleanliness":    float(rv.get("review_scores_cleanliness",0) or 0),
            "checkin":        float(rv.get("review_scores_checkin",0) or 0),
            "communication":  float(rv.get("review_scores_communication",0) or 0),
            "location":       float(rv.get("review_scores_location",0) or 0),
            "value":          float(rv.get("review_scores_value",0) or 0),
            "country": addr.get("country","Unknown"),
            "market": addr.get("market","Unknown"),
            "is_superhost": host.get("host_is_superhost",False),
            "host_listings": int(host.get("host_total_listings_count",1) or 1),
            "amenities_count": len(d.get("amenities",[])),
            "cancellation_policy": d.get("cancellation_policy","Unknown"),
            "first_review": d.get("first_review"),
            "last_review":  d.get("last_review"),
        })
    return pd.DataFrame(rows)

try:
    df = load_data()
except Exception as e:
    st.error(f"MongoDB error: {e}")
    st.stop()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⭐ Review Filters")
    countries = ["All"] + sorted(df["country"].dropna().unique().tolist())
    sel_c = st.selectbox("Country", countries)
    min_reviews = st.slider("Minimum # of Reviews", 0, 200, 1)
    min_rating  = st.slider("Minimum Rating Score", 0, 100, 0)
    sel_super = st.checkbox("Superhosts Only", False)

fdf = df.copy()
if sel_c != "All":  fdf = fdf[fdf["country"] == sel_c]
fdf = fdf[fdf["num_reviews"] >= min_reviews]
fdf = fdf[fdf["rating"] >= min_rating]
if sel_super:       fdf = fdf[fdf["is_superhost"] == True]
rdf = fdf[fdf["rating"] > 0]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>⭐ Reviews & Ratings</h1>
  <p>Guest satisfaction analysis · scores, patterns & what drives great reviews</p>
</div>""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
for col,(val,lbl) in zip([c1,c2,c3,c4,c5],[
    (f"{rdf['rating'].mean():.1f}", "Avg Rating (0–100)"),
    (f"{rdf['cleanliness'].mean():.2f}", "Avg Cleanliness (0–10)"),
    (f"{rdf['location'].mean():.2f}", "Avg Location (0–10)"),
    (f"{rdf['value'].mean():.2f}", "Avg Value (0–10)"),
    (f"{rdf['num_reviews'].sum():,}", "Total Reviews"),
]):
    with col:
        st.markdown(f'<div class="kpi"><div class="kv">{val}</div><div class="kl">{lbl}</div></div>',
                    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 1: Category scores radar + bar ────────────────────────────────────
st.markdown('<div class="sh">Review Category Breakdown</div>', unsafe_allow_html=True)
c_a, c_b = st.columns(2)

score_cols = ["accuracy","cleanliness","checkin","communication","location","value"]
score_labels = ["Accuracy","Cleanliness","Check-in","Communication","Location","Value"]
avg_scores = [rdf[c].mean() for c in score_cols]

with c_a:
    fig_radar = go.Figure(go.Scatterpolar(
        r=avg_scores + [avg_scores[0]],
        theta=score_labels + [score_labels[0]],
        fill='toself',
        fillcolor='rgba(245,166,35,0.15)',
        line=dict(color="#F5A623", width=2.5),
        marker=dict(size=7, color="#F5A623"),
    ))
    fig_radar.update_layout(
        title="Average Score by Category",
        polar=dict(radialaxis=dict(visible=True, range=[0,10],
                                   tickfont=dict(size=10))),
        height=380, margin=dict(l=20,r=20,t=50,b=20),
        font=dict(family="DM Sans"), paper_bgcolor="white",
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with c_b:
    score_df = pd.DataFrame({"category": score_labels, "score": avg_scores})
    score_df = score_df.sort_values("score", ascending=True)
    fig_bar = px.bar(score_df, x="score", y="category", orientation="h",
                     color="score",
                     color_continuous_scale=["#FFE0B2","#F5A623","#E87722"],
                     range_x=[0, 10],
                     text="score",
                     labels={"score":"Avg Score (0–10)","category":""})
    fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_bar.update_layout(coloraxis_showscale=False, title="Category Scores Ranked",
                          height=380, plot_bgcolor="white", paper_bgcolor="white",
                          margin=dict(l=0,r=40,t=40,b=0), font=dict(family="DM Sans"))
    st.plotly_chart(fig_bar, use_container_width=True)

# ── Section 2: Ratings by country & property type ─────────────────────────────
st.markdown('<div class="sh">Ratings by Country & Property Type</div>', unsafe_allow_html=True)
c_c, c_d = st.columns(2)

with c_c:
    cg = (rdf.groupby("country")["rating"]
              .agg(["mean","count"]).reset_index()
              .rename(columns={"mean":"avg_rating","count":"listings"})
              .query("listings >= 5")
              .sort_values("avg_rating", ascending=False))
    fig3 = px.bar(cg, x="country", y="avg_rating", text="avg_rating",
                  color="avg_rating",
                  color_continuous_scale=["#FFE0B2","#E87722"],
                  labels={"country":"","avg_rating":"Avg Rating"},
                  range_y=[0,100])
    fig3.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    fig3.update_layout(title="Avg Rating by Country", coloraxis_showscale=False,
                       height=360, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"),
                       xaxis_tickangle=-30)
    st.plotly_chart(fig3, use_container_width=True)

with c_d:
    top_props = rdf["property_type"].value_counts().head(8).index
    pg = (rdf[rdf["property_type"].isin(top_props)]
              .groupby("property_type")["rating"]
              .agg(["mean","count"]).reset_index()
              .rename(columns={"mean":"avg_rating","count":"listings"})
              .sort_values("avg_rating"))
    fig4 = px.bar(pg, x="avg_rating", y="property_type", orientation="h",
                  text="avg_rating",
                  color="avg_rating",
                  color_continuous_scale=["#FFE0B2","#E87722"],
                  range_x=[0,100],
                  labels={"avg_rating":"Avg Rating","property_type":""})
    fig4.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    fig4.update_layout(title="Avg Rating by Property Type", coloraxis_showscale=False,
                       height=360, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=40,r=40,t=40,b=0), font=dict(family="DM Sans"))
    st.plotly_chart(fig4, use_container_width=True)

# ── Section 3: Reviews count, superhost comparison ─────────────────────────────
st.markdown('<div class="sh">Review Volume & Superhost Impact</div>', unsafe_allow_html=True)
c_e, c_f = st.columns(2)

with c_e:
    fig5 = px.scatter(
        rdf[(rdf["num_reviews"]<500) & (rdf["price"]<500) & (rdf["price"]>0)],
        x="num_reviews", y="rating", color="is_superhost",
        color_discrete_map={True:"#F5A623", False:"#CCCCCC"},
        opacity=0.6, size_max=8,
        labels={"num_reviews":"Number of Reviews","rating":"Rating Score","is_superhost":"Superhost"},
    )
    fig5.update_layout(title="Reviews Count vs Rating Score",
                       height=360, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"),
                       legend=dict(title="Superhost", orientation="h", y=-0.15))
    fig5.update_xaxes(showgrid=True, gridcolor="#f5f5f5")
    fig5.update_yaxes(showgrid=True, gridcolor="#f5f5f5")
    st.plotly_chart(fig5, use_container_width=True)

with c_f:
    # Superhost vs regular host comparison across all score categories
    sh_yes = rdf[rdf["is_superhost"]==True][score_cols].mean()
    sh_no  = rdf[rdf["is_superhost"]==False][score_cols].mean()
    comp_df = pd.DataFrame({
        "Category": score_labels,
        "Superhost": sh_yes.values,
        "Regular Host": sh_no.values,
    })
    fig6 = go.Figure()
    fig6.add_trace(go.Bar(x=comp_df["Category"], y=comp_df["Superhost"],
                          name="Superhost", marker_color="#F5A623"))
    fig6.add_trace(go.Bar(x=comp_df["Category"], y=comp_df["Regular Host"],
                          name="Regular Host", marker_color="#D3D3D3"))
    fig6.update_layout(barmode="group", title="Superhost vs Regular Host Scores",
                       height=360, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"),
                       legend=dict(orientation="h", y=-0.15),
                       yaxis=dict(range=[0,10], showgrid=True, gridcolor="#f5f5f5"))
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.caption(f"Showing {len(rdf):,} listings with review scores · Use sidebar filters to refine")
