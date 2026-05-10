import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import theme_utils as tu

st.set_page_config(
    page_title="Airbnb Analytics Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Apply Theme ──────────────────────────────────────────────────────────────
tu.inject_airbnb_theme()

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
        coords = addr.get("location", {}).get("coordinates", [])
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
            "num_reviews": int(float(str(d.get("number_of_reviews", 0) or 0))),
            "number_of_reviews": int(float(str(d.get("number_of_reviews", 0) or 0))),
            "rating": float(str(rv.get("review_scores_rating", 0) or 0)),
            "review_score": float(str(rv.get("review_scores_rating", 0) or 0)),
            "review_cleanliness": float(str(rv.get("review_scores_cleanliness", 0) or 0)),
            "review_location": float(str(rv.get("review_scores_location", 0) or 0)),
            "review_value": float(str(rv.get("review_scores_value", 0) or 0)),
            "review_communication": float(str(rv.get("review_scores_communication", 0) or 0)),
            "review_accuracy": float(str(rv.get("review_scores_accuracy", 0) or 0)),
            "review_checkin": float(str(rv.get("review_scores_checkin", 0) or 0)),
            "accuracy": float(str(rv.get("review_scores_accuracy", 0) or 0)),
            "cleanliness": float(str(rv.get("review_scores_cleanliness", 0) or 0)),
            "checkin": float(str(rv.get("review_scores_checkin", 0) or 0)),
            "communication": float(str(rv.get("review_scores_communication", 0) or 0)),
            "location": float(str(rv.get("review_scores_location", 0) or 0)),
            "value": float(str(rv.get("review_scores_value", 0) or 0)),
            "country": addr.get("country", "Unknown"),
            "country_code": addr.get("country_code", ""),
            "market": addr.get("market", "Unknown"),
            "suburb": addr.get("suburb", ""),
            "lat": coords[1] if len(coords) > 1 else None,
            "lon": coords[0] if len(coords) > 0 else None,
            "amenities_count": len(d.get("amenities", [])),
            "amenities": d.get("amenities", []),
            "min_nights": int(d.get("minimum_nights", 1) or 1),
            "max_nights": int(d.get("maximum_nights", 365) or 365),
            "cancellation_policy": d.get("cancellation_policy", "Unknown"),
            "host_id": str(host.get("host_id", "")),
            "host_name": host.get("host_name", "Unknown"),
            "is_superhost": bool(host.get("host_is_superhost", False)),
            "host_is_superhost": bool(host.get("host_is_superhost", False)),
            "host_total_listings": int(host.get("host_total_listings_count", 1) or 1),
            "host_listings_count": int(host.get("host_total_listings_count", 1) or 1),
            "host_response_rate": host.get("host_response_rate", ""),
            "host_response_time": host.get("host_response_time", ""),
            "host_acceptance_rate": host.get("host_acceptance_rate", ""),
            "host_identity_verified": bool(host.get("host_identity_verified", False)),
            "host_since": host.get("host_since"),
            "availability_30": int(float(str(avail.get("availability_30", 0) or 0))),
            "availability_365": int(float(str(avail.get("availability_365", 0) or 0))),
            "first_review": d.get("first_review"),
            "last_review": d.get("last_review"),
        })
    
    # Parse rates for Host Analysis
    df = pd.DataFrame(rows)
    def parse_pct(s):
        try: return float(str(s).replace("%", "").strip())
        except: return None
    df["response_rate_pct"] = df["host_response_rate"].apply(parse_pct)
    df["acceptance_rate_pct"] = df["host_acceptance_rate"].apply(parse_pct)
    
    return df

# ── Load data ────────────────────────────────────────────────────────────────
try:
    df = load_listings()
    st.session_state.df = df
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
tu.airbnb_header("🏠 Airbnb Analytics Dashboard", "Global listings intelligence · Sample Airbnb Dataset from MongoDB")

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
        tu.airbnb_metric_card(lbl, val)

st.markdown("<br>", unsafe_allow_html=True)

