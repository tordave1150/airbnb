import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Price Analysis · Airbnb", page_icon="💰", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  h1,h2,h3 { font-family: 'Syne', sans-serif !important; }
  .page-header { background: linear-gradient(135deg, #FC642D 0%, #BD1E59 100%);
    color: white; padding: 1.5rem 2rem; border-radius: 14px; margin-bottom: 1.5rem; }
  .page-header h1 { color: white !important; font-size: 2rem; margin: 0; }
  .page-header p { color: rgba(255,255,255,0.85); margin: 0.3rem 0 0; }
  .kpi { background: white; border-radius: 12px; padding: 1.2rem 1.4rem;
    border: 1px solid #f0f0f0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align:center;}
  .kv { font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:700; color:#FC642D;}
  .kl { color:#717171; font-size:0.82rem; margin-top:0.2rem; }
  .sh { font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700;
    color:#222; margin:1.8rem 0 0.8rem; border-left:4px solid #FC642D; padding-left:0.7rem;}
</style>
""", unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return pymongo.MongoClient(st.secrets["mongo"]["uri"])

@st.cache_data(ttl=300)
def load_data():
    col = get_client()["sample_airbnb"]["listingsAndReviews"]
    docs = list(col.find({}, {
        "price":1,"cleaning_fee":1,"security_deposit":1,"extra_people":1,
        "property_type":1,"room_type":1,"bedrooms":1,"beds":1,"accommodates":1,
        "address":1,"cancellation_policy":1,"amenities":1,"review_scores":1,
        "host":1,"minimum_nights":1,
    }))
    rows = []
    for d in docs:
        addr = d.get("address",{})
        rv   = d.get("review_scores",{})
        rows.append({
            "price": float(str(d.get("price",0) or 0)),
            "cleaning_fee": float(str(d.get("cleaning_fee",0) or 0)),
            "security_deposit": float(str(d.get("security_deposit",0) or 0)),
            "extra_people": float(str(d.get("extra_people",0) or 0)),
            "property_type": d.get("property_type","Other"),
            "room_type": d.get("room_type","Other"),
            "bedrooms": float(str(d.get("bedrooms",0) or 0)),
            "beds": float(str(d.get("beds",0) or 0)),
            "accommodates": int(float(str(d.get("accommodates",0) or 0))),
            "country": addr.get("country","Unknown"),
            "market": addr.get("market","Unknown"),
            "cancellation_policy": d.get("cancellation_policy","Unknown"),
            "amenities_count": len(d.get("amenities",[])),
            "review_score": float(str(rv.get("review_scores_rating",0) or 0)),
            "review_value": float(str(rv.get("review_scores_value",0) or 0)),
            "is_superhost": d.get("host",{}).get("host_is_superhost", False),
            "min_nights": int(d.get("minimum_nights",1) or 1),
        })
    return pd.DataFrame(rows)

try:
    df = load_data()
except Exception as e:
    st.error(f"MongoDB connection error: {e}")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💰 Price Filters")
    countries = ["All"] + sorted(df["country"].dropna().unique().tolist())
    sel_c = st.selectbox("Country", countries)
    room_types = ["All"] + sorted(df["room_type"].dropna().unique().tolist())
    sel_r = st.selectbox("Room Type", room_types)
    pmax = int(df["price"].quantile(0.98))
    sel_p = st.slider("Max Price ($/night)", 0, pmax, pmax)
    sel_bed = st.slider("Bedrooms (max)", 0, int(df["bedrooms"].max()), int(df["bedrooms"].max()))

fdf = df.copy()
if sel_c != "All":  fdf = fdf[fdf["country"] == sel_c]
if sel_r != "All":  fdf = fdf[fdf["room_type"] == sel_r]
fdf = fdf[fdf["price"] <= sel_p]
fdf = fdf[fdf["bedrooms"] <= sel_bed]
fdf_priced = fdf[fdf["price"] > 0]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>💰 Price Analysis</h1>
  <p>Deep dive into pricing patterns, fees, and value drivers across listings</p>
</div>""", unsafe_allow_html=True)

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
        st.markdown(f'<div class="kpi"><div class="kv">{val}</div><div class="kl">{lbl}</div></div>',
                    unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Section 1: Price by country & room type ───────────────────────────────────
st.markdown('<div class="sh">Price by Geography & Room Type</div>', unsafe_allow_html=True)
c_a, c_b = st.columns(2)

with c_a:
    cg = fdf_priced.groupby("country")["price"].agg(["median","mean","count"]).reset_index()
    cg.columns = ["country","median","mean","count"]
    cg = cg[cg["count"] >= 5].sort_values("median", ascending=False)
    fig = px.bar(cg, x="country", y="median", text="median",
                 color="median", color_continuous_scale=["#FFD9DF","#FC642D"],
                 labels={"median":"Median Price ($)", "country":""})
    fig.update_traces(texttemplate='$%{text:.0f}', textposition='outside')
    fig.update_layout(title="Median Price by Country", coloraxis_showscale=False,
                      height=360, plot_bgcolor="white", paper_bgcolor="white",
                      margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"),
                      xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

with c_b:
    rg = fdf_priced.groupby("room_type").agg(
        median_price=("price","median"), count=("price","count")).reset_index()
    fig2 = px.bar(rg, x="room_type", y="median_price", text="median_price",
                  color="room_type",
                  color_discrete_sequence=["#FC642D","#FF8A65","#FFB89A","#FFD9DF"],
                  labels={"median_price":"Median Price ($)","room_type":""})
    fig2.update_traces(texttemplate='$%{text:.0f}', textposition='outside')
    fig2.update_layout(title="Median Price by Room Type", showlegend=False,
                       height=360, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"))
    st.plotly_chart(fig2, use_container_width=True)

# ── Section 2: Bedrooms vs price & fee breakdown ───────────────────────────────
st.markdown('<div class="sh">Capacity & Fee Structure</div>', unsafe_allow_html=True)
c_c, c_d = st.columns(2)

with c_c:
    bed_price = (fdf_priced[fdf_priced["bedrooms"]<=10]
                 .groupby("bedrooms")["price"].median().reset_index())
    fig3 = px.line(bed_price, x="bedrooms", y="price",
                   markers=True, color_discrete_sequence=["#FC642D"],
                   labels={"bedrooms":"Number of Bedrooms","price":"Median Price ($)"})
    fig3.update_traces(marker=dict(size=9, color="#FC642D"),
                       line=dict(width=3))
    fig3.update_layout(title="Price Scales with Bedrooms",
                       height=340, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"))
    fig3.update_xaxes(showgrid=True, gridcolor="#f5f5f5", dtick=1)
    fig3.update_yaxes(showgrid=True, gridcolor="#f5f5f5")
    st.plotly_chart(fig3, use_container_width=True)

with c_d:
    fee_df = fdf_priced[["price","cleaning_fee","security_deposit","extra_people"]].mean()
    fig4 = go.Figure(go.Pie(
        labels=["Base Price","Cleaning Fee","Security Deposit","Extra People Fee"],
        values=[fee_df["price"], fee_df["cleaning_fee"],
                fee_df["security_deposit"], fee_df["extra_people"]],
        hole=0.5,
        marker_colors=["#FC642D","#FF8A65","#FFB89A","#FFD9DF"],
        textinfo="label+percent",
    ))
    fig4.update_layout(title="Average Fee Breakdown",
                       height=340, font=dict(family="DM Sans"),
                       margin=dict(l=0,r=0,t=40,b=0),
                       legend=dict(orientation="v", x=1, y=0.5))
    st.plotly_chart(fig4, use_container_width=True)

# ── Section 3: Price scatter vs review score ──────────────────────────────────
st.markdown('<div class="sh">Price vs Quality & Value</div>', unsafe_allow_html=True)
scatter_df = fdf_priced[
    (fdf_priced["review_score"] > 0) &
    (fdf_priced["price"] < fdf_priced["price"].quantile(0.95))
].copy()

c_e, c_f = st.columns(2)
with c_e:
    fig5 = px.scatter(scatter_df, x="price", y="review_score",
                      color="room_type", size="accommodates",
                      opacity=0.65, size_max=18,
                      color_discrete_sequence=["#FC642D","#00A699","#FC642D55","#484848"],
                      labels={"price":"Price ($/night)","review_score":"Review Score",
                              "room_type":"Room Type"},
                      hover_data=["property_type","bedrooms"])
    fig5.update_layout(title="Price vs Review Score (sized by capacity)",
                       height=380, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"))
    fig5.update_xaxes(showgrid=True, gridcolor="#f5f5f5")
    fig5.update_yaxes(showgrid=True, gridcolor="#f5f5f5")
    st.plotly_chart(fig5, use_container_width=True)

with c_f:
    # Price vs review_value
    fig6 = px.box(fdf_priced[fdf_priced["property_type"].isin(
                      fdf_priced["property_type"].value_counts().head(7).index)],
                  x="property_type", y="price",
                  color="property_type",
                  color_discrete_sequence=px.colors.sequential.OrRd,
                  labels={"property_type":"","price":"Price ($/night)"})
    fig6.update_layout(title="Price Distribution by Top Property Types",
                       showlegend=False, height=380,
                       plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"),
                       xaxis_tickangle=-30)
    fig6.update_yaxes(showgrid=True, gridcolor="#f5f5f5")
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.caption(f"Showing {len(fdf_priced):,} priced listings · Use sidebar filters to narrow results")
