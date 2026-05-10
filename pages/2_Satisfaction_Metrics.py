import streamlit as st
# pyrefly: ignore [missing-import]
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import theme_utils as tu

st.set_page_config(page_title="Satisfaction · Hospitality Intelligence", page_icon="⭐", layout="wide")

# ── Apply Theme ──────────────────────────────────────────────────────────────
tu.inject_airbnb_theme()

# ── Data ──────────────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.switch_page("Overview.py")

df = st.session_state.df

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⭐ Reviews")
    countries = ["All"] + sorted(df["country"].dropna().unique().tolist())
    sel_c = st.selectbox("Country", countries)
    min_reviews = st.slider("Min Reviews", 0, 200, 1)
    min_rating  = st.slider("Min Rating", 0, 100, 0)
    sel_super = st.checkbox("Superhosts", False)

fdf = df.copy()
if sel_c != "All":  fdf = fdf[fdf["country"] == sel_c]
fdf = fdf[fdf["num_reviews"] >= min_reviews]
fdf = fdf[fdf["rating"] >= min_rating]
if sel_super:       fdf = fdf[fdf["is_superhost"] == True]
rdf = fdf[fdf["rating"] > 0]

# ── Header ────────────────────────────────────────────────────────────────────
tu.airbnb_header("Guest Satisfaction", "Analysis of review scores, category breakdown, and host performance")

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
        tu.airbnb_metric_card(lbl, val)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 1: Category scores radar + bar ────────────────────────────────────
tu.airbnb_section_header("Review Category Breakdown")
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
    fig_radar.update_layout(title="Average Score by Category", polar=dict(radialaxis=dict(visible=True, range=[0,10])), height=380)
    tu.apply_plotly_theme(fig_radar)
    st.plotly_chart(fig_radar, use_container_width=True)

with c_b:
    score_df = pd.DataFrame({"category": score_labels, "score": avg_scores})
    score_df = score_df.sort_values("score", ascending=True)
    fig_bar = px.bar(score_df, x="score", y="category", orientation="h",
                     color="score",
                     color_continuous_scale=["#f7f7f7","#ff385c","#460479"],
                     range_x=[0, 10],
                     text="score",
                     labels={"score":"Avg Score (0–10)","category":""})
    fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_bar.update_layout(coloraxis_showscale=False, title="Category Scores Ranked", height=380)
    tu.apply_plotly_theme(fig_bar)
    st.plotly_chart(fig_bar, use_container_width=True)

# ── Section 2: Ratings by country & property type ─────────────────────────────
tu.airbnb_section_header("Ratings by Country & Property Type")
c_c, c_d = st.columns(2)

with c_c:
    cg = (rdf.groupby("country")["rating"]
              .agg(["mean","count"]).reset_index()
              .rename(columns={"mean":"avg_rating","count":"listings"})
              .query("listings >= 5")
              .sort_values("avg_rating", ascending=False))
    fig3 = px.bar(cg, x="country", y="avg_rating", text="avg_rating",
                  color="avg_rating",
                  color_continuous_scale=["#f7f7f7","#ff385c"],
                  labels={"country":"","avg_rating":"Avg Rating"},
                  range_y=[0,100])
    fig3.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    fig3.update_layout(title="Avg Rating by Country", coloraxis_showscale=False, height=360, xaxis_tickangle=-30)
    tu.apply_plotly_theme(fig3)
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
                  color_continuous_scale=["#f7f7f7","#ff385c"],
                  range_x=[0,100],
                  labels={"avg_rating":"Avg Rating","property_type":""})
    fig4.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    fig4.update_layout(title="Avg Rating by Property Type", coloraxis_showscale=False, height=360)
    tu.apply_plotly_theme(fig4)
    st.plotly_chart(fig4, use_container_width=True)

# ── Section 3: Reviews count, superhost comparison ─────────────────────────────
tu.airbnb_section_header("Review Volume & Superhost Impact")
c_e, c_f = st.columns(2)

with c_e:
    fig5 = px.scatter(
        rdf[(rdf["num_reviews"]<500) & (rdf["price"]<500) & (rdf["price"]>0)],
        x="num_reviews", y="rating", color="is_superhost",
        color_discrete_map={True:"#ff385c", False:"#dddddd"},
        opacity=0.6, size_max=8,
        labels={"num_reviews":"Number of Reviews","rating":"Rating Score","is_superhost":"Superhost"},
    )
    fig5.update_layout(title="Reviews Count vs Rating Score", height=360, legend=dict(title="Superhost", orientation="h", y=-0.15))
    tu.apply_plotly_theme(fig5)
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
    fig6.update_layout(barmode="group", title="Superhost vs Regular Host Scores", height=360, legend=dict(orientation="h", y=-0.15))
    tu.apply_plotly_theme(fig6)
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.caption(f"Showing {len(rdf):,} listings with review scores · Use sidebar filters to refine")
