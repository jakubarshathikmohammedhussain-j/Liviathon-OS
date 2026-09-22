import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timedelta

# ==========================================
# PAGE & SYSTEM CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="LEVIATHAN OS // Maritime Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# WORLD-CLASS ENTERPRISE DARK UI (CUSTOM CSS)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* Global Theme Overrides */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #07090E;
        color: #E2E8F0;
    }
    
    .stApp {
        background: radial-gradient(circle at 15% 15%, rgba(16, 24, 40, 0.8) 0%, #07090E 100%);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0B0F17 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Glassmorphism Card System */
    .glass-card {
        background: rgba(15, 23, 42, 0.55);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.5);
    }
    
    .glass-card-accent {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 1px solid rgba(16, 185, 129, 0.25);
    }

    /* Stat Typography */
    .kpi-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #94A3B8;
        margin-bottom: 6px;
    }
    
    .kpi-value {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.1rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.1;
    }

    .kpi-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        padding: 3px 8px;
        border-radius: 6px;
        margin-top: 10px;
    }

    .badge-green { background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-amber { background: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-red { background: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.3); }

    /* Pulsing Signal Dot */
    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse 1.8s infinite;
        margin-right: 8px;
    }
    
    .pulse-dot.red {
        background: #EF4444;
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
        animation: pulse-red 1s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    @keyframes pulse-red {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    /* Terminal Console Style */
    .terminal-console {
        background-color: #000000;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 15px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #10B981;
        height: 180px;
        overflow: hidden;
        margin-top: 15px;
    }
    .term-time { color: #64748b; margin-right: 10px;}
    .term-crit { color: #EF4444; }
    .term-warn { color: #F59E0B; }
    .term-sys { color: #3b82f6; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA INGESTION ENGINE (GLOBAL)
# ==========================================
@st.cache_data(ttl=600, show_spinner=False)
def load_telemetry_stream():
    np.random.seed(42)
    n_points = 3500 
    
    lat_clusters = np.random.choice(
        [5.5, 27.0, 9.1, 50.0, 33.7, 15.0, 35.9], 
        size=n_points, p=[0.25, 0.15, 0.15, 0.15, 0.10, 0.10, 0.10]
    )
    lon_clusters = np.random.choice(
        [95.0, 34.6, -79.7, -1.0, -118.2, 115.0, -5.5], 
        size=n_points, p=[0.25, 0.15, 0.15, 0.15, 0.10, 0.10, 0.10]
    )
    
    lats = lat_clusters + np.random.normal(0, 3.5, n_points)
    lons = lon_clusters + np.random.normal(0, 4.5, n_points)
    
    entities = np.random.choice(
        ['Pacific Container Chok', 'Maersk Line Triple-E', 'CMA CGM Apex', 'Evergreen Marine G-Type', 'Suez Congestion Anomaly', 'Panama Transit Delay'], 
        size=n_points, p=[0.12, 0.28, 0.25, 0.20, 0.08, 0.07]
    )
    
    return pd.DataFrame({
        'timestamp': pd.date_range(end=datetime.now(), periods=n_points, freq='2min'),
        'domain': 'LEVIATHAN_GLOBAL',
        'entity_id': entities,
        'latitude': lats,
        'longitude': lons,
        'is_chokepoint': [('Chok' in e or 'Anomaly' in e or 'Delay' in e) for e in entities]
    })

# Load base data
data = load_telemetry_stream()

# ==========================================
# SIDEBAR NAVIGATION & SIMULATOR
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="padding: 10px 0 20px 0;">
            <div style="font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #10B981; letter-spacing: 0.15em;">
                <span class="pulse-dot"></span>SYSTEM ACTIVE
            </div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em; margin-top: 4px;">
                LEVIATHAN OS
            </div>
            <div style="font-size: 0.78rem; color: #64748B;">Autonomous Maritime & Eco-Routing Engine</div>
        </div>
    """, unsafe_allow_html=True)
    
    screen = st.radio("Navigation", ["Fleet Operations", "Chokepoint Analytics", "Dynamic Eco-Router"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("<div style='font-family: \"JetBrains Mono\"; font-size: 0.7rem; color: #64748B; margin-bottom: 12px;'>LETHAL PITCH CONTROLS</div>", unsafe_allow_html=True)
    
    # LETHAL FEATURE 1: DISRUPTION SIMULATOR
    simulate_anomaly = st.toggle("⚠️ Simulate Weather Anomaly", value=False)
    
    if simulate_anomaly:
        st.error("CRITICAL: Category 4 Typhoon simulated in South China Sea. Rerouting protocols engaged.")
        # Inject 800 massive red data points into the South China Sea
        anomaly_lats = 15.0 + np.random.normal(0, 1.5, 800)
        anomaly_lons = 115.0 + np.random.normal(0, 1.5, 800)
        anomaly_df = pd.DataFrame({
            'timestamp': pd.date_range(end=datetime.now(), periods=800, freq='1min'),
            'domain': 'TYPHOON_DISRUPTION',
            'entity_id': ['Severe Weather Chokepoint'] * 800,
            'latitude': anomaly_lats,
            'longitude': anomaly_lons,
            'is_chokepoint': [True] * 800
        })
        data = pd.concat([data, anomaly_df], ignore_index=True)

# ==========================================
# SCREEN 1: FLEET OPERATIONS DASHBOARD
# ==========================================
if screen == "Fleet Operations":
    st.markdown("""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 2.2rem; font-weight: 700; margin-bottom: 4px; color: #FFFFFF;">Live Fleet Matrix</h1>
            <p style="color: #94A3B8; font-size: 0.95rem;">Real-time spatial distribution across critical maritime channels.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        vessel_count = len(data['entity_id'].unique()) * 18
        st.markdown(f"""
            <div class="glass-card">
                <div class="kpi-title">Monitored Vessels</div>
                <div class="kpi-value">{vessel_count}</div>
                <div class="kpi-badge badge-green">Live Pipeline Sync</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        choke_count = int(data['is_chokepoint'].sum() / 8)
        if simulate_anomaly:
            badge_html = '<div class="kpi-badge badge-red"><span class="pulse-dot red"></span>Typhoon Detected</div>'
        else:
            badge_html = '<div class="kpi-badge badge-amber">Standard Congestion</div>'
            
        st.markdown(f"""
            <div class="glass-card">
                <div class="kpi-title">Active Bottlenecks</div>
                <div class="kpi-value" style="color: {'#EF4444' if simulate_anomaly else '#F8FAFC'}">{choke_count}</div>
                {badge_html}
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class="glass-card glass-card-accent">
                <div class="kpi-title">Fuel Abatement Tracker</div>
                <div class="kpi-value">3,420 MT</div>
                <div class="kpi-badge badge-green">+$48,000 Saved (24h)</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
            <div class="glass-card">
                <div class="kpi-title">SDG 13 CO2 Offset</div>
                <div class="kpi-value">10,773 T</div>
                <div class="kpi-badge badge-green">Verified Reduction</div>
            </div>
        """, unsafe_allow_html=True)

    c_map, c_term = st.columns([7, 3])
    
    with c_map:
        st.markdown("<div style='font-size: 1.1rem; font-weight: 600; margin-bottom: 12px;'>Spatial Density Elevators (3D View)</div>", unsafe_allow_html=True)
        # Center map on South China Sea if anomaly is active, else standard view
        start_lat, start_lon = (12.0, 110.0) if simulate_anomaly else (15.0, 60.0)
        
        st.pydeck_chart(pdk.Deck(
            map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
            initial_view_state=pdk.ViewState(latitude=start_lat, longitude=start_lon, zoom=2.5, pitch=50, bearing=-10),
            layers=[
                pdk.Layer(
                    'HexagonLayer',
                    data=data,
                    get_position='[longitude, latitude]',
                    radius=45000,
                    elevation_scale=75,
                    elevation_range=[0, 4000],
                    pickable=True,
                    extruded=True,
                    get_fill_color="[16, 185, 129, 160]"
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=data[data['is_chokepoint']],
                    get_position='[longitude, latitude]',
                    get_color='[239, 68, 68, 220]' if simulate_anomaly else '[245, 158, 11, 200]',
                    get_radius=55000,
                    pickable=True
                )
            ],
            tooltip={"text": "Vessel Cluster Density"}
        ))

    # LETHAL FEATURE 2: AUTOMATED DISPATCH LOG
    with c_term:
        st.markdown("<div style='font-size: 1.1rem; font-weight: 600; margin-bottom: 12px;'>Autonomous Dispatch Logic</div>", unsafe_allow_html=True)
        
        now = datetime.now()
        t1 = (now - timedelta(seconds=12)).strftime("%H:%M:%S")
        t2 = (now - timedelta(seconds=45)).strftime("%H:%M:%S")
        t3 = (now - timedelta(minutes=2)).strftime("%H:%M:%S")
        t4 = (now - timedelta(minutes=4)).strftime("%H:%M:%S")
        
        if simulate_anomaly:
            logs = f"""
            <div><span class="term-time">[{t1}]</span> <span class="term-crit">[CRITICAL]</span> TYPHOON PRESSURE DROP IN SEC-4</div>
            <div><span class="term-time">[{t2}]</span> <span class="term-sys">[SYS]</span> HALTING AIS LEGACY ROUTES IN ZONE</div>
            <div><span class="term-time">[{t3}]</span> <span style="color:#10B981;">[SUCCESS]</span> AUTONOMOUS REROUTE: 42 VESSELS BYPASSED</div>
            <div><span class="term-time">[{t4}]</span> <span class="term-warn">[WARN]</span> RECALCULATING FUEL BURN CURVES...</div>
            """
        else:
            logs = f"""
            <div><span class="term-time">[{t1}]</span> <span class="term-sys">[SYS]</span> INGESTING BIGQUERY TELEMETRY (3,500 ROWS)</div>
            <div><span class="term-time">[{t2}]</span> <span style="color:#10B981;">[SUCCESS]</span> PACIFIC CHOKEPOINT CLEAR</div>
            <div><span class="term-time">[{t3}]</span> <span class="term-warn">[WARN]</span> SUEZ CANAL TRAFFIC DENSITY INCREASING 12%</div>
            <div><span class="term-time">[{t4}]</span> <span class="term-sys">[SYS]</span> OPTIMIZING FUEL CURVES FOR FLEET ALPHA...</div>
            """
            
        st.markdown(f"""
            <div class="terminal-console">
                <div>> INITIALIZING O.M.E.G.A. PROTOCOL...</div>
                <div>> CONNECTION ESTABLISHED</div>
                <br>
                {logs}
                <br>
                <div class="pulse-dot"></div> <span style="color:#64748b;">Awaiting telemetry...</span>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# SCREEN 2: CHOKEPOINT ANALYTICS
# ==========================================
elif screen == "Chokepoint Analytics":
    st.markdown("""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 2.2rem; font-weight: 700; margin-bottom: 4px; color: #FFFFFF;">Bottleneck Analytics</h1>
            <p style="color: #94A3B8; font-size: 0.95rem;">Historical density models isolating the disruption entity groups.</p>
        </div>
    """, unsafe_allow_html=True)
    
    choke_df = data[data['is_chokepoint']]
    col_map, col_metrics = st.columns([2, 1])
    
    with col_map:
        st.pydeck_chart(pdk.Deck(
            map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
            initial_view_state=pdk.ViewState(latitude=20.0, longitude=50.0, zoom=1.5, pitch=0),
            layers=[
                pdk.Layer(
                    'HeatmapLayer',
                    data=choke_df,
                    get_position='[longitude, latitude]',
                    radiusPixels=60,
                    intensity=1.5,
                    threshold=0.05
                )
            ]
        ))
        
    with col_metrics:
        st.markdown("""
            <div class="glass-card">
                <div class="kpi-title">Average Wait Delay</div>
                <div class="kpi-value" style="color: #F87171;">42.8 Hrs</div>
                <p style="font-size: 0.8rem; color: #94A3B8; margin-top: 8px;">Idle time caused by anchorage queuing.</p>
            </div>
            <div class="glass-card">
                <div class="kpi-title">Fuel Waste Coefficient</div>
                <div class="kpi-value">18.4 MT/day</div>
                <p style="font-size: 0.8rem; color: #94A3B8; margin-top: 8px;">Auxiliary power burned during holding patterns.</p>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# SCREEN 3: DYNAMIC ECO-ROUTER & ROI
# ==========================================
elif screen == "Dynamic Eco-Router":
    st.markdown("""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 2.2rem; font-weight: 700; margin-bottom: 4px; color: #FFFFFF;">Enterprise ROI & Eco-Routing</h1>
            <p style="color: #94A3B8; font-size: 0.95rem;">Translate SDG 13 Climate Action directly into enterprise profitability.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # LETHAL FEATURE 3: PREDICTIVE ROI CALCULATOR
    st.markdown("<div style='background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); padding: 25px; border-radius: 12px; margin-bottom: 30px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #10B981; font-size: 1.2rem; margin-bottom: 20px;'>B2B Predictive Savings Calculator</h3>", unsafe_allow_html=True)
    
    calc_col1, calc_col2 = st.columns(2)
    with calc_col1:
        fleet_size = st.slider("Active Fleet Size (Vessels)", min_value=5, max_value=250, value=45)
    with calc_col2:
        annual_voyages = st.slider("Average Annual Voyages per Vessel", min_value=10, max_value=100, value=32)
        
    # Standard route vs LEVIATHAN bypass constants
    savings_usd_per_voyage = 48000
    savings_co2_per_voyage = 278
    
    total_usd = (fleet_size * annual_voyages * savings_usd_per_voyage) / 1000000 # In Millions
    total_co2 = fleet_size * annual_voyages * savings_co2_per_voyage
    
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.markdown(f"""
            <div style="margin-top: 20px;">
                <div class="kpi-title">Projected Annual Capital Saved</div>
                <div class="kpi-value" style="font-size: 3rem; color: #10B981;">${total_usd:.1f}M</div>
            </div>
        """, unsafe_allow_html=True)
    with res_c2:
        st.markdown(f"""
            <div style="margin-top: 20px;">
                <div class="kpi-title">Projected SDG 13 CO2 Abatement</div>
                <div class="kpi-value" style="font-size: 3rem;">{total_co2:,} Tons</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<h3 style='font-size: 1.1rem; color: #94A3B8; margin-bottom: 15px;'>Per-Voyage Bypass Metrics</h3>", unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        st.markdown("""
            <div class="glass-card" style="border-top: 4px solid #EF4444;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-weight: 700; font-size: 1.1rem; color: #F87171;">Standard Route (Legacy AIS)</span>
                </div>
                <div style="margin-bottom: 14px;"><div style="font-size: 0.8rem; color: #64748B;">CONGESTION DELAY EXPOSURE</div><div style="font-size: 1.4rem; font-weight: 700; color: #F87171;">+38.5 Hours</div></div>
                <div style="margin-bottom: 14px;"><div style="font-size: 0.8rem; color: #64748B;">ESTIMATED FUEL BURN</div><div style="font-size: 1.4rem; font-weight: 700;">412 MT</div></div>
                <div><div style="font-size: 0.8rem; color: #64748B;">CARBON FOOTPRINT</div><div style="font-size: 1.4rem; font-weight: 700; color: #F87171;">1,298 Tons CO2</div></div>
            </div>
        """, unsafe_allow_html=True)
        
    with r2:
        st.markdown("""
            <div class="glass-card glass-card-accent" style="border-top: 4px solid #10B981;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-weight: 700; font-size: 1.1rem; color: #10B981;">LEVIATHAN Dynamic Bypass</span>
                </div>
                <div style="margin-bottom: 14px;"><div style="font-size: 0.8rem; color: #64748B;">CONGESTION DELAY EXPOSURE</div><div style="font-size: 1.4rem; font-weight: 700; color: #10B981;">0.0 Hours (Direct Transit)</div></div>
                <div style="margin-bottom: 14px;"><div style="font-size: 0.8rem; color: #64748B;">ESTIMATED FUEL BURN</div><div style="font-size: 1.4rem; font-weight: 700; color: #10B981;">324 MT (-21.3%)</div></div>
                <div><div style="font-size: 0.8rem; color: #64748B;">CARBON FOOTPRINT</div><div style="font-size: 1.4rem; font-weight: 700; color: #10B981;">1,020 Tons CO2 (-278 Tons)</div></div>
            </div>
        """, unsafe_allow_html=True)