# ── Guest Favorite Highlight ────────────────────────────────────────────────
avg_rating = fdf["review_score"][fdf["review_score"]>0].mean() / 20 # scale to 5
if pd.isna(avg_rating): avg_rating = 4.85
tu.airbnb_guest_favorite(f"{avg_rating:.2f}", f"{len(fdf[fdf['review_score']>0]):,}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Listings by country + room type ───────────────────────────────────
tu.airbnb_section_header("Listings Distribution")
col_a, col_b = st.columns([3, 2])

with col_a:
    country_counts = fdf["country"].value_counts().reset_index()
    country_counts.columns = ["country", "count"]
    fig = px.bar(country_counts, x="count", y="country", orientation="h",
                 color="count", color_continuous_scale=["#FFD9DF","#FF385C"],
                 labels={"count": "Listings", "country": ""})
    fig.update_layout(title="Listings by Country", coloraxis_showscale=False, height=360)
    tu.apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    rt = fdf["room_type"].value_counts().reset_index()
    rt.columns = ["room_type", "count"]
    fig2 = px.pie(rt, names="room_type", values="count",
                  color_discrete_sequence=["#ff385c","#e00b41","#92174d","#460479","#dddddd"],
                  hole=0.55)
    fig2.update_layout(title="Room Type Breakdown", height=360)
    tu.apply_plotly_theme(fig2)
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Price distribution + review score distribution ────────────────────
tu.airbnb_section_header("Price & Review Insights")
col_c, col_d = st.columns(2)

with col_c:
    price_data = fdf[fdf["price"] > 0]["price"]
    fig3 = px.histogram(price_data, nbins=50, color_discrete_sequence=["#FF385C"],
                        labels={"value":"Price ($/night)", "count":"Listings"})
    fig3.update_layout(title="Price Distribution", height=320, showlegend=False)
    tu.apply_plotly_theme(fig3)
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    rv_data = fdf[fdf["review_score"] > 0]["review_score"]
    fig4 = px.histogram(rv_data, nbins=30, color_discrete_sequence=["#92174d"],
                        labels={"value":"Review Score", "count":"Listings"})
    fig4.update_layout(title="Review Score Distribution", height=320, showlegend=False)
    tu.apply_plotly_theme(fig4)
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Avg price by property type ────────────────────────────────────────
tu.airbnb_section_header("Property Type Performance")
col_e, col_f = st.columns([2, 3])

with col_e:
    prop_stats = (fdf.groupby("property_type")
                    .agg(listings=("id","count"), avg_price=("price","median"),
                         avg_score=("review_score","mean"))
                    .reset_index()
                    .sort_values("listings", ascending=False)
                    .head(10))
    fig5 = px.bar(prop_stats, x="property_type", y="avg_price",
                  color="avg_price", color_continuous_scale=["#f7f7f7","#460479"],
                  labels={"property_type":"","avg_price":"Median Price ($)"})
    fig5.update_layout(title="Median Price by Property Type", coloraxis_showscale=False, height=340, xaxis_tickangle=-35)
    tu.apply_plotly_theme(fig5)
    st.plotly_chart(fig5, use_container_width=True)

with col_f:
    cancel = fdf["cancellation_policy"].value_counts().reset_index()
    cancel.columns = ["policy","count"]
    avg_price_cancel = fdf.groupby("cancellation_policy")["price"].median().reset_index()
    avg_price_cancel.columns = ["policy","median_price"]
    cancel = cancel.merge(avg_price_cancel, on="policy")

    fig6 = make_subplots(specs=[[{"secondary_y": True}]])
    fig6.add_trace(go.Bar(x=cancel["policy"], y=cancel["count"],
                          name="Listings", marker_color="#ff385c", opacity=0.8))
    fig6.add_trace(go.Scatter(x=cancel["policy"], y=cancel["median_price"],
                              name="Median Price", mode="lines+markers",
                              marker=dict(color="#460479", size=8),
                              line=dict(color="#460479", width=2)),
                   secondary_y=True)
    fig6.update_layout(title="Cancellation Policy: Listings & Price", height=340, legend=dict(orientation="h", y=-0.15))
    tu.apply_plotly_theme(fig6)
    st.plotly_chart(fig6, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(f"Showing **{len(fdf):,}** of **{len(df):,}** listings · "
           "Data: MongoDB sample_airbnb · Use sidebar filters to explore")
