import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Geographic Analysis · Airbnb", page_icon="🌍", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  h1,h2,h3 { font-family: 'Syne', sans-serif !important; }
  .page-header { background: linear-gradient(135deg, #4A90D9 0%, #2C5F8A 100%);
    color: white; padding: 1.5rem 2rem; border-radius: 14px; margin-bottom: 1.5rem; }
  .page-header h1 { color: white !important; font-size: 2rem; margin: 0; }
  .page-header p  { color: rgba(255,255,255,0.85); margin: 0.3rem 0 0; }
  .kpi { background: white; border-radius: 12px; padding: 1.2rem 1.4rem;
    border: 1px solid #f0f0f0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align:center; }
  .kv  { font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:700; color:#4A90D9; }
  .kl  { color:#717171; font-size:0.82rem; margin-top:0.2rem; }
  .sh  { font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700;
    color:#222; margin:1.8rem 0 0.8rem; border-left:4px solid #4A90D9; padding-left:0.7rem; }
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
        "price":1,"property_type":1,"room_type":1,
        "address":1,"review_scores":1,"host":1,
        "number_of_reviews":1,"bedrooms":1,"amenities":1,
        "availability":1,"cancellation_policy":1,
    }))
    rows = []
    for d in docs:
        addr  = d.get("address",{})
        loc   = addr.get("location",{})
        coords = loc.get("coordinates",[None,None]) if loc else [None,None]
        rv    = d.get("review_scores",{})
        avail = d.get("availability",{})
        rows.append({
            "price": float(str(d.get("price",0) or 0)),
            "property_type": d.get("property_type","Other"),
            "room_type": d.get("room_type","Other"),
            "country": addr.get("country","Unknown"),
            "country_code": addr.get("country_code",""),
            "market": addr.get("market","Unknown"),
            "suburb": addr.get("suburb",""),
            "lat": coords[1] if len(coords)>1 else None,
            "lon": coords[0] if len(coords)>0 else None,
            "rating": float(str(rv.get("review_scores_rating",0) or 0)),
            "num_reviews": int(float(str(d.get("number_of_reviews",0) or 0))),
            "bedrooms": float(str(d.get("bedrooms",0) or 0)),
            "amenities_count": len(d.get("amenities",[])),
            "is_superhost": bool(d.get("host",{}).get("host_is_superhost",False)),
            "availability_30": int(float(str(avail.get("availability_30",0) or 0))),
            "availability_365": int(float(str(avail.get("availability_365",0) or 0))),
            "cancellation_policy": d.get("cancellation_policy","Unknown"),
        })
    return pd.DataFrame(rows)

try:
    df = load_data()
except Exception as e:
    st.error(f"MongoDB error: {e}")
    st.stop()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌍 Geo Filters")
    countries = ["All"] + sorted(df["country"].dropna().unique().tolist())
    sel_c = st.selectbox("Country", countries)
    sel_rt = st.selectbox("Room Type", ["All"]+sorted(df["room_type"].dropna().unique().tolist()))
    pmax = int(df["price"].quantile(0.98))
    sel_p = st.slider("Max Price", 0, pmax, pmax)

fdf = df.copy()
if sel_c != "All":  fdf = fdf[fdf["country"] == sel_c]
if sel_rt != "All": fdf = fdf[fdf["room_type"] == sel_rt]
fdf = fdf[fdf["price"] <= sel_p]

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>🌍 Geographic & Market Analysis</h1>
  <p>Where listings cluster · market pricing · country-level benchmarks</p>
</div>""", unsafe_allow_html=True)

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
        st.markdown(f'<div class="kpi"><div class="kv">{val}</div><div class="kl">{lbl}</div></div>',
                    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 1: Choropleth world map ───────────────────────────────────────────
st.markdown('<div class="sh">Global Listings Map</div>', unsafe_allow_html=True)

country_stats = (fdf[fdf["price"]>0].groupby(["country","country_code"])
                 .agg(listings=("price","count"), median_price=("price","median"),
                      avg_rating=("rating","mean"))
                 .reset_index())

tab_map1, tab_map2 = st.tabs(["📊 Listings Count", "💲 Median Price"])
with tab_map1:
    fig_map1 = px.choropleth(country_stats, locations="country_code",
                              color="listings", hover_name="country",
                              color_continuous_scale=["#D6EAF8","#4A90D9","#1A5276"],
                              labels={"listings":"Listings"})
    fig_map1.update_layout(height=420, margin=dict(l=0,r=0,t=20,b=0),
                            font=dict(family="DM Sans"),
                            geo=dict(showframe=False, showcoastlines=True,
                                     coastlinecolor="#dddddd", bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_map1, use_container_width=True)

with tab_map2:
    fig_map2 = px.choropleth(country_stats, locations="country_code",
                              color="median_price", hover_name="country",
                              color_continuous_scale=["#FDEBD0","#E67E22","#784212"],
                              labels={"median_price":"Median Price ($)"})
    fig_map2.update_layout(height=420, margin=dict(l=0,r=0,t=20,b=0),
                            font=dict(family="DM Sans"),
                            geo=dict(showframe=False, showcoastlines=True,
                                     coastlinecolor="#dddddd", bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_map2, use_container_width=True)

# ── Section 2: Market breakdown ──────────────────────────────────────────────
st.markdown('<div class="sh">Top Markets Deep Dive</div>', unsafe_allow_html=True)
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
                      color_continuous_scale=["#D6EAF8","#4A90D9"],
                      labels={"median_price":"Median Price ($)"},
                      hover_data={"listings":True,"median_price":":.0f"})
    fig3.update_layout(title="Market Size (colored by median price)",
                       height=400, margin=dict(l=0,r=0,t=40,b=0),
                       font=dict(family="DM Sans"))
    st.plotly_chart(fig3, use_container_width=True)

with c_b:
    top_market_list = top_markets["market"].tolist()
    mdf = fdf[(fdf["market"].isin(top_market_list)) & (fdf["price"]>0)]
    fig4 = px.box(mdf, x="market", y="price",
                  color="market",
                  color_discrete_sequence=px.colors.sequential.Blues_r,
                  labels={"market":"","price":"Price ($/night)"})
    fig4.update_layout(title="Price Distribution in Top Markets",
                       showlegend=False, height=400,
                       plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"),
                       xaxis_tickangle=-40)
    fig4.update_yaxes(range=[0, fdf["price"].quantile(0.95)],
                      showgrid=True, gridcolor="#f5f5f5")
    st.plotly_chart(fig4, use_container_width=True)

# ── Section 3: Scatter map + availability ─────────────────────────────────────
st.markdown('<div class="sh">Listing Locations & Availability</div>', unsafe_allow_html=True)
c_c, c_d = st.columns(2)

with c_c:
    geo_df = fdf.dropna(subset=["lat","lon"])
    geo_df = geo_df[(geo_df["lat"].between(-90,90)) & (geo_df["lon"].between(-180,180))]
    geo_df = geo_df[geo_df["price"]>0].head(3000)
    fig5 = px.scatter_geo(geo_df, lat="lat", lon="lon",
                          color="price", size="num_reviews",
                          hover_name="market",
                          hover_data={"price":True,"rating":True,"lat":False,"lon":False},
                          color_continuous_scale=["#AED6F1","#4A90D9","#1A5276"],
                          projection="natural earth", size_max=12,
                          labels={"price":"Price ($)"})
    fig5.update_layout(title="Listing Locations (sized by review count)",
                       height=400, margin=dict(l=0,r=0,t=40,b=0),
                       font=dict(family="DM Sans"),
                       geo=dict(showframe=False, coastlinecolor="#dddddd",
                                bgcolor="rgba(0,0,0,0)"))
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
    fig6.update_layout(barmode="group", title="Avg Availability by Country",
                       height=400, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"),
                       legend=dict(orientation="h", y=-0.2),
                       xaxis_tickangle=-30)
    fig6.update_yaxes(showgrid=True, gridcolor="#f5f5f5")
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.caption(f"Showing {len(fdf):,} listings across {fdf['country'].nunique()} countries · Use sidebar to filter")
