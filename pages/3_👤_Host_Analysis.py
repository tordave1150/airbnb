import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Host Analysis · Airbnb", page_icon="👤", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  h1,h2,h3 { font-family: 'Syne', sans-serif !important; }
  .page-header { background: linear-gradient(135deg, #00A699 0%, #007A70 100%);
    color: white; padding: 1.5rem 2rem; border-radius: 14px; margin-bottom: 1.5rem; }
  .page-header h1 { color: white !important; font-size: 2rem; margin: 0; }
  .page-header p  { color: rgba(255,255,255,0.85); margin: 0.3rem 0 0; }
  .kpi { background: white; border-radius: 12px; padding: 1.2rem 1.4rem;
    border: 1px solid #f0f0f0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align:center; }
  .kv  { font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:700; color:#00A699; }
  .kl  { color:#717171; font-size:0.82rem; margin-top:0.2rem; }
  .sh  { font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700;
    color:#222; margin:1.8rem 0 0.8rem; border-left:4px solid #00A699; padding-left:0.7rem; }
  .host-card { background:white; border:1px solid #e8f8f7; border-radius:12px;
    padding:1rem 1.2rem; margin-bottom:0.6rem; border-left:4px solid #00A699; }
  .host-name { font-weight:600; font-size:0.95rem; color:#222; }
  .host-meta { font-size:0.8rem; color:#717171; margin-top:2px; }
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
        "host":1,"price":1,"property_type":1,"room_type":1,"address":1,
        "number_of_reviews":1,"review_scores":1,"amenities":1,
        "bedrooms":1,"accommodates":1,"cancellation_policy":1,
    }))
    rows = []
    for d in docs:
        host = d.get("host",{})
        rv   = d.get("review_scores",{})
        addr = d.get("address",{})
        rows.append({
            "host_id": str(host.get("host_id","")),
            "host_name": host.get("host_name","Unknown"),
            "is_superhost": bool(host.get("host_is_superhost",False)),
            "host_total_listings": int(host.get("host_total_listings_count",1) or 1),
            "host_response_rate": host.get("host_response_rate",""),
            "host_acceptance_rate": host.get("host_acceptance_rate",""),
            "host_identity_verified": bool(host.get("host_identity_verified",False)),
            "host_since": host.get("host_since"),
            "price": float(str(d.get("price",0) or 0)),
            "property_type": d.get("property_type","Other"),
            "room_type": d.get("room_type","Other"),
            "bedrooms": float(str(d.get("bedrooms",0) or 0)),
            "accommodates": int(float(str(d.get("accommodates",0) or 0))),
            "num_reviews": int(float(str(d.get("number_of_reviews",0) or 0))),
            "rating": float(str(rv.get("review_scores_rating",0) or 0)),
            "country": addr.get("country","Unknown"),
            "market": addr.get("market","Unknown"),
            "amenities_count": len(d.get("amenities",[])),
            "cancellation_policy": d.get("cancellation_policy","Unknown"),
        })
    df = pd.DataFrame(rows)
    # Parse response/acceptance rates
    def parse_pct(s):
        try: return float(str(s).replace("%","").strip())
        except: return None
    df["response_rate_pct"] = df["host_response_rate"].apply(parse_pct)
    df["acceptance_rate_pct"] = df["host_acceptance_rate"].apply(parse_pct)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"MongoDB error: {e}")
    st.stop()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 👤 Host Filters")
    countries = ["All"] + sorted(df["country"].dropna().unique().tolist())
    sel_c = st.selectbox("Country", countries)
    sel_super = st.selectbox("Host Type", ["All","Superhost","Regular Host"])
    sel_verified = st.checkbox("Identity Verified Only", False)

fdf = df.copy()
if sel_c != "All":   fdf = fdf[fdf["country"] == sel_c]
if sel_super == "Superhost":     fdf = fdf[fdf["is_superhost"]==True]
if sel_super == "Regular Host":  fdf = fdf[fdf["is_superhost"]==False]
if sel_verified:     fdf = fdf[fdf["host_identity_verified"]==True]

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>👤 Host Analysis</h1>
  <p>Understanding host performance, superhost impact & multi-listing strategies</p>
</div>""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
superhost_pct = fdf["is_superhost"].mean()*100
verified_pct  = fdf["host_identity_verified"].mean()*100
for col,(val,lbl) in zip([c1,c2,c3,c4,c5],[
    (f"{fdf['host_id'].nunique():,}", "Unique Hosts"),
    (f"{superhost_pct:.1f}%", "Superhost Rate"),
    (f"{verified_pct:.1f}%", "Identity Verified"),
    (f"{fdf[fdf['response_rate_pct'].notna()]['response_rate_pct'].mean():.0f}%", "Avg Response Rate"),
    (f"{fdf['host_total_listings'].median():.0f}", "Median Listings / Host"),
]):
    with col:
        st.markdown(f'<div class="kpi"><div class="kv">{val}</div><div class="kl">{lbl}</div></div>',
                    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 1: Superhost vs Regular ──────────────────────────────────────────
st.markdown('<div class="sh">Superhost vs Regular Host Performance</div>', unsafe_allow_html=True)
c_a, c_b = st.columns(2)

with c_a:
    metrics_compare = []
    for label, col in [("Avg Price","price"),("Avg Rating","rating"),
                       ("Avg Reviews","num_reviews"),("Avg Amenities","amenities_count")]:
        sh_val = fdf[fdf["is_superhost"]==True][col].mean()
        rg_val = fdf[fdf["is_superhost"]==False][col].mean()
        metrics_compare.append({"Metric":label,"Superhost":sh_val,"Regular":rg_val})
    mc_df = pd.DataFrame(metrics_compare)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=mc_df["Metric"], y=mc_df["Superhost"],
                         name="Superhost", marker_color="#00A699"))
    fig.add_trace(go.Bar(x=mc_df["Metric"], y=mc_df["Regular"],
                         name="Regular Host", marker_color="#D3D3D3"))
    fig.update_layout(barmode="group", title="Key Metrics: Superhost vs Regular",
                      height=360, plot_bgcolor="white", paper_bgcolor="white",
                      margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"),
                      legend=dict(orientation="h", y=-0.15))
    fig.update_yaxes(showgrid=True, gridcolor="#f5f5f5")
    st.plotly_chart(fig, use_container_width=True)

with c_b:
    sh_counts = fdf["is_superhost"].value_counts().reset_index()
    sh_counts.columns = ["is_superhost","count"]
    sh_counts["label"] = sh_counts["is_superhost"].map({True:"Superhost",False:"Regular Host"})
    fig2 = px.pie(sh_counts, names="label", values="count", hole=0.55,
                  color_discrete_sequence=["#00A699","#E0E0E0"])
    fig2.update_layout(title="Host Type Distribution",
                       height=360, margin=dict(l=0,r=0,t=40,b=0),
                       font=dict(family="DM Sans"),
                       legend=dict(orientation="h", y=-0.05))
    fig2.update_traces(textinfo="percent+label", textposition="inside")
    st.plotly_chart(fig2, use_container_width=True)

# ── Section 2: Multi-listing hosts ───────────────────────────────────────────
st.markdown('<div class="sh">Multi-Listing Host Strategies</div>', unsafe_allow_html=True)
c_c, c_d = st.columns(2)

with c_c:
    bins = [1, 2, 5, 10, 20, 50, 200, 9999]
    labels = ["1","2","3–5","6–10","11–20","21–50","50+"]
    fdf["listing_bucket"] = pd.cut(fdf["host_total_listings"], bins=bins, labels=labels, right=True)
    bucket_ct = fdf["listing_bucket"].value_counts().reset_index()
    bucket_ct.columns = ["bucket","count"]
    bucket_ct = bucket_ct.sort_values("bucket")
    fig3 = px.bar(bucket_ct, x="bucket", y="count", text="count",
                  color="count", color_continuous_scale=["#B2DFDB","#00A699"],
                  labels={"bucket":"Listings per Host","count":"Host Count"})
    fig3.update_traces(textposition="outside")
    fig3.update_layout(title="Distribution of Listings per Host", coloraxis_showscale=False,
                       height=340, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"))
    st.plotly_chart(fig3, use_container_width=True)

with c_d:
    # Avg price by listing count bucket
    price_bucket = (fdf[fdf["price"]>0]
                    .groupby("listing_bucket")["price"]
                    .median().reset_index())
    price_bucket.columns = ["bucket","median_price"]
    fig4 = px.line(price_bucket, x="bucket", y="median_price",
                   markers=True, color_discrete_sequence=["#00A699"],
                   labels={"bucket":"Listings per Host","median_price":"Median Price ($)"})
    fig4.update_traces(marker=dict(size=9), line=dict(width=3))
    fig4.update_layout(title="Price Trend by Host Scale",
                       height=340, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"))
    fig4.update_xaxes(showgrid=True, gridcolor="#f5f5f5")
    fig4.update_yaxes(showgrid=True, gridcolor="#f5f5f5")
    st.plotly_chart(fig4, use_container_width=True)

# ── Section 3: Response rate & cancellation ───────────────────────────────────
st.markdown('<div class="sh">Host Responsiveness & Policies</div>', unsafe_allow_html=True)
c_e, c_f = st.columns(2)

with c_e:
    resp_df = fdf[fdf["response_rate_pct"].notna()].copy()
    resp_bins = [0,50,70,85,95,100]
    resp_labels = ["<50%","50–70%","70–85%","85–95%","95–100%"]
    resp_df["resp_bucket"] = pd.cut(resp_df["response_rate_pct"],
                                     bins=resp_bins, labels=resp_labels, right=True)
    rbc = resp_df["resp_bucket"].value_counts().reset_index()
    rbc.columns = ["bucket","count"]
    rbc = rbc.sort_values("bucket")
    fig5 = px.bar(rbc, x="bucket", y="count", text="count",
                  color="count", color_continuous_scale=["#E0F7F5","#00A699"],
                  labels={"bucket":"Response Rate Range","count":"Host Count"})
    fig5.update_traces(textposition="outside")
    fig5.update_layout(title="Host Response Rate Distribution", coloraxis_showscale=False,
                       height=340, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"))
    st.plotly_chart(fig5, use_container_width=True)

with c_f:
    cancel_ct = fdf["cancellation_policy"].value_counts().reset_index()
    cancel_ct.columns = ["policy","count"]
    fig6 = px.bar(cancel_ct, x="policy", y="count", text="count",
                  color="policy",
                  color_discrete_sequence=["#00A699","#26C6DA","#4DD0E1","#80DEEA","#B2EBF2"],
                  labels={"policy":"","count":"Listings"})
    fig6.update_traces(textposition="outside")
    fig6.update_layout(title="Cancellation Policy Preferences", showlegend=False,
                       height=340, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"))
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.caption(f"Showing {fdf['host_id'].nunique():,} unique hosts across {len(fdf):,} listings · Use sidebar to filter")
