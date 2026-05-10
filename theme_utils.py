import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Airbnb Color Palette (Minimalist 3-Color Rule)
COLORS = {
    "rausch": "#ff385c",        # Action Color
    "white": "#ffffff",         # Background
    "ink_black": "#222222",     # Text
    "ash_gray": "#6a6a6a",      # Secondary Text
    "hairline_gray": "#ebebeb",  # Subtle Dividers
    "soft_cloud": "#f7f7f7"     # Subtle Backgrounds
}

def inject_airbnb_theme():
    """Injects custom CSS to enforce a minimalist Airbnb visual design system."""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Typography & Colors */
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, system-ui, sans-serif !important;
        color: {COLORS["ink_black"]};
        background-color: {COLORS["white"]};
    }}
    
    /* Remove unnecessary padding and borders */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }}

    /* Minimal Metric Cards */
    .metric-card {{
        background-color: {COLORS["white"]};
        border-radius: 8px;
        padding: 16px;
        border: 1px solid {COLORS["hairline_gray"]};
        transition: border-color 0.2s ease;
    }}
    .metric-card:hover {{
        border-color: {COLORS["rausch"]};
    }}
    .metric-value {{
        font-size: 24px;
        font-weight: 700;
        color: {COLORS["ink_black"]};
    }}
    .metric-label {{
        font-size: 13px;
        font-weight: 500;
        color: {COLORS["ash_gray"]};
        margin-top: 2px;
    }}

    /* Sidebar Streamlining */
    [data-testid="stSidebar"] {{
        background-color: {COLORS["white"]};
        border-right: 1px solid {COLORS["hairline_gray"]};
    }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        font-size: 14px;
        color: {COLORS["ash_gray"]};
    }}

    /* Buttons */
    .stButton>button {{
        background-color: {COLORS["rausch"]};
        color: {COLORS["white"]};
        border-radius: 6px;
        font-weight: 600;
        border: none;
    }}

    /* Plotly Charts container (Minimalist) */
    .stPlotlyChart {{
        border: 1px solid {COLORS["hairline_gray"]};
        border-radius: 8px;
        padding: 12px;
        background-color: {COLORS["white"]};
        margin-top: 12px;
    }}
    
    /* Header layout */
    .minimal-header {{
        margin-bottom: 1.5rem;
    }}
    .minimal-title {{
        font-size: 32px;
        font-weight: 700;
        color: {COLORS["ink_black"]};
        margin-bottom: 4px;
    }}
    .minimal-subtitle {{
        font-size: 16px;
        color: {COLORS["ash_gray"]};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def airbnb_header(title, subtitle=None):
    """Renders a minimalist page header."""
    st.markdown(f'<div class="minimal-header">', unsafe_allow_html=True)
    st.markdown(f'## {title}')
    if subtitle:
        st.caption(subtitle)
    st.divider()

def airbnb_section_header(title):
    """Renders a minimalist section header."""
    st.markdown(f"### {title}")

def airbnb_metric_card(label, value):
    """Renders a minimalist metric card."""
    html = f'''
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)

def airbnb_guest_favorite(rating, reviews_count):
    """Renders a minimalist 'Guest Favorite' highlight."""
    st.info(f"⭐ **Guest Favorite** · {rating} rating based on {reviews_count} reviews", icon="🌟")

def apply_plotly_theme(fig):
    """Updates a Plotly figure to use minimalist guidelines."""
    fig.update_layout(
        font=dict(family="'Inter', sans-serif", color=COLORS["ink_black"], size=13),
        title_font=dict(size=18, family="'Inter', sans-serif", color=COLORS["ink_black"]),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, l=10, r=10, b=10),
        hoverlabel=dict(
            bgcolor=COLORS["white"],
            font_size=13,
            bordercolor=COLORS["hairline_gray"]
        )
    )
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linewidth=1,
        linecolor=COLORS["hairline_gray"],
        tickfont=dict(color=COLORS["ash_gray"])
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=COLORS["hairline_gray"],
        zeroline=False,
        tickfont=dict(color=COLORS["ash_gray"])
    )
