import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

st.set_page_config(page_title="Amenities & Features · Airbnb", page_icon="🏡", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  h1,h2,h3 { font-family: 'Syne', sans-serif !important; }
  .page-header { background: linear-gradient(135deg, #8E44AD 0%, #5B2C6F 100%);
    color: white; padding: 1.5rem 2rem; border-radius: 14px; margin-bottom: 1.5rem; }
  .page-header h1 { color: white !important; font-size: 2rem; margin: 0; }
  .page-header p  { color: rgba(255,255,255,0.85); margin: 0.3rem 0 0; }
  .kpi { background: white; border-radius: 12px; padding: 1.2rem 1.4rem;
    border: 1px solid #f0f0f0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align:center; }
  .kv  { font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:700; color:#8E44AD; }
  .kl  { color:#717171; font-size:0.82rem; margin-top:0.2rem; }
  .sh  { font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700;
    color:#222; margin:1.8rem 0 0.8rem; border-left:4px solid #8E44AD; padding-left:0.7rem; }
  .amenity-tag { display:inline-block; background:#F5EEF8; color:#6C3483;
    border-radius:20px; padding:4px 12px; margin:4px; font-size:0.8rem; font-weight:500; }
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
        "amenities":1,"price":1,"property_type":1,"room_type":1,
        "address":1,"review_scores":1,"host":1,
        "bedrooms":1,"beds":1,"bathrooms":1,"accommodates":1,
        "number_of_reviews":1,"bed_type":1,
    }))
    rows = []
    for d in docs:
        rv   = d.get("review_scores",{})
        addr = d.get("address",{})
        rows.append({
            "amenities": [a.strip() for a in d.get("amenities",[]) if a.strip()],
            "amenities_count": len(d.get("amenities",[])),
            "price": float(str(d.get("price",0) or 0)),
            "property_type": d.get("property_type","Other"),
            "room_type": d.get("room_type","Other"),
            "bed_type": d.get("bed_type","Other"),
            "bedrooms": float(str(d.get("bedrooms",0) or 0)),
            "beds": float(str(d.get("beds",0) or 0)),
            "bathrooms": float(str(d.get("bathrooms",0) or 0)),
            "accommodates": int(float(str(d.get("accommodates",0) or 0))),
            "num_reviews": int(float(str(d.get("number_of_reviews",0) or 0))),
            "rating": float(str(rv.get("review_scores_rating",0) or 0)),
            "country": addr.get("country","Unknown"),
            "is_superhost": bool(d.get("host",{}).get("host_is_superhost",False)),
        })
    return pd.DataFrame(rows)

try:
    df = load_data()
except Exception as e:
    st.error(f"MongoDB error: {e}")
    st.stop()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏡 Feature Filters")
    countries = ["All"] + sorted(df["country"].dropna().unique().tolist())
    sel_c = st.selectbox("Country", countries)
    sel_pt = st.selectbox("Property Type",
                          ["All"]+sorted(df["property_type"].dropna().unique().tolist()))
    sel_rt = st.selectbox("Room Type",
                          ["All"]+sorted(df["room_type"].dropna().unique().tolist()))

fdf = df.copy()
if sel_c  != "All": fdf = fdf[fdf["country"] == sel_c]
if sel_pt != "All": fdf = fdf[fdf["property_type"] == sel_pt]
if sel_rt != "All": fdf = fdf[fdf["room_type"] == sel_rt]

# ── Build amenity frequency ───────────────────────────────────────────────────
all_amenities = [a for lst in fdf["amenities"] for a in lst]
amenity_counter = Counter(all_amenities)
amenity_df = pd.DataFrame(amenity_counter.most_common(50),
                           columns=["amenity","count"])

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>🏡 Amenities & Property Features</h1>
  <p>What amenities are most common, which drive higher prices & better reviews</p>
</div>""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
for col,(val,lbl) in zip([c1,c2,c3,c4,c5],[
    (f"{len(amenity_counter):,}", "Unique Amenities"),
    (f"{fdf['amenities_count'].mean():.1f}", "Avg Amenities / Listing"),
    (f"{fdf['amenities_count'].max()}", "Max Amenities Found"),
    (f"{fdf['beds'].mean():.1f}", "Avg Beds"),
    (f"{fdf['bathrooms'].mean():.1f}", "Avg Bathrooms"),
]):
    with col:
        st.markdown(f'<div class="kpi"><div class="kv">{val}</div><div class="kl">{lbl}</div></div>',
                    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 1: Top amenities ──────────────────────────────────────────────────
st.markdown('<div class="sh">Most Common Amenities</div>', unsafe_allow_html=True)
c_a, c_b = st.columns([3, 2])

with c_a:
    top20 = amenity_df.head(20)
    fig = px.bar(top20.sort_values("count"), x="count", y="amenity",
                 orientation="h", text="count",
                 color="count",
                 color_continuous_scale=["#E8DAEF","#8E44AD"],
                 labels={"count":"# Listings","amenity":""})
    fig.update_traces(textposition="outside")
    fig.update_layout(title="Top 20 Most Common Amenities", coloraxis_showscale=False,
                      height=500, plot_bgcolor="white", paper_bgcolor="white",
                      margin=dict(l=0,r=40,t=40,b=0), font=dict(family="DM Sans"))
    st.plotly_chart(fig, use_container_width=True)

with c_b:
    st.markdown("**Top amenities at a glance:**")
    tags_html = "".join(
        f'<span class="amenity-tag">{row["amenity"]} ({row["count"]})</span>'
        for _, row in amenity_df.head(30).iterrows()
    )
    st.markdown(tags_html, unsafe_allow_html=True)

# ── Section 2: Amenity count vs price & rating ─────────────────────────────────
st.markdown('<div class="sh">Amenities vs Price & Quality</div>', unsafe_allow_html=True)
c_c, c_d = st.columns(2)

with c_c:
    bins = [0,5,10,15,20,25,30,40,100]
    labels = ["0–5","6–10","11–15","16–20","21–25","26–30","31–40","40+"]
    fdf_p = fdf[fdf["price"]>0].copy()
    fdf_p["amenity_bucket"] = pd.cut(fdf_p["amenities_count"],
                                      bins=bins, labels=labels, right=True)
    ap = (fdf_p.groupby("amenity_bucket")
                .agg(median_price=("price","median"), count=("price","count"))
                .reset_index())
    fig3 = px.bar(ap, x="amenity_bucket", y="median_price", text="median_price",
                  color="median_price",
                  color_continuous_scale=["#E8DAEF","#8E44AD"],
                  labels={"amenity_bucket":"# Amenities","median_price":"Median Price ($)"})
    fig3.update_traces(texttemplate='$%{text:.0f}', textposition='outside')
    fig3.update_layout(title="More Amenities → Higher Price?", coloraxis_showscale=False,
                       height=360, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"))
    fig3.update_yaxes(showgrid=True, gridcolor="#f5f5f5")
    st.plotly_chart(fig3, use_container_width=True)

with c_d:
    fdf_r = fdf[fdf["rating"]>0].copy()
    fdf_r["amenity_bucket"] = pd.cut(fdf_r["amenities_count"],
                                      bins=bins, labels=labels, right=True)
    ar = (fdf_r.groupby("amenity_bucket")
               .agg(avg_rating=("rating","mean"), count=("rating","count"))
               .reset_index())
    fig4 = px.line(ar, x="amenity_bucket", y="avg_rating",
                   markers=True, color_discrete_sequence=["#8E44AD"],
                   labels={"amenity_bucket":"# Amenities","avg_rating":"Avg Rating Score"},
                   text="avg_rating")
    fig4.update_traces(marker=dict(size=9), line=dict(width=3),
                       texttemplate="%{text:.0f}", textposition="top center")
    fig4.update_layout(title="More Amenities → Better Ratings?",
                       height=360, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"))
    fig4.update_xaxes(showgrid=True, gridcolor="#f5f5f5")
    fig4.update_yaxes(showgrid=True, gridcolor="#f5f5f5", range=[0,100])
    st.plotly_chart(fig4, use_container_width=True)

# ── Section 3: Bed & property specs ──────────────────────────────────────────
st.markdown('<div class="sh">Property Specifications</div>', unsafe_allow_html=True)
c_e, c_f = st.columns(2)

with c_e:
    bed_type_ct = fdf["bed_type"].value_counts().reset_index()
    bed_type_ct.columns = ["bed_type","count"]
    fig5 = px.pie(bed_type_ct, names="bed_type", values="count",
                  color_discrete_sequence=["#8E44AD","#A569BD","#C39BD3","#D7BDE2","#E8DAEF"],
                  hole=0.5)
    fig5.update_layout(title="Bed Type Distribution",
                       height=340, font=dict(family="DM Sans"),
                       margin=dict(l=0,r=0,t=40,b=0),
                       legend=dict(orientation="v", x=1, y=0.5))
    fig5.update_traces(textinfo="percent+label", textposition="inside")
    st.plotly_chart(fig5, use_container_width=True)

with c_f:
    # Capacity distribution: accommodates
    acc_df = fdf[(fdf["accommodates"]>0)&(fdf["accommodates"]<=16)]["accommodates"].value_counts().reset_index()
    acc_df.columns = ["accommodates","count"]
    acc_df = acc_df.sort_values("accommodates")
    fig6 = px.bar(acc_df, x="accommodates", y="count", text="count",
                  color="accommodates",
                  color_continuous_scale=["#E8DAEF","#5B2C6F"],
                  labels={"accommodates":"Guests Accommodated","count":"Listings"})
    fig6.update_traces(textposition="outside")
    fig6.update_layout(title="Accommodation Capacity Distribution",
                       coloraxis_showscale=False, height=340,
                       plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=40,b=0), font=dict(family="DM Sans"),
                       xaxis=dict(tickmode="linear", dtick=1))
    fig6.update_yaxes(showgrid=True, gridcolor="#f5f5f5")
    st.plotly_chart(fig6, use_container_width=True)

# ── Section 4: Key amenity premium analysis ────────────────────────────────────
st.markdown('<div class="sh">Premium Amenity Impact on Price</div>', unsafe_allow_html=True)

premium_amenities = [
    "Wifi","Pool","Kitchen","Air conditioning","Washer","Dryer",
    "Free parking on premises","Gym","Elevator","Hot tub",
    "Pets allowed","Smoking allowed","TV","Doorman",
]
impact_rows = []
baseline = fdf[fdf["price"]>0]["price"].median()
for amenity in premium_amenities:
    with_am = fdf[fdf["amenities"].apply(lambda x: amenity in x) & (fdf["price"]>0)]["price"].median()
    without_am = fdf[fdf["amenities"].apply(lambda x: amenity not in x) & (fdf["price"]>0)]["price"].median()
    count_with = fdf[fdf["amenities"].apply(lambda x: amenity in x)].shape[0]
    if count_with >= 10:
        impact_rows.append({
            "Amenity": amenity,
            "With ($)": round(with_am,0),
            "Without ($)": round(without_am,0),
            "Price Premium ($)": round(with_am - without_am, 0),
            "Coverage (%)": round(count_with/len(fdf)*100, 1),
        })

impact_df = pd.DataFrame(impact_rows).sort_values("Price Premium ($)", ascending=True)

fig7 = px.bar(impact_df, x="Price Premium ($)", y="Amenity",
              orientation="h", text="Price Premium ($)",
              color="Price Premium ($)",
              color_continuous_scale=["#FADBD8","#E8DAEF","#8E44AD"],
              labels={"Price Premium ($)":"Price Premium vs Without ($/night)", "Amenity":""},
              hover_data={"With ($)":True, "Without ($)":True, "Coverage (%)":True})
fig7.update_traces(texttemplate='$%{text:.0f}', textposition='outside')
fig7.update_layout(title="Price Premium for Listings WITH Each Amenity",
                   coloraxis_showscale=False, height=420,
                   plot_bgcolor="white", paper_bgcolor="white",
                   margin=dict(l=0,r=50,t=40,b=0), font=dict(family="DM Sans"))
fig7.add_vline(x=0, line_dash="dash", line_color="#999", line_width=1)
st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")
st.caption(f"Analyzed {len(fdf):,} listings · {len(amenity_counter):,} unique amenities found · Use sidebar to filter")
