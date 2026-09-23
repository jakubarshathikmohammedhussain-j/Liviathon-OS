import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# ==========================================
# PAGE & SYSTEM CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="LEVIATHAN OS // Maritime Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "alarm_played" not in st.session_state:
    st.session_state.alarm_played = False

# Configure Gemini safely
GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# ==========================================
# WORLD-CLASS ENTERPRISE DARK UI (CUSTOM CSS)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #07090E;
        color: #E2E8F0;
    }
    
    .stApp {
        background: radial-gradient(circle at 15% 15%, rgba(16, 24, 40, 0.8) 0%, #07090E 100%);
    }

    section[data-testid="stSidebar"] {
        background-color: #0B0F17 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

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

    .ai-justification-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(15, 23, 42, 0.7) 100%);
        border-left: 4px solid #3B82F6;
        padding: 18px;
        border-radius: 0 12px 12px 0;
        margin-top: 20px;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #93C5FD;
    }

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

    .terminal-console {
        background-color: #030712;
        border: 1px solid #1F2937;
        border-radius: 8px;
        padding: 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #10B981;
        height: 180px;
        overflow-y: auto;
        margin-top: 15px;
    }
    .term-time { color: #64748B; margin-right: 8px; }
    .term-crit { color: #EF4444; font-weight: 700; }
    .term-sys { color: #3B82F6; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA INGESTION ENGINE (GLOBAL & DYNAMIC)
# ==========================================
@st.cache_data(ttl=600, show_spinner=False)
def load_telemetry_stream():
    np.random.seed(42)
    n_points = 3500 
    
    routes = [
        (13.0, 80.0), # Bay of Bengal / Chennai Hub
        (25.0, 55.0), # Arabian Sea / Persian Gulf
        (5.5, 95.0),  # Malacca Strait
        (27.0, 34.6), # Suez Canal / Red Sea
        (50.0, -1.0), # English Channel
        (9.1, -79.7)  # Panama Canal
    ]
    
    selected_routes = [routes[np.random.choice(len(routes), p=[0.30, 0.20, 0.20, 0.15, 0.10, 0.05])] for _ in range(n_points)]
    lat_clusters = np.array([r[0] for r in selected_routes])
    lon_clusters = np.array([r[1] for r in selected_routes])
    
    lats = lat_clusters + np.random.normal(0, 1.8, n_points)
    lons = lon_clusters + np.random.normal(0, 2.2, n_points)
    
    entities = np.random.choice(
        ['Bay of Bengal Hub Anomaly', 'Malacca Container Chok', 'Arabian Sea Delay', 'Maersk Line Triple-E', 'CMA CGM Apex'], 
        size=n_points, 
        p=[0.15, 0.15, 0.10, 0.35, 0.25]
    )
    
    return pd.DataFrame({
        'timestamp': pd.date_range(end=datetime.now(), periods=n_points, freq='2min'),
        'domain': 'LEVIATHAN_GLOBAL',
        'entity_id': entities,
        'latitude': lats,
        'longitude': lons,
        'is_chokepoint': [('Anomaly' in e or 'Chok' in e or 'Delay' in e) for e in entities]
    })

data = load_telemetry_stream()

# ==========================================
# SIDEBAR NAVIGATION & MULTI-SCENARIO SIMULATOR
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
            <div style="font-size: 0.78rem; color: #64748B;">O.M.E.G.A. Autonomous Engine</div>
        </div>
    """, unsafe_allow_html=True)
    
    screen = st.radio("Navigation", ["Fleet Operations", "Chokepoint Analytics", "Dynamic Eco-Router"], label_visibility="collapsed")
    st.markdown("---")
    
    st.markdown("<div style='font-family: \"JetBrains Mono\"; font-size: 0.7rem; color: #64748B; margin-bottom: 12px;'>LETHAL PITCH CONTROLS</div>", unsafe_allow_html=True)
    
    scenario = st.selectbox(
        "Select Live Simulation Scenario",
        [
            "🟢 Nominal Operations (Global Clear)",
            "⚠️ Typhoon Disruption (Bay of Bengal)",
            "🏴‍☠️ Pirate Interception (Malacca Strait)",
            "🛑 Suez Canal Blockage"
        ]
    )
    
    if "Typhoon" in scenario:
        st.error("CRITICAL: Category 4 Typhoon active in Bay of Bengal.")
        sim_lats = 13.0 + np.random.normal(0, 1.2, 900)
        sim_lons = 82.0 + np.random.normal(0, 1.2, 900)
        sim_df = pd.DataFrame({
            'timestamp': pd.date_range(end=datetime.now(), periods=900, freq='1min'),
            'domain': 'TYPHOON_DISRUPTION',
            'entity_id': ['Severe Weather Chokepoint'] * 900,
            'latitude': sim_lats,
            'longitude': sim_lons,
            'is_chokepoint': [True] * 900
        })
        data = pd.concat([data, sim_df], ignore_index=True)
    elif "Pirate" in scenario:
        st.warning("SECURITY ALERT: Unauthorized Vessel Interception in Malacca.")
        sim_lats = 5.5 + np.random.normal(0, 0.8, 700)
        sim_lons = 95.0 + np.random.normal(0, 0.8, 700)
        sim_df = pd.DataFrame({
            'timestamp': pd.date_range(end=datetime.now(), periods=700, freq='1min'),
            'domain': 'SECURITY_INTERCEPTION',
            'entity_id': ['Pirate Interception Zone'] * 700,
            'latitude': sim_lats,
            'longitude': sim_lons,
            'is_chokepoint': [True] * 700
        })
        data = pd.concat([data, sim_df], ignore_index=True)
    elif "Suez" in scenario:
        st.error("BLOCKAGE: Grounded Container Megaship at Suez Approach.")
        sim_lats = 27.0 + np.random.normal(0, 0.6, 800)
        sim_lons = 34.6 + np.random.normal(0, 0.6, 800)
        sim_df = pd.DataFrame({
            'timestamp': pd.date_range(end=datetime.now(), periods=800, freq='1min'),
            'domain': 'SUEZ_BLOCKAGE',
            'entity_id': ['Suez Megaship Grounding'] * 800,
            'latitude': sim_lats,
            'longitude': sim_lons,
            'is_chokepoint': [True] * 800
        })
        data = pd.concat([data, sim_df], ignore_index=True)

    st.markdown("---")
    st.markdown("<div style='font-family: \"JetBrains Mono\"; font-size: 0.7rem; color: #3B82F6; margin-bottom: 12px;'>O.M.E.G.A. COPILOT</div>", unsafe_allow_html=True)
    
    chat_container = st.container(height=250)
    for msg in st.session_state.chat_history:
        with chat_container.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Ask O.M.E.G.A..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)
            
        with chat_container.chat_message("assistant"):
            response = ""
            if GEMINI_AVAILABLE:
                sys_prompt = f"You are O.M.E.G.A., the AI core of LEVIATHAN OS. Current simulation status: {scenario}. Answer concisely in 2 sentences. User query: {prompt}"
                try:
                    response = gemini_model.generate_content(sys_prompt).text
                except Exception:
                    response = None
            
            if not response:
                if "cost" in prompt.lower() or "financial" in prompt.lower() or "saving" in prompt.lower():
                    response = f"Under [{scenario}], LEVIATHAN OS bypasses static anchorage queues, saving $48,000 per voyage and reducing auxiliary fuel burn by 21%."
                elif "malacca" in prompt.lower() or "suez" in prompt.lower():
                    response = f"Active telemetry indicates severe bottleneck friction in this corridor. Autonomous rerouting protocols have been successfully dispatched."
                else:
                    response = f"O.M.E.G.A. Core analysis active under [{scenario}]. Fleet telemetry nominal, SDG 13 emission targets maintained."
            
            st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

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
        st.markdown(f'<div class="glass-card"><div class="kpi-title">Monitored Vessels</div><div class="kpi-value">{len(data["entity_id"].unique()) * 18}</div><div class="kpi-badge badge-green">Live Pipeline Sync</div></div>', unsafe_allow_html=True)
    with col2:
        choke_count = int(data['is_chokepoint'].sum() / 8)
        is_crisis = "Nominal" not in scenario
        b_html = f'<div class="kpi-badge badge-red"><span class="pulse-dot red"></span>{scenario.split(" ")[1]} Active</div>' if is_crisis else '<div class="kpi-badge badge-amber">Standard Queuing</div>'
        st.markdown(f'<div class="glass-card"><div class="kpi-title">Active Bottlenecks</div><div class="kpi-value" style="color: {"#EF4444" if is_crisis else "#F8FAFC"}">{choke_count}</div>{b_html}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="glass-card glass-card-accent"><div class="kpi-title">Fuel Inefficiency Averted</div><div class="kpi-value">3,420 MT</div><div class="kpi-badge badge-green">+$48,000 Saved (24h)</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="glass-card"><div class="kpi-title">CO2 Emissions Abated</div><div class="kpi-value">10,773 T</div><div class="kpi-badge badge-green">SDG 13 Compliant</div></div>', unsafe_allow_html=True)

    c_map, c_term = st.columns([7, 3])
    with c_map:
        st.markdown("<div style='font-size: 1.1rem; font-weight: 600; margin-bottom: 12px;'>Spatial Density Elevators (3D Water Channels)</div>", unsafe_allow_html=True)
        s_lat, s_lon, zoom = (13.0, 82.0, 4.2) if "Typhoon" in scenario else ((5.5, 95.0, 4.5) if "Pirate" in scenario else ((27.0, 34.6, 4.5) if "Suez" in scenario else (15.0, 75.0, 3.2)))
        
        st.pydeck_chart(pdk.Deck(
            map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
            initial_view_state=pdk.ViewState(latitude=s_lat, longitude=s_lon, zoom=zoom, pitch=45, bearing=-10),
            layers=[
                pdk.Layer(
                    'HexagonLayer', data=data, get_position='[longitude, latitude]', 
                    radius=30000, elevation_scale=65, elevation_range=[0, 3500], 
                    pickable=True, extruded=True, get_fill_color="[16, 185, 129, 160]"
                ),
                pdk.Layer(
                    'ScatterplotLayer', data=data[data['is_chokepoint']], 
                    get_position='[longitude, latitude]', 
                    get_color='[239, 68, 68, 220]' if "Nominal" not in scenario else '[245, 158, 11, 200]', 
                    get_radius=40000, pickable=True
                )
            ],
            tooltip={"text": "Vessel Cluster Density"}
        ))

    with c_term:
        st.markdown("<div style='font-size: 1.1rem; font-weight: 600; margin-bottom: 12px;'>Autonomous Dispatch Logic</div>", unsafe_allow_html=True)
        t1, t2, t3, t4 = [(datetime.now() - timedelta(seconds=x)).strftime("%H:%M:%S") for x in (12, 45, 120, 240)]
        if "Nominal" not in scenario:
            logs = f"<div><span class='term-time'>[{t1}]</span> <span class='term-crit'>[CRITICAL]</span> {scenario.upper()}</div><div><span class='term-time'>[{t2}]</span> <span class='term-sys'>[SYS]</span> HALTING AIS LEGACY ROUTES</div><div><span class='term-time'>[{t3}]</span> <span style='color:#10B981;'>[SUCCESS]</span> AUTONOMOUS REROUTE ACTIVE</div>"
        else:
            logs = f"<div><span class='term-time'>[{t1}]</span> <span class='term-sys'>[SYS]</span> TELEMETRY SYNC ACTIVE</div><div><span class='term-time'>[{t2}]</span> <span style='color:#10B981;'>[SUCCESS]</span> INDIAN OCEAN CLEAR</div><div><span class='term-time'>[{t3}]</span> <span style='color:#F59E0B;'>[WARN]</span> SUEZ CANAL LOAD INCREASING 12%</div>"
        st.markdown(f'<div class="terminal-console"><div>> INITIALIZING O.M.E.G.A...</div><br>{logs}<br><div class="pulse-dot"></div> <span style="color:#64748B;">Awaiting pings...</span></div>', unsafe_allow_html=True)

# ==========================================
# SCREEN 2: CHOKEPOINT ANALYTICS
# ==========================================
elif screen == "Chokepoint Analytics":
    st.markdown("""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 2.2rem; font-weight: 700; margin-bottom: 4px; color: #FFFFFF;">Bottleneck & Chokepoint Analytics</h1>
            <p style="color: #94A3B8; font-size: 0.95rem;">Granular regional vulnerability analysis across global trade corridors.</p>
        </div>
    """, unsafe_allow_html=True)
    
    ai_status = f"Active Scenario: {scenario}. Real-time telemetry adjusting queue profiles."
    briefing_text = ""
    if GEMINI_AVAILABLE:
        try:
            briefing_text = gemini_model.generate_content(f"Write a 2-sentence executive briefing for logistics managers under scenario: {scenario}. Tone: Cold, analytical.").text
        except:
             briefing_text = ""
             
    if not briefing_text:
        if "Typhoon" in scenario:
            briefing_text = "Typhoon pressure drop detected in Bay of Bengal. Halting coastal feeder routes to eliminate auxiliary fuel waste."
        elif "Pirate" in scenario:
            briefing_text = "Security breach isolated in Malacca Strait. Autonomous detour vectors dispatched to all regional tonnage."
        elif "Suez" in scenario:
            briefing_text = "Megaship grounding at Suez approach. Rerouting container traffic around the Cape of Good Hope corridor."
        else:
            briefing_text = f"System monitoring {scenario}. Queue stability maintained across primary channels with nominal latency."
            
    box_text = f"🧠 **[O.M.E.G.A LIVE INFERENCE]:** {briefing_text}"
    speech_text = briefing_text
        
    box_style = "background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(15, 23, 42, 0.7) 100%); border: 1px solid rgba(239, 68, 68, 0.3);" if "Nominal" not in scenario else "background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(15, 23, 42, 0.7) 100%); border: 1px solid rgba(59, 130, 246, 0.3);"
    st.markdown(f'<div style="{box_style} padding: 18px; border-radius: 12px; margin-bottom: 24px; font-family: \'JetBrains Mono\'; font-size: 0.85rem; color: #93C5FD; line-height: 1.5;">{box_text}</div>', unsafe_allow_html=True)
    
    if st.button("🎙️ Broadcast AI Voice Briefing", type="secondary"):
        components.html(f"""
            <script>
                var msg = new SpeechSynthesisUtterance("{speech_text}");
                msg.volume = 1;
                msg.rate = 0.95;
                msg.pitch = 0.85;
                window.speechSynthesis.speak(msg);
            </script>
        """, height=0)
        st.toast("Broadcasting AI Executive Briefing...", icon="🔊")
    
    choke_df = data[data['is_chokepoint']]
    col_map, col_metrics = st.columns([2, 1])
    
    with col_map:
        st.markdown("<div style='font-size: 1rem; font-weight: 600; margin-bottom: 8px;'>Global Vulnerability Heatmap</div>", unsafe_allow_html=True)
        st.pydeck_chart(pdk.Deck(
            map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', 
            initial_view_state=pdk.ViewState(latitude=12.0, longitude=80.0, zoom=3.2, pitch=0), 
            layers=[pdk.Layer('HeatmapLayer', data=choke_df, get_position='[longitude, latitude]', radiusPixels=45, intensity=1.5, threshold=0.05)]
        ))
        
    with col_metrics:
        st.markdown('<div class="glass-card"><div class="kpi-title">Average Wait Delay</div><div class="kpi-value" style="color: #F87171;">42.8 Hrs</div><p style="font-size: 0.8rem; color: #94A3B8; margin-top: 8px;">Idle time caused by anchorage queuing.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card"><div class="kpi-title">Fuel Waste Coefficient</div><div class="kpi-value">18.4 MT/day</div><p style="font-size: 0.8rem; color: #94A3B8; margin-top: 8px;">Auxiliary power burned during holding patterns.</p></div>', unsafe_allow_html=True)

    st.markdown("<div style='font-size: 1.2rem; font-weight: 600; margin-top: 30px; margin-bottom: 15px;'>Corridor Disruption Index & Historical Breakdown</div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📊 Analytics Charts", "📋 Raw Telemetry Matrix"])
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='kpi-title'>Monthly Queue Duration (Hours)</div>", unsafe_allow_html=True)
            st.bar_chart(pd.DataFrame({'Idle Hours': [45, 52, 61, 48, 55, 42.8]}, index=['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']))
        with c2:
            st.markdown("<div class='kpi-title'>Fuel Burn Variance by Channel (MT)</div>", unsafe_allow_html=True)
            st.line_chart(pd.DataFrame({'Fuel Burn (MT)': [320, 410, 290, 380, 450]}, index=['Malacca', 'Suez', 'Panama', 'Gibraltar', 'English Channel']))
    with tab2:
        st.dataframe(pd.DataFrame({'Corridor ID': ['CHOKE-901 (Bay of Bengal)', 'CHOKE-402 (Malacca)', 'CHOKE-105 (Suez)', 'CHOKE-888 (Panama)'], 'Active Vessels': [142, 98, 76, 54], 'Avg Delay (Hrs)': [48.2, 39.5, 31.0, 24.4], 'Status': ['CRITICAL', 'WARNING', 'STABLE', 'STABLE']}), use_container_width=True)

# ==========================================
# SCREEN 3: DYNAMIC ECO-ROUTER & ROI
# ==========================================
elif screen == "Dynamic Eco-Router":
    st.markdown("""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 2.2rem; font-weight: 700; margin-bottom: 4px; color: #FFFFFF;">Enterprise ROI & Carbon Offset</h1>
            <p style="color: #94A3B8; font-size: 0.95rem;">Translate SDG 13 Climate Action directly into enterprise profitability.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #10B981; font-size: 1.2rem; margin-bottom: 20px; margin-top: 10px;'>B2B Predictive Savings Calculator</h3>", unsafe_allow_html=True)
    calc_col1, calc_col2 = st.columns(2)
    with calc_col1: fleet_size = st.slider("Active Fleet Size (Vessels)", 5, 250, 45)
    with calc_col2: annual_voyages = st.slider("Average Annual Voyages per Vessel", 10, 100, 32)
        
    total_usd = (fleet_size * annual_voyages * 48000) / 1000000 
    total_co2 = fleet_size * annual_voyages * 278
    carbon_rev = int(total_co2 * 25)
    
    res_c1, res_c2 = st.columns(2)
    with res_c1: st.markdown(f'<div style="margin-top: 10px; margin-bottom: 20px;"><div class="kpi-title">Projected Annual Capital Saved</div><div class="kpi-value" style="font-size: 3rem; color: #10B981;">${total_usd:.1f}M</div></div>', unsafe_allow_html=True)
    with res_c2: st.markdown(f'<div style="margin-top: 10px; margin-bottom: 20px;"><div class="kpi-title">Projected SDG 13 CO2 Abatement</div><div class="kpi-value" style="font-size: 3rem;">{total_co2:,} Tons</div></div>', unsafe_allow_html=True)

    st.markdown(f"""
        <div class="glass-card glass-card-accent">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div><div class="kpi-title" style="color: #10B981;">NEW FEATURE: CARBON CREDIT MONETIZATION ENGINE</div><div style="font-size: 1.2rem; font-weight: 700; color: #F8FAFC; margin-top: 4px;">Estimated Carbon Offset Revenue: <span style="color: #10B981;">${carbon_rev:,} USD / yr</span> <span style="font-size:0.9rem; color:#94A3B8;">(at $25/Ton)</span></div></div>
                <div class="kpi-badge badge-green">ESG Revenue Stream</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='font-size: 1.1rem; color: #94A3B8; margin-top: 30px; margin-bottom: 15px;'>Per-Voyage Bypass Metrics</h3>", unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        st.markdown("""<div class="glass-card" style="border-top: 4px solid #EF4444;"><div style="margin-bottom: 12px;"><span style="font-weight: 700; font-size: 1.1rem; color: #F87171;">Standard Route (Legacy AIS)</span></div>
        <div style="margin-bottom: 14px;"><div style="font-size: 0.8rem; color: #64748B;">CONGESTION DELAY EXPOSURE</div><div style="font-size: 1.4rem; font-weight: 700; color: #F87171;">+38.5 Hours</div></div>
        <div style="margin-bottom: 14px;"><div style="font-size: 0.8rem; color: #64748B;">ESTIMATED FUEL BURN</div><div style="font-size: 1.4rem; font-weight: 700;">412 MT</div></div>
        <div><div style="font-size: 0.8rem; color: #64748B;">CARBON FOOTPRINT</div><div style="font-size: 1.4rem; font-weight: 700; color: #F87171;">1,298 Tons CO2</div></div></div>""", unsafe_allow_html=True)
    with r2:
        st.markdown("""<div class="glass-card glass-card-accent" style="border-top: 4px solid #10B981;"><div style="margin-bottom: 12px;"><span style="font-weight: 700; font-size: 1.1rem; color: #10B981;">LEVIATHAN Dynamic Bypass</span></div>
        <div style="margin-bottom: 14px;"><div style="font-size: 0.8rem; color: #64748B;">CONGESTION DELAY EXPOSURE</div><div style="font-size: 1.4rem; font-weight: 700; color: #10B981;">0.0 Hours (Direct Transit)</div></div>
        <div style="margin-bottom: 14px;"><div style="font-size: 0.8rem; color: #64748B;">ESTIMATED FUEL BURN</div><div style="font-size: 1.4rem; font-weight: 700; color: #10B981;">324 MT (-21.3%)</div></div>
        <div><div style="font-size: 0.8rem; color: #64748B;">CARBON FOOTPRINT</div><div style="font-size: 1.4rem; font-weight: 700; color: #10B981;">1,020 Tons CO2 (-278 Tons)</div></div></div>""", unsafe_allow_html=True)

    justification = ""
    if GEMINI_AVAILABLE:
        try:
            justification = gemini_model.generate_content(f"As an AI logistics commander, write a 3-sentence technical justification for why routing a ship on a detour under scenario '{scenario}' saves fuel compared to idling.").text
        except:
             justification = ""
             
    if not justification:
        justification = f"O.M.E.G.A Core Analysis: Under scenario [{scenario}], while the bypass route introduces spatial deviation, it eliminates static anchorage wait time. By avoiding continuous auxiliary generator burn in the chokepoint queue, overall fuel efficiency increases by 21.3%."
        
    st.markdown(f"""
        <div class="ai-justification-box">
            <strong style="color: #60A5FA;">🧠 O.M.E.G.A. GENERATIVE STRATEGY MATRIX:</strong><br><br>
            {justification}
        </div>
    """, unsafe_allow_html=True)
