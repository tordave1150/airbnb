import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import theme_utils as tu

st.set_page_config(page_title="Amenities & Features · Airbnb", page_icon="🏡", layout="wide")

# ── Apply Theme ──────────────────────────────────────────────────────────────
tu.inject_airbnb_theme()

# ── Data ──────────────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.switch_page("app.py")

df = st.session_state.df

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
tu.airbnb_header("🏡 Amenities & Property Features", "What amenities are most common, which drive higher prices & better reviews")

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
        tu.airbnb_metric_card(lbl, val)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section 1: Top amenities ──────────────────────────────────────────────────
tu.airbnb_section_header("Most Common Amenities")
c_a, c_b = st.columns([3, 2])

with c_a:
    top20 = amenity_df.head(20)
    fig = px.bar(top20.sort_values("count"), x="count", y="amenity",
                 orientation="h", text="count",
                 color="count",
                 color_continuous_scale=["#f7f7f7","#ff385c"],
                 labels={"count":"# Listings","amenity":""})
    fig.update_traces(textposition="outside")
    fig.update_layout(title="Top 20 Most Common Amenities", coloraxis_showscale=False, height=500)
    tu.apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

with c_b:
    st.markdown("**Top amenities at a glance:**")
    tags_html = "".join(
        f'<span class="amenity-tag">{row["amenity"]} ({row["count"]})</span>'
        for _, row in amenity_df.head(30).iterrows()
    )
    st.markdown(tags_html, unsafe_allow_html=True)

# ── Section 2: Amenity count vs price & rating ─────────────────────────────────
tu.airbnb_section_header("Amenities vs Price & Quality")
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
                  color_continuous_scale=["#f7f7f7","#ff385c"],
                  labels={"amenity_bucket":"# Amenities","median_price":"Median Price ($)"})
    fig3.update_traces(texttemplate='$%{text:.0f}', textposition='outside')
    fig3.update_layout(title="More Amenities → Higher Price?", coloraxis_showscale=False, height=360)
    tu.apply_plotly_theme(fig3)
    st.plotly_chart(fig3, use_container_width=True)

with c_d:
    fdf_r = fdf[fdf["rating"]>0].copy()
    fdf_r["amenity_bucket"] = pd.cut(fdf_r["amenities_count"],
                                      bins=bins, labels=labels, right=True)
    ar = (fdf_r.groupby("amenity_bucket")
               .agg(avg_rating=("rating","mean"), count=("rating","count"))
               .reset_index())
    fig4 = px.line(ar, x="amenity_bucket", y="avg_rating",
                   markers=True, color_discrete_sequence=["#ff385c"],
                   labels={"amenity_bucket":"# Amenities","avg_rating":"Avg Rating Score"},
                   text="avg_rating")
    fig4.update_traces(marker=dict(size=9), line=dict(width=3),
                       texttemplate="%{text:.0f}", textposition="top center")
    fig4.update_layout(title="More Amenities → Better Ratings?", height=360)
    tu.apply_plotly_theme(fig4)
    st.plotly_chart(fig4, use_container_width=True)

# ── Section 3: Bed & property specs ──────────────────────────────────────────
tu.airbnb_section_header("Property Specifications")
c_e, c_f = st.columns(2)

with c_e:
    bed_type_ct = fdf["bed_type"].value_counts().reset_index()
    bed_type_ct.columns = ["bed_type","count"]
    fig5 = px.pie(bed_type_ct, names="bed_type", values="count",
                  color_discrete_sequence=["#ff385c","#e00b41","#92174d","#460479","#dddddd"],
                  hole=0.5)
    fig5.update_layout(title="Bed Type Distribution", height=340)
    tu.apply_plotly_theme(fig5)
    st.plotly_chart(fig5, use_container_width=True)

with c_f:
    # Capacity distribution: accommodates
    acc_df = fdf[(fdf["accommodates"]>0)&(fdf["accommodates"]<=16)]["accommodates"].value_counts().reset_index()
    acc_df.columns = ["accommodates","count"]
    acc_df = acc_df.sort_values("accommodates")
    fig6 = px.bar(acc_df, x="accommodates", y="count", text="count",
                  color="accommodates",
                  color_continuous_scale=["#f7f7f7","#ff385c"],
                  labels={"accommodates":"Guests Accommodated","count":"Listings"})
    fig6.update_traces(textposition="outside")
    fig6.update_layout(title="Accommodation Capacity Distribution", coloraxis_showscale=False, height=340, xaxis=dict(tickmode="linear", dtick=1))
    tu.apply_plotly_theme(fig6)
    st.plotly_chart(fig6, use_container_width=True)

# ── Section 4: Key amenity premium analysis ────────────────────────────────────
tu.airbnb_section_header("Premium Amenity Impact on Price")

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
              color_continuous_scale=["#f7f7f7","#ff385c","#e00b41"],
              labels={"Price Premium ($)":"Price Premium vs Without ($/night)", "Amenity":""},
              hover_data={"With ($)":True, "Without ($)":True, "Coverage (%)":True})
fig7.update_traces(texttemplate='$%{text:.0f}', textposition='outside')
fig7.update_layout(title="Price Premium for Listings WITH Each Amenity", coloraxis_showscale=False, height=420)
tu.apply_plotly_theme(fig7)
fig7.add_vline(x=0, line_dash="dash", line_color="#999", line_width=1)
st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")
st.caption(f"Analyzed {len(fdf):,} listings · {len(amenity_counter):,} unique amenities found · Use sidebar to filter")
