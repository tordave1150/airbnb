import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import theme_utils as tu

st.set_page_config(page_title="Geography · Hospitality Intelligence", page_icon="🌍", layout="wide")

# ── Apply Theme ──────────────────────────────────────────────────────────────
tu.inject_airbnb_theme()

# ── Data ──────────────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.switch_page("Overview.py")

df = st.session_state.df

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌍 Geography")
    countries = ["All"] + sorted(df["country"].dropna().unique().tolist())
    sel_c = st.selectbox("Country", countries)
    sel_rt = st.selectbox("Room", ["All"]+sorted(df["room_type"].dropna().unique().tolist()))
    pmax = int(df["price"].quantile(0.98))
    sel_p = st.slider("Max ($)", 0, pmax, pmax)

fdf = df.copy()
if sel_c != "All":  fdf = fdf[fdf["country"] == sel_c]
if sel_rt != "All": fdf = fdf[fdf["room_type"] == sel_rt]
fdf = fdf[fdf["price"] <= sel_p]

# ── Header ─────────────────────────────────────────────────────────────────────
tu.airbnb_header("Market Geography", "Regional distribution, market pricing, and country-level performance benchmarks")

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
for col,(val,lbl) in zip([c1,c2,c3,c4,c5],[
    (f"{fdf['country'].nunique()}", "Countries"),
    (f"{fdf['market'].nunique()}", "Markets"),
    (f"${fdf[fdf['price']>0]['price'].median():.0f}", "Global Median Price"),
    (f"{fdf[fdf['price']>0].groupby('country')['price'].median().idxmax()}", "Highest-Price Country"),
    (f"{fdf['country'].value_counts().idxmax()}", "Most Listings Country"),
]):
    with col:
        tu.airbnb_metric_card(lbl, val)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 1: Choropleth world map ───────────────────────────────────────────
tu.airbnb_section_header("Global Listings Map")

country_stats = (fdf[fdf["price"]>0].groupby(["country","country_code"])
                 .agg(listings=("price","count"), median_price=("price","median"),
                      avg_rating=("rating","mean"))
                 .reset_index())

tab_map1, tab_map2 = st.tabs(["📊 Listings Count", "💲 Median Price"])
with tab_map1:
    fig_map1 = px.choropleth(country_stats, locations="country", locationmode="country names",
                              color="listings", hover_name="country",
                              color_continuous_scale=["#f7f7f7","#ff385c","#e00b41"],
                              labels={"listings":"Listings"})
    fig_map1.update_layout(height=420)
    tu.apply_plotly_theme(fig_map1)
    fig_map1.update_geos(showframe=False, showcoastlines=True, coastlinecolor="#dddddd", bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map1, use_container_width=True)

with tab_map2:
    fig_map2 = px.choropleth(country_stats, locations="country", locationmode="country names",
                              color="median_price", hover_name="country",
                              color_continuous_scale=["#f7f7f7","#460479"],
                              labels={"median_price":"Median Price ($)"})
    fig_map2.update_layout(height=420)
    tu.apply_plotly_theme(fig_map2)
    fig_map2.update_geos(showframe=False, showcoastlines=True, coastlinecolor="#dddddd", bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map2, use_container_width=True)

# ── Section 2: Market breakdown ──────────────────────────────────────────────
tu.airbnb_section_header("Top Markets Deep Dive")
c_a, c_b = st.columns(2)

with c_a:
    top_markets = (fdf[fdf["price"]>0].groupby("market")
                   .agg(listings=("price","count"), median_price=("price","median"))
                   .reset_index()
                   .query("listings >= 5")
                   .sort_values("listings", ascending=False)
                   .head(15))
    fig3 = px.treemap(top_markets, path=["market"], values="listings",
                      color="median_price",
                      color_continuous_scale=["#f7f7f7","#ff385c"],
                      labels={"median_price":"Median Price ($)"},
                      hover_data={"listings":True,"median_price":":.0f"})
    fig3.update_layout(title="Market Size (colored by median price)", height=400)
    tu.apply_plotly_theme(fig3)
    st.plotly_chart(fig3, use_container_width=True)

with c_b:
    top_market_list = top_markets["market"].tolist()
    mdf = fdf[(fdf["market"].isin(top_market_list)) & (fdf["price"]>0)]
    fig4 = px.box(mdf, x="market", y="price",
                  color="market",
                  color_discrete_sequence=["#ff385c","#e00b41","#92174d","#460479","#dddddd"],
                  labels={"market":"","price":"Price ($/night)"})
    fig4.update_layout(title="Price Distribution in Top Markets", showlegend=False, height=400, xaxis_tickangle=-40)
    tu.apply_plotly_theme(fig4)
    st.plotly_chart(fig4, use_container_width=True)

# ── Section 3: Scatter map + availability ─────────────────────────────────────
tu.airbnb_section_header("Listing Locations & Availability")
c_c, c_d = st.columns(2)

with c_c:
    geo_df = fdf.dropna(subset=["lat","lon"])
    geo_df = geo_df[(geo_df["lat"].between(-90,90)) & (geo_df["lon"].between(-180,180))]
    geo_df = geo_df[geo_df["price"]>0].head(3000)
    fig5 = px.scatter_geo(geo_df, lat="lat", lon="lon",
                          color="price", size="num_reviews",
                          hover_name="market",
                          hover_data={"price":True,"rating":True,"lat":False,"lon":False},
                          color_continuous_scale=["#f7f7f7","#ff385c","#e00b41"],
                          projection="natural earth", size_max=12,
                          labels={"price":"Price ($)"})
    fig5.update_layout(title="Listing Locations (sized by review count)", height=400)
    tu.apply_plotly_theme(fig5)
    fig5.update_geos(showframe=False, coastlinecolor="#dddddd", bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig5, use_container_width=True)

with c_d:
    avail_country = (fdf.groupby("country")
                     .agg(avail_30=("availability_30","mean"),
                          avail_365=("availability_365","mean"),
                          listings=("price","count"))
                     .reset_index()
                     .query("listings >= 5")
                     .sort_values("avail_365"))
    fig6 = go.Figure()
    fig6.add_trace(go.Bar(x=avail_country["country"], y=avail_country["avail_30"],
                          name="Avg Available (30 days)", marker_color="#AED6F1"))
    fig6.add_trace(go.Bar(x=avail_country["country"], y=avail_country["avail_365"],
                          name="Avg Available (365 days)", marker_color="#4A90D9"))
    fig6.update_layout(barmode="group", title="Avg Availability by Country", height=400, legend=dict(orientation="h", y=-0.2), xaxis_tickangle=-30)
    tu.apply_plotly_theme(fig6)
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.caption(f"Showing {len(fdf):,} listings across {fdf['country'].nunique()} countries · Use sidebar to filter")
