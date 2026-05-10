import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import theme_utils as tu

st.set_page_config(page_title="Pricing · Hospitality Intelligence", page_icon="💰", layout="wide")

# ── Apply Theme ──────────────────────────────────────────────────────────────
tu.inject_airbnb_theme()

# ── Data ─────────────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.switch_page("Overview.py")

df = st.session_state.df

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💰 Pricing")
    countries = ["All"] + sorted(df["country"].dropna().unique().tolist())
    sel_c = st.selectbox("Country", countries)
    room_types = ["All"] + sorted(df["room_type"].dropna().unique().tolist())
    sel_r = st.selectbox("Room", room_types)
    pmax = int(df["price"].quantile(0.98))
    sel_p = st.slider("Max ($)", 0, pmax, pmax)
    sel_bed = st.slider("Beds", 0, int(df["bedrooms"].max()), int(df["bedrooms"].max()))

fdf = df.copy()
if sel_c != "All":  fdf = fdf[fdf["country"] == sel_c]
if sel_r != "All":  fdf = fdf[fdf["room_type"] == sel_r]
fdf = fdf[fdf["price"] <= sel_p]
fdf = fdf[fdf["bedrooms"] <= sel_bed]
fdf_priced = fdf[fdf["price"] > 0]

# ── Header ────────────────────────────────────────────────────────────────────
tu.airbnb_header("Pricing Strategy", "Deep dive into nightly rates, cleaning fees, and value drivers")

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
total_cost = fdf_priced["price"] + fdf_priced["cleaning_fee"]
for col,(val,lbl) in zip([c1,c2,c3,c4,c5],[
    (f"${fdf_priced['price'].mean():.0f}", "Avg Nightly Price"),
    (f"${fdf_priced['price'].median():.0f}", "Median Price"),
    (f"${fdf_priced['cleaning_fee'].mean():.0f}", "Avg Cleaning Fee"),
    (f"${total_cost.mean():.0f}", "Avg Total / Night"),
    (f"${fdf_priced['extra_people'].mean():.0f}", "Avg Extra Guest Fee"),
]):
    with col:
        tu.airbnb_metric_card(lbl, val)
st.markdown("<br>", unsafe_allow_html=True)

# ── Section 1: Price by country & room type ───────────────────────────────────
tu.airbnb_section_header("Price by Geography & Room Type")
c_a, c_b = st.columns(2)

with c_a:
    cg = fdf_priced.groupby("country")["price"].agg(["median","mean","count"]).reset_index()
    cg.columns = ["country","median","mean","count"]
    cg = cg[cg["count"] >= 5].sort_values("median", ascending=False)
    fig = px.bar(cg, x="country", y="median", text="median",
                 color="median", color_continuous_scale=["#f7f7f7","#ff385c"],
                 labels={"median":"Median Price ($)", "country":""})
    fig.update_traces(texttemplate='$%{text:.0f}', textposition='outside')
    fig.update_layout(title="Median Price by Country", coloraxis_showscale=False, height=360, xaxis_tickangle=-30)
    tu.apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

with c_b:
    rg = fdf_priced.groupby("room_type").agg(
        median_price=("price","median"), count=("price","count")).reset_index()
    fig2 = px.bar(rg, x="room_type", y="median_price", text="median_price",
                  color="room_type",
                  color_discrete_sequence=["#ff385c","#e00b41","#92174d","#460479"],
                  labels={"median_price":"Median Price ($)","room_type":""})
    fig2.update_traces(texttemplate='$%{text:.0f}', textposition='outside')
    fig2.update_layout(title="Median Price by Room Type", showlegend=False, height=360)
    tu.apply_plotly_theme(fig2)
    st.plotly_chart(fig2, use_container_width=True)

# ── Section 2: Bedrooms vs price & fee breakdown ───────────────────────────────
tu.airbnb_section_header("Capacity & Fee Structure")
c_c, c_d = st.columns(2)

with c_c:
    bed_price = (fdf_priced[fdf_priced["bedrooms"]<=10]
                 .groupby("bedrooms")["price"].median().reset_index())
    fig3 = px.line(bed_price, x="bedrooms", y="price",
                   markers=True, color_discrete_sequence=["#ff385c"],
                   labels={"bedrooms":"Number of Bedrooms","price":"Median Price ($)"})
    fig3.update_traces(marker=dict(size=9, color="#ff385c"), line=dict(width=3))
    fig3.update_layout(title="Price Scales with Bedrooms", height=340)
    tu.apply_plotly_theme(fig3)
    st.plotly_chart(fig3, use_container_width=True)

