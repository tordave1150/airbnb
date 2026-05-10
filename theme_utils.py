import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Airbnb Color Palette
COLORS = {
    "rausch": "#ff385c",
    "rausch_deep": "#e00b41",
    "plus_magenta": "#92174d",
    "luxe_purple": "#460479",
    "info_blue": "#428bff",
    "white": "#ffffff",
    "soft_cloud": "#f7f7f7",
    "hairline_gray": "#dddddd",
    "ink_black": "#222222",
    "charcoal": "#3f3f3f",
    "ash_gray": "#6a6a6a",
    "mute_gray": "#929292",
    "stone_gray": "#c1c1c1",
    "error_red": "#c13515"
}

def inject_airbnb_theme():
    """Injects custom CSS to enforce the Airbnb visual design system."""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Typography & Colors */
    html, body, [class*="css"] {{
        font-family: 'Airbnb Cereal VF', 'Circular', 'Inter', -apple-system, system-ui, sans-serif !important;
        color: {COLORS["ink_black"]};
        background-color: {COLORS["white"]};
        font-weight: 500;
    }}
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS["ink_black"]};
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }}
    
    /* Buttons */
    .stButton>button {{
        background-color: {COLORS["rausch"]};
        color: {COLORS["white"]};
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        border: none;
        box-shadow: none;
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .stButton>button:hover {{
        background-color: {COLORS["rausch_deep"]};
        transform: scale(0.96);
    }}
    .stButton>button:active {{
        box-shadow: 0 0 0 2px {COLORS["white"]}, 0 0 0 4px {COLORS["ink_black"]};
    }}
    
    /* Markdown / Text */
    p {{
        font-weight: 500;
        line-height: 1.43;
    }}
    
    /* Secondary text elements */
    .st-emotion-cache-1104e7c, .st-emotion-cache-1629p8f h1, .st-emotion-cache-1629p8f h2, .st-emotion-cache-1629p8f h3 {{
        color: {COLORS["ink_black"]};
    }}
    
    /* Metrics / Cards */
    .metric-card {{
        background-color: {COLORS["white"]};
        border-radius: 14px;
        padding: 24px;
        border: 1px solid {COLORS["hairline_gray"]};
        box-shadow: rgba(0, 0, 0, 0.02) 0 0 0 1px, rgba(0, 0, 0, 0.04) 0 2px 6px 0, rgba(0, 0, 0, 0.1) 0 4px 8px 0;
        transition: box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1), transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: left;
        margin-bottom: 16px;
    }}
    .metric-card:hover {{
        box-shadow: rgba(0, 0, 0, 0.04) 0 0 0 1px, rgba(0, 0, 0, 0.08) 0 4px 12px 0, rgba(0, 0, 0, 0.12) 0 8px 16px 0;
        transform: translateY(-2px);
    }}
    .metric-value {{
        font-size: 28px;
        font-weight: 700;
        color: {COLORS["ink_black"]};
        letter-spacing: -0.02em;
        line-height: 1.2;
    }}
    .metric-label {{
        font-size: 14px;
        font-weight: 500;
        color: {COLORS["ash_gray"]};
        margin-top: 4px;
        text-transform: none;
    }}

    /* Guest Favorite Lockup */
    .guest-favorite-container {{
        text-align: center;
        padding: 48px 0;
        background: {COLORS["white"]};
    }}
    .guest-favorite-rating {{
        font-size: 56px;
        font-weight: 700;
        color: {COLORS["ink_black"]};
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 24px;
    }}
    .laurel-wreath {{
        width: 48px;
        height: 48px;
        opacity: 0.8;
    }}
    .guest-favorite-label {{
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 8px;
        color: {COLORS["ink_black"]};
    }}
    .guest-favorite-sub {{
        font-size: 14px;
        color: {COLORS["ash_gray"]};
        font-weight: 500;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLORS["soft_cloud"]};
        border-right: 1px solid {COLORS["hairline_gray"]};
    }}
    
    /* Selectboxes and Inputs */
    .stSelectbox>div>div, .stNumberInput>div>div, .stTextInput>div>div {{
        border-radius: 8px;
        border: 1px solid {COLORS["hairline_gray"]};
        background-color: {COLORS["white"]};
    }}
    .stSelectbox>div>div:focus-within, .stTextInput>div>div:focus-within {{
        border-color: {COLORS["ink_black"]} !important;
        box-shadow: 0 0 0 1px {COLORS["ink_black"]} !important;
    }}
    
    /* Plotly Charts container */
    .stPlotlyChart {{
        border: 1px solid {COLORS["hairline_gray"]};
        border-radius: 14px;
        padding: 16px;
        background-color: {COLORS["white"]};
        box-shadow: rgba(0, 0, 0, 0.02) 0 0 0 1px, rgba(0, 0, 0, 0.04) 0 2px 6px 0, rgba(0, 0, 0, 0.1) 0 4px 8px 0;
        margin-top: 16px;
    }}
    
    /* Header layout */
    .airbnb-header-container {{
        margin-bottom: 48px;
        padding-bottom: 24px;
        border-bottom: 1px solid {COLORS["hairline_gray"]};
    }}
    .airbnb-title {{
        font-size: 48px;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 8px;
        color: {COLORS["ink_black"]};
    }}
    .airbnb-subtitle {{
        font-size: 18px;
        color: {COLORS["ash_gray"]};
        font-weight: 500;
    }}
    
    /* Section dividers */
    .airbnb-section-title {{
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: {COLORS["ink_black"]};
        margin-top: 48px;
        margin-bottom: 24px;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def airbnb_header(title, subtitle=None):
    """Renders a pristine, margin-adjusted page header."""
    html = f'''
    <div class="airbnb-header-container">
        <div class="airbnb-title">{title}</div>
        {"<div class='airbnb-subtitle'>" + subtitle + "</div>" if subtitle else ""}
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)

def airbnb_section_header(title):
    """Renders a section header that aligns with Airbnb's typography."""
    st.markdown(f'<div class="airbnb-section-title">{title}</div>', unsafe_allow_html=True)

def airbnb_metric_card(label, value):
    """Renders a custom HTML metric card with Airbnb styling and 3-layer shadow."""
    html = f'''
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)

def airbnb_guest_favorite(rating, reviews_count):
    """Renders the signature 'Guest Favorite' laurel wreath lockup."""
    html = f'''
    <div class="guest-favorite-container">
        <div class="guest-favorite-rating">
            <span style="transform: scaleX(-1);">🌿</span>
            {rating}
            <span>🌿</span>
        </div>
        <div class="guest-favorite-label">Guest Favorite</div>
        <div class="guest-favorite-sub">One of the most loved homes on Airbnb, based on {reviews_count} reviews</div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)

def apply_plotly_theme(fig):
    """Updates a Plotly figure to use Airbnb's aesthetic guidelines."""
    
    fig.update_layout(
        font=dict(
            family="'Airbnb Cereal VF', 'Circular', 'Inter', sans-serif",
            color=COLORS["ink_black"],
            size=14
        ),
        title_font=dict(
            size=21,
            family="'Airbnb Cereal VF', 'Circular', 'Inter', sans-serif",
            color=COLORS["ink_black"]
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, l=10, r=10, b=30),
        hoverlabel=dict(
            bgcolor=COLORS["white"],
            font_size=14,
            font_family="'Airbnb Cereal VF', 'Circular', 'Inter', sans-serif",
            bordercolor=COLORS["hairline_gray"]
        )
    )
    
    # Update axes to be minimalist
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
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
        showline=False,
        tickfont=dict(color=COLORS["ash_gray"])
    )
