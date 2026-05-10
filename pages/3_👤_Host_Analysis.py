import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import theme_utils as tu

st.set_page_config(page_title="Host Analysis · Airbnb", page_icon="👤", layout="wide")

# ── Apply Theme ──────────────────────────────────────────────────────────────
tu.inject_airbnb_theme()

# ── Data ──────────────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.switch_page("app.py")

df = st.session_state.df

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
tu.airbnb_header("👤 Host Analysis", "Understanding host performance, superhost impact & multi-listing strategies")

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
        tu.airbnb_metric_card(lbl, val)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 1: Superhost vs Regular ──────────────────────────────────────────
tu.airbnb_section_header("Superhost vs Regular Host Performance")
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
    fig.update_layout(barmode="group", title="Key Metrics: Superhost vs Regular", height=360, legend=dict(orientation="h", y=-0.15))
    tu.apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

with c_b:
    sh_counts = fdf["is_superhost"].value_counts().reset_index()
    sh_counts.columns = ["is_superhost","count"]
    sh_counts["label"] = sh_counts["is_superhost"].map({True:"Superhost",False:"Regular Host"})
    fig2 = px.pie(sh_counts, names="label", values="count", hole=0.55,
                  color_discrete_sequence=["#ff385c","#dddddd"])
    fig2.update_layout(title="Host Type Distribution", height=360, legend=dict(orientation="h", y=-0.05))
    tu.apply_plotly_theme(fig2)
    st.plotly_chart(fig2, use_container_width=True)

# ── Section 2: Multi-listing hosts ───────────────────────────────────────────
tu.airbnb_section_header("Multi-Listing Host Strategies")
c_c, c_d = st.columns(2)

with c_c:
    bins = [1, 2, 5, 10, 20, 50, 200, 9999]
    labels = ["1","2","3–5","6–10","11–20","21–50","50+"]
    fdf["listing_bucket"] = pd.cut(fdf["host_total_listings"], bins=bins, labels=labels, right=True)
    bucket_ct = fdf["listing_bucket"].value_counts().reset_index()
    bucket_ct.columns = ["bucket","count"]
    bucket_ct = bucket_ct.sort_values("bucket")
    fig3 = px.bar(bucket_ct, x="bucket", y="count", text="count",
                  color="count", color_continuous_scale=["#f7f7f7","#ff385c"],
                  labels={"bucket":"Listings per Host","count":"Host Count"})
    fig3.update_traces(textposition="outside")
    fig3.update_layout(title="Distribution of Listings per Host", coloraxis_showscale=False, height=340)
    tu.apply_plotly_theme(fig3)
    st.plotly_chart(fig3, use_container_width=True)

with c_d:
    # Avg price by listing count bucket
    price_bucket = (fdf[fdf["price"]>0]
                    .groupby("listing_bucket")["price"]
                    .median().reset_index())
    price_bucket.columns = ["bucket","median_price"]
    fig4 = px.line(price_bucket, x="bucket", y="median_price",
                   markers=True, color_discrete_sequence=["#ff385c"],
                   labels={"bucket":"Listings per Host","median_price":"Median Price ($)"})
    fig4.update_traces(marker=dict(size=9), line=dict(width=3))
    fig4.update_layout(title="Price Trend by Host Scale", height=340)
    tu.apply_plotly_theme(fig4)
    st.plotly_chart(fig4, use_container_width=True)

# ── Section 3: Response rate & cancellation ───────────────────────────────────
tu.airbnb_section_header("Host Responsiveness & Policies")
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
                  color="count", color_continuous_scale=["#f7f7f7","#ff385c"],
                  labels={"bucket":"Response Rate Range","count":"Host Count"})
    fig5.update_traces(textposition="outside")
    fig5.update_layout(title="Host Response Rate Distribution", coloraxis_showscale=False, height=340)
    tu.apply_plotly_theme(fig5)
    st.plotly_chart(fig5, use_container_width=True)

with c_f:
    cancel_ct = fdf["cancellation_policy"].value_counts().reset_index()
    cancel_ct.columns = ["policy","count"]
    fig6 = px.bar(cancel_ct, x="policy", y="count", text="count",
                  color="policy",
                  color_discrete_sequence=["#ff385c","#e00b41","#92174d","#460479","#dddddd"],
                  labels={"policy":"","count":"Listings"})
    fig6.update_traces(textposition="outside")
    fig6.update_layout(title="Cancellation Policy Preferences", showlegend=False, height=340)
    tu.apply_plotly_theme(fig6)
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.caption(f"Showing {fdf['host_id'].nunique():,} unique hosts across {len(fdf):,} listings · Use sidebar to filter")