with c_d:
    fee_df = fdf_priced[["price","cleaning_fee","security_deposit","extra_people"]].mean()
    fig4 = go.Figure(go.Pie(
        labels=["Base Price","Cleaning Fee","Security Deposit","Extra People Fee"],
        values=[fee_df["price"], fee_df["cleaning_fee"],
                fee_df["security_deposit"], fee_df["extra_people"]],
        hole=0.5,
        marker_colors=["#ff385c","#e00b41","#92174d","#dddddd"],
        textinfo="label+percent",
    ))
    fig4.update_layout(title="Average Fee Breakdown", height=340)
    tu.apply_plotly_theme(fig4)
    st.plotly_chart(fig4, use_container_width=True)

# ── Section 3: Price scatter vs review score ──────────────────────────────────
tu.airbnb_section_header("Price vs Quality & Value")

try:
    # ROBUST CLEANING: Ensure columns are numeric and filter for valid scatter data
    scatter_df = fdf_priced.copy()
    
    # Categorical cleaning
    for col in ["room_type", "property_type"]:
        if col in scatter_df.columns:
            scatter_df[col] = scatter_df[col].fillna("Unknown").astype(str)
            
    # Numeric cleaning
    for col in ["price", "review_score", "accommodates", "bedrooms"]:
        if col in scatter_df.columns:
            scatter_df[col] = pd.to_numeric(scatter_df[col], errors='coerce')

    # Drop NaNs and non-finite values for core plot columns
    scatter_df = scatter_df.dropna(subset=["review_score", "accommodates", "price"])
    scatter_df = scatter_df[
        (np.isfinite(scatter_df["review_score"])) & 
        (np.isfinite(scatter_df["accommodates"])) &
        (np.isfinite(scatter_df["price"]))
    ]
    
    # Filter for positive values to ensure Plotly can render size correctly
    scatter_df = scatter_df[
        (scatter_df["review_score"] > 0) & 
        (scatter_df["accommodates"] > 0) &
        (scatter_df["price"] > 0)
    ]

    # Apply price outlier filter safely
    if not scatter_df.empty:
        q95 = scatter_df["price"].quantile(0.95)
        if pd.notna(q95):
            scatter_df = scatter_df[scatter_df["price"] <= q95]

    c_e, c_f = st.columns(2)
    with c_e:
        if not scatter_df.empty:
            fig5 = px.scatter(scatter_df, x="price", y="review_score",
                              color="room_type", size="accommodates",
                              opacity=0.65, size_max=18,
                              color_discrete_sequence=["#ff385c","#460479","#6a6a6a","#222222"],
                              labels={"price":"Price ($/night)","review_score":"Review Score",
                                      "room_type":"Room Type"},
                              hover_data=["property_type","bedrooms"])
            fig5.update_layout(title="Price vs Review Score (sized by capacity)", height=380)
            tu.apply_plotly_theme(fig5)
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("💡 Insufficient data for the Price vs Review Score scatter plot with current filters.")

    with c_f:
        # Box plot for Price distribution by top property types
        if not fdf_priced.empty:
            prop_counts = fdf_priced["property_type"].value_counts()
            if not prop_counts.empty:
                top_props = prop_counts.head(7).index
                box_df = fdf_priced[fdf_priced["property_type"].isin(top_props)].copy()
                box_df["price"] = pd.to_numeric(box_df["price"], errors='coerce')
                box_df = box_df[box_df["price"] > 0].dropna(subset=["price"])
                
                if not box_df.empty:
                    fig6 = px.box(box_df, x="property_type", y="price",
                                  color="property_type",
                                  color_discrete_sequence=["#ff385c", "#e00b41", "#92174d", "#460479", "#222222", "#6a6a6a", "#dddddd"],
                                  labels={"property_type":"","price":"Price ($/night)"})
                    fig6.update_layout(title="Price Distribution by Top Property Types", showlegend=False, height=380, xaxis_tickangle=-30)
                    tu.apply_plotly_theme(fig6)
                    st.plotly_chart(fig6, use_container_width=True)
                else:
                    st.info("💡 No valid price data for property type distribution.")
            else:
                st.info("💡 No property type data available.")
        else:
            st.info("💡 No listings available for the property type breakdown.")

except Exception as e:
    st.error(f"⚠️ Error rendering Price vs Quality charts: {e}")
    st.caption("This may be due to missing or invalid data in the dataset. Try adjusting your filters.")


st.markdown("---")
st.caption(f"Showing {len(fdf_priced):,} priced listings · Use sidebar filters to narrow results")
