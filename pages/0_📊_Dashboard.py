import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Airbnb Analytics Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  h1, h2, h3 { font-family: 'Syne', sans-serif !important; }
  .main-header {
    background: linear-gradient(135deg, #FF385C 0%, #BD1E59 100%);
    color: white; padding: 2rem 2.5rem; border-radius: 16px;
    margin-bottom: 2rem;
  }
  .main-header h1 { color: white !important; font-size: 2.4rem; margin: 0 0 0.3rem; }
  .main-header p  { color: rgba(255,255,255,0.85); margin: 0; font-size: 1.05rem; }
  .metric-card {
    background: white; border-radius: 14px; padding: 1.4rem 1.6rem;
    border: 1px solid #f0f0f0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); text-align: center;
  }
  .metric-value { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 700; color: #FF385C; }
  .metric-label { color: #717171; font-size: 0.85rem; margin-top: 0.2rem; }
  .section-header { font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 700;
    color: #222; margin: 2rem 0 1rem; border-left: 4px solid #FF385C; padding-left: 0.75rem; }
  [data-testid="stSidebar"] { background: #fafafa; border-right: 1px solid #efefef; }
  .stSelectbox label, .stMultiSelect label { font-weight: 500; color: #444; }
</style>
""", unsafe_allow_html=True)

# ── MongoDB connection ───────────────────────────────────────────────────────
@st.cache_resource
def get_mongo_client():
    return pymongo.MongoClient(st.secrets["mongo"]["uri"])

@st.cache_data(ttl=300)
def load_listings():
    client = get_mongo_client()
    db = client["sample_airbnb"]
    col = db["listingsAndReviews"]
    docs = list(col.find({}, {
        "name": 1, "property_type": 1, "room_type": 1, "bed_type": 1,
        "price": 1, "cleaning_fee": 1, "security_deposit": 1, "extra_people": 1,
        "accommodates": 1, "bedrooms": 1, "beds": 1, "bathrooms": 1,
        "number_of_reviews": 1, "review_scores": 1, "host": 1,
        "address": 1, "amenities": 1, "minimum_nights": 1, "maximum_nights": 1,
        "cancellation_policy": 1, "availability": 1, "first_review": 1, "last_review": 1,
    }))
    rows = []
    for d in docs:
        addr = d.get("address", {})
        rv   = d.get("review_scores", {})
        host = d.get("host", {})
        avail = d.get("availability", {})
        rows.append({
            "id": str(d.get("_id", "")),
            "name": d.get("name", ""),
            "property_type": d.get("property_type", "Other"),
            "room_type": d.get("room_type", "Other"),
            "bed_type": d.get("bed_type", "Other"),
            "price": float(str(d.get("price", 0) or 0)),
            "cleaning_fee": float(str(d.get("cleaning_fee", 0) or 0)),
            "security_deposit": float(str(d.get("security_deposit", 0) or 0)),
            "extra_people": float(str(d.get("extra_people", 0) or 0)),
            "accommodates": int(float(str(d.get("accommodates", 0) or 0))),
            "bedrooms": float(str(d.get("bedrooms", 0) or 0)),
            "beds": float(str(d.get("beds", 0) or 0)),
            "bathrooms": float(str(d.get("bathrooms", 0) or 0)),
            "number_of_reviews": int(float(str(d.get("number_of_reviews", 0) or 0))),
            "review_score": float(str(rv.get("review_scores_rating", 0) or 0)),
            "review_cleanliness": float(str(rv.get("review_scores_cleanliness", 0) or 0)),
            "review_location": float(str(rv.get("review_scores_location", 0) or 0)),
            "review_value": float(str(rv.get("review_scores_value", 0) or 0)),
            "review_communication": float(str(rv.get("review_scores_communication", 0) or 0)),
            "review_accuracy": float(str(rv.get("review_scores_accuracy", 0) or 0)),
            "review_checkin": float(str(rv.get("review_scores_checkin", 0) or 0)),
            "country": addr.get("country", "Unknown"),
            "country_code": addr.get("country_code", ""),
            "market": addr.get("market", "Unknown"),
            "suburb": addr.get("suburb", ""),
            "amenities_count": len(d.get("amenities", [])),
            "amenities": d.get("amenities", []),
            "min_nights": int(d.get("minimum_nights", 1) or 1),
            "max_nights": int(d.get("maximum_nights", 365) or 365),
            "cancellation_policy": d.get("cancellation_policy", "Unknown"),
            "host_is_superhost": host.get("host_is_superhost", False),
            "host_total_listings": int(host.get("host_total_listings_count", 1) or 1),
            "availability_30": int(avail.get("availability_30", 0) or 0),
            "availability_365": int(avail.get("availability_365", 0) or 0),
            "first_review": d.get("first_review"),
            "last_review": d.get("last_review"),
        })
    return pd.DataFrame(rows)

# ── Load data ────────────────────────────────────────────────────────────────
try:
    df = load_listings()
    data_ok = True
except Exception as e:
    st.error(f"⚠️ Could not connect to MongoDB: {e}")
    st.info("Make sure the connection string and network access are configured.")
    data_ok = False
    st.stop()

# ── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Airbnb_Logo_B%C3%A9lo.svg/320px-Airbnb_Logo_B%C3%A9lo.svg.png", width=140)
    st.markdown("---")
    st.markdown("### 🔍 Global Filters")

    countries = ["All"] + sorted(df["country"].dropna().unique().tolist())
    sel_country = st.selectbox("Country", countries)

    property_types = ["All"] + sorted(df["property_type"].dropna().unique().tolist())
    sel_property = st.selectbox("Property Type", property_types)

    room_types = ["All"] + sorted(df["room_type"].dropna().unique().tolist())
    sel_room = st.selectbox("Room Type", room_types)

    price_min, price_max = int(df["price"].min()), int(df["price"].quantile(0.98))
    sel_price = st.slider("Price Range ($/night)", price_min, price_max, (price_min, price_max))

    st.markdown("---")
    st.caption("📊 Sample Airbnb Dataset · MongoDB Atlas")

# ── Apply filters ────────────────────────────────────────────────────────────
fdf = df.copy()
if sel_country != "All":   fdf = fdf[fdf["country"] == sel_country]
if sel_property != "All":  fdf = fdf[fdf["property_type"] == sel_property]
if sel_room != "All":      fdf = fdf[fdf["room_type"] == sel_room]
fdf = fdf[(fdf["price"] >= sel_price[0]) & (fdf["price"] <= sel_price[1])]

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🏠 Airbnb Analytics Dashboard</h1>
  <p>Global listings intelligence · Sample Airbnb Dataset from MongoDB</p>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (f"{len(fdf):,}", "Total Listings"),
    (f"${fdf['price'].median():.0f}", "Median Price / Night"),
    (f"{fdf['review_score'][fdf['review_score']>0].mean():.1f}/100", "Avg Review Score"),
    (f"{fdf['country'].nunique()}", "Countries"),
    (f"{fdf['host_is_superhost'].sum():,}", "Superhosts"),
]
for col, (val, lbl) in zip([k1,k2,k3,k4,k5], kpis):
    with col:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value">{val}</div>
          <div class="metric-label">{lbl}</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Listings by country + room type ───────────────────────────────────
st.markdown('<div class="section-header">Listings Distribution</div>', unsafe_allow_html=True)
col_a, col_b = st.columns([3, 2])

with col_a:
    country_counts = fdf["country"].value_counts().reset_index()
    country_counts.columns = ["country", "count"]
    fig = px.bar(country_counts, x="count", y="country", orientation="h",
                 color="count", color_continuous_scale=["#FFD9DF","#FF385C"],
                 labels={"count": "Listings", "country": ""})
    fig.update_layout(title="Listings by Country", coloraxis_showscale=False,
                      margin=dict(l=0,r=0,t=40,b=0), height=360,
                      plot_bgcolor="white", paper_bgcolor="white",
                      font=dict(family="DM Sans"))
    fig.update_xaxes(showgrid=True, gridcolor="#f5f5f5")
    fig.update_yaxes(showgrid=False)
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    rt = fdf["room_type"].value_counts().reset_index()
    rt.columns = ["room_type", "count"]
    fig2 = px.pie(rt, names="room_type", values="count",
                  color_discrete_sequence=["#FF385C","#FF7096","#FFB3C1","#FFD9DF","#FFEAEE"],
                  hole=0.55)
    fig2.update_layout(title="Room Type Breakdown", margin=dict(l=0,r=0,t=40,b=0),
                       height=360, font=dict(family="DM Sans"),
                       legend=dict(orientation="v", x=1.0, y=0.5))
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Price distribution + review score distribution ────────────────────
st.markdown('<div class="section-header">Price & Review Insights</div>', unsafe_allow_html=True)
col_c, col_d = st.columns(2)

with col_c:
    price_data = fdf[fdf["price"] > 0]["price"]
    fig3 = px.histogram(price_data, nbins=50, color_discrete_sequence=["#FF385C"],
                        labels={"value":"Price ($/night)", "count":"Listings"})
    fig3.update_layout(title="Price Distribution", margin=dict(l=0,r=0,t=40,b=0),
                       height=320, plot_bgcolor="white", paper_bgcolor="white",
                       font=dict(family="DM Sans"), showlegend=False)
    fig3.update_xaxes(showgrid=True, gridcolor="#f5f5f5")
    fig3.update_yaxes(showgrid=True, gridcolor="#f5f5f5")
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    rv_data = fdf[fdf["review_score"] > 0]["review_score"]
    fig4 = px.histogram(rv_data, nbins=30, color_discrete_sequence=["#00A699"],
                        labels={"value":"Review Score", "count":"Listings"})
    fig4.update_layout(title="Review Score Distribution", margin=dict(l=0,r=0,t=40,b=0),
                       height=320, plot_bgcolor="white", paper_bgcolor="white",
                       font=dict(family="DM Sans"), showlegend=False)
    fig4.update_xaxes(showgrid=True, gridcolor="#f5f5f5")
    fig4.update_yaxes(showgrid=True, gridcolor="#f5f5f5")
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Avg price by property type ────────────────────────────────────────
st.markdown('<div class="section-header">Property Type Performance</div>', unsafe_allow_html=True)
col_e, col_f = st.columns([2, 3])

with col_e:
    prop_stats = (fdf.groupby("property_type")
                    .agg(listings=("id","count"), avg_price=("price","median"),
                         avg_score=("review_score","mean"))
                    .reset_index()
                    .sort_values("listings", ascending=False)
                    .head(10))
    fig5 = px.bar(prop_stats, x="property_type", y="avg_price",
                  color="avg_price", color_continuous_scale=["#FFD9DF","#BD1E59"],
                  labels={"property_type":"","avg_price":"Median Price ($)"})
    fig5.update_layout(title="Median Price by Property Type", coloraxis_showscale=False,
                       margin=dict(l=0,r=0,t=40,b=0), height=340,
                       plot_bgcolor="white", paper_bgcolor="white",
                       xaxis_tickangle=-35, font=dict(family="DM Sans"))
    st.plotly_chart(fig5, use_container_width=True)

with col_f:
    cancel = fdf["cancellation_policy"].value_counts().reset_index()
    cancel.columns = ["policy","count"]
    avg_price_cancel = fdf.groupby("cancellation_policy")["price"].median().reset_index()
    avg_price_cancel.columns = ["policy","median_price"]
    cancel = cancel.merge(avg_price_cancel, on="policy")

    fig6 = make_subplots(specs=[[{"secondary_y": True}]])
    fig6.add_trace(go.Bar(x=cancel["policy"], y=cancel["count"],
                          name="Listings", marker_color="#FF385C", opacity=0.8))
    fig6.add_trace(go.Scatter(x=cancel["policy"], y=cancel["median_price"],
                              name="Median Price", mode="lines+markers",
                              marker=dict(color="#00A699", size=8),
                              line=dict(color="#00A699", width=2)),
                   secondary_y=True)
    fig6.update_layout(title="Cancellation Policy: Listings & Price",
                       margin=dict(l=0,r=0,t=40,b=0), height=340,
                       plot_bgcolor="white", paper_bgcolor="white",
                       font=dict(family="DM Sans"),
                       legend=dict(orientation="h", y=-0.15))
    fig6.update_yaxes(title_text="Count", secondary_y=False, showgrid=True, gridcolor="#f5f5f5")
    fig6.update_yaxes(title_text="Median Price ($)", secondary_y=True, showgrid=False)
    st.plotly_chart(fig6, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(f"Showing **{len(fdf):,}** of **{len(df):,}** listings · "
           "Data: MongoDB sample_airbnb · Use sidebar filters to explore")
