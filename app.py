import streamlit as st

st.set_page_config(
    page_title="Airbnb Analytics",
    page_icon="🏠",
    layout="wide",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  h1, h2, h3 { font-family: 'Syne', sans-serif !important; }
  .main-header {
    background: linear-gradient(135deg, #FF385C 0%, #BD1E59 100%);
    color: white; padding: 3rem 2.5rem; border-radius: 16px;
    margin-bottom: 2rem;
    text-align: center;
  }
  .main-header h1 { color: white !important; font-size: 3rem; margin: 0 0 0.5rem; }
  .main-header p  { color: rgba(255,255,255,0.9); margin: 0; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
  <h1>🏠 Airbnb Analytics</h1>
  <p>Welcome to the Global Airbnb Listings Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

st.info("👈 Please select a dashboard from the sidebar to begin exploring the data.")

st.markdown("""
### Available Modules
* **📊 Dashboard:** High-level metrics and global listings distribution.
* **💰 Price Analysis:** Deep dive into pricing patterns, fees, and value drivers.
* **⭐ Reviews & Ratings:** Analysis of guest satisfaction and review trends.
* **👤 Host Analysis:** Insights into host performance and superhost impact.
* **🌍 Geographic Analysis:** Spatial distribution of listings and regional trends.
* **🏡 Amenities & Features:** Impact of property features on price and ratings.
""")
