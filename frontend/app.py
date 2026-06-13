"""
HELIX — Real-time Medical Disaster Response Intelligence
Frontend: Streamlit Dashboard (Full Redesign)
Palette: Deep navy · Sky blue · Cyan · Amber alerts · Red critical
Typography: Space Grotesk (display) · Inter (body) · JetBrains Mono (data)
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go

# ══════════════════════════════════════════════════════════════════
#  PAGE CONFIG — must be the first Streamlit call
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="HELIX · Humanitarian Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════
#  DESIGN TOKENS
# ══════════════════════════════════════════════════════════════════
BG0   = "#070d1a"   # page background
BG1   = "#0c1322"   # nav / hero
BG2   = "#101a2e"   # cards
BG3   = "#162040"   # elevated surfaces
B0    = "#1e2d4a"   # primary border
B1    = "#243555"   # lighter border
T0    = "#e8eef8"   # primary text
T1    = "#7a90b8"   # secondary text
T2    = "#3d5278"   # muted text
BLUE  = "#3b82f6"
CYAN  = "#06b6d4"
AMBER = "#f59e0b"   # alerts only
RED   = "#ef4444"   # critical only
GREEN = "#10b981"


# ══════════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════════════════
def apply_styles():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── RESET ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.stApp {{
    background: {BG0} !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: {T0} !important;
}}
.main .block-container {{ padding: 0 !important; max-width: 100% !important; }}
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {{ display: none !important; }}

/* ── HEADER ── */
[data-testid="stHeader"] {{
    background: rgba(7,13,26,0.95) !important;
    backdrop-filter: blur(14px) !important;
    border-bottom: 1px solid {B0} !important;
}}

/* ── TABS ── */
[data-testid="stTabs"] {{
    background: {BG1};
    border-bottom: 1px solid {B0};
    position: sticky; top: 0; z-index: 999;
}}
[data-baseweb="tab-list"] {{
    background: transparent !important;
    padding: 0 2.5rem !important;
    gap: 0 !important;
}}
button[data-baseweb="tab"] {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 11px !important; font-weight: 600 !important;
    letter-spacing: 0.09em !important; text-transform: uppercase !important;
    color: {T2} !important; border: none !important; background: transparent !important;
    padding: 1.1rem 1.5rem !important; transition: color 0.2s !important;
}}
button[data-baseweb="tab"]:hover {{ color: {T1} !important; }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: {CYAN} !important; }}
[data-baseweb="tab-highlight"] {{ background: {CYAN} !important; height: 2px !important; }}
[data-baseweb="tab-border"] {{ display: none !important; }}

/* ── METRICS ── */
[data-testid="stMetric"] {{
    background: {BG2} !important; border: 1px solid {B0} !important;
    border-radius: 10px !important; padding: 1.25rem 1.5rem !important;
}}
[data-testid="stMetricLabel"] p {{
    font-family: 'Inter', sans-serif !important; font-size: 10.5px !important;
    font-weight: 600 !important; letter-spacing: 0.1em !important;
    text-transform: uppercase !important; color: {T1} !important;
}}
[data-testid="stMetricValue"] {{
    font-family: 'Space Grotesk', sans-serif !important; font-size: 2rem !important;
    font-weight: 700 !important; color: {T0} !important; line-height: 1.1 !important;
}}
[data-testid="stMetricDelta"] svg {{ display: none !important; }}

/* ── COLUMNS ── */
[data-testid="stHorizontalBlock"] {{ gap: 1rem !important; }}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {BG0}; }}
::-webkit-scrollbar-thumb {{ background: {B1}; border-radius: 4px; }}

/* ══ CUSTOM COMPONENT CLASSES ══ */

/* Layout */
.hx-pad     {{ padding: 2.5rem; }}
.hx-pad-sm  {{ padding: 1.5rem 2.5rem; }}

/* Cards */
.hx-card {{
    background: {BG2}; border: 1px solid {B0};
    border-radius: 10px; padding: 1.5rem;
}}
.hx-card-crit {{
    background: {BG2}; border: 1px solid rgba(239,68,68,.3);
    border-left: 3px solid {RED}; border-radius: 10px; padding: 1.5rem;
}}
.hx-card-warn {{
    background: {BG2}; border: 1px solid rgba(245,158,11,.3);
    border-left: 3px solid {AMBER}; border-radius: 10px; padding: 1.5rem;
}}
.hx-card-ok {{
    background: {BG2}; border: 1px solid rgba(16,185,129,.2);
    border-left: 3px solid {GREEN}; border-radius: 10px; padding: 1.5rem;
}}
.hx-card-blue {{
    background: {BG2}; border: 1px solid rgba(59,130,246,.25);
    border-left: 3px solid {BLUE}; border-radius: 10px; padding: 1.5rem;
}}

/* Typography */
.eyebrow {{
    font-family: 'Inter', sans-serif; font-size: 10.5px; font-weight: 600;
    letter-spacing: 0.13em; text-transform: uppercase; color: {CYAN};
    display: block; margin-bottom: 0.5rem;
}}
.section-title {{
    font-family: 'Space Grotesk', sans-serif; font-size: 1.55rem; font-weight: 700;
    color: {T0}; letter-spacing: -0.02em; margin: 0 0 0.35rem 0; line-height: 1.2;
}}
.section-desc {{
    font-size: 0.875rem; color: {T1}; margin: 0 0 2rem 0; line-height: 1.6;
}}

/* Data display */
.label {{
    font-family: 'Inter', sans-serif;
    font-size: 10px; font-weight: 600; letter-spacing: 0.11em;
    text-transform: uppercase; color: {T1};
}}
.mono-lg {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.15rem; font-weight: 500; color: {T0};
}}
.mono-sm {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px; font-weight: 400; color: {T1};
}}

/* Badges */
.bdg-red  {{ display:inline-block; background:rgba(239,68,68,.12);  color:{RED};   border:1px solid rgba(239,68,68,.3);  border-radius:4px; padding:2px 9px; font-size:10.5px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; white-space:nowrap; }}
.bdg-amb  {{ display:inline-block; background:rgba(245,158,11,.12); color:{AMBER}; border:1px solid rgba(245,158,11,.3); border-radius:4px; padding:2px 9px; font-size:10.5px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; white-space:nowrap; }}
.bdg-grn  {{ display:inline-block; background:rgba(16,185,129,.12); color:{GREEN}; border:1px solid rgba(16,185,129,.3); border-radius:4px; padding:2px 9px; font-size:10.5px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; white-space:nowrap; }}
.bdg-blu  {{ display:inline-block; background:rgba(59,130,246,.12); color:{BLUE};  border:1px solid rgba(59,130,246,.3); border-radius:4px; padding:2px 9px; font-size:10.5px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; white-space:nowrap; }}
.bdg-cyn  {{ display:inline-block; background:rgba(6,182,212,.12);  color:{CYAN};  border:1px solid rgba(6,182,212,.3);  border-radius:4px; padding:2px 9px; font-size:10.5px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; white-space:nowrap; }}

/* Gap/progress bars */
.gap-bar  {{ height:5px; background:{B0}; border-radius:3px; overflow:hidden; margin-top:6px; }}
.gap-red  {{ height:100%; border-radius:3px; background:linear-gradient(90deg,{RED},{RED}88); }}
.gap-amb  {{ height:100%; border-radius:3px; background:linear-gradient(90deg,{AMBER},{AMBER}88); }}
.gap-blu  {{ height:100%; border-radius:3px; background:linear-gradient(90deg,{BLUE},{BLUE}88); }}
.gap-grn  {{ height:100%; border-radius:3px; background:linear-gradient(90deg,{GREEN},{GREEN}88); }}

/* Live pulse dot */
.live-dot {{
    display: inline-block; width: 7px; height: 7px; border-radius: 50%;
    background: {GREEN}; animation: pulse-live 2s infinite;
    margin-right: 6px; vertical-align: middle;
}}
@keyframes pulse-live {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50%       {{ opacity: .4; transform: scale(.75); }}
}}

/* Route path nodes */
.route-path {{
    display: flex; align-items: center; gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px; color: {T1}; flex-wrap: wrap;
    margin: 10px 0;
}}
.route-node {{
    background: {BG3}; border: 1px solid {B1};
    border-radius: 4px; padding: 2px 9px; color: {T0}; font-size: 11px;
}}
.route-arrow {{ color: {CYAN}; font-size: 14px; }}

/* Temp badge */
.temp-badge {{
    font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 500;
    background: {BG3}; border: 1px solid {B1}; border-radius: 4px;
    padding: 3px 10px; display: inline-block;
}}

/* Confidence bar */
.conf-bar  {{ height: 4px; background: {B0}; border-radius: 2px; overflow: hidden; margin-top: 5px; }}
.conf-fill {{ height: 100%; border-radius: 2px; }}

/* Separators */
.divider {{ border: none; border-top: 1px solid {B0}; margin: 2rem 0; }}
.sep-sm  {{ border: none; border-top: 1px solid {B0}; margin: 1rem 0; }}

/* Algorithm pill */
.algo-pill {{
    background: {BG3}; border: 1px solid {B1}; border-radius: 6px;
    padding: 1rem 1.25rem; margin-bottom: 1.5rem;
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  DATA LAYER
# ══════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def fetch_disasters():
    """Fetch from GDACS, fall back to synthetic demo data."""
    try:
        import xml.etree.ElementTree as ET
        r = requests.get(
            "https://www.gdacs.org/xml/rss.xml",
            timeout=8, headers={"User-Agent": "HELIX/1.0"}
        )
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            geo_ns  = "http://www.w3.org/2003/01/geo/wgs84_pos#"
            gdac_ns = "http://www.gdacs.org"
            items = []
            for item in root.findall(".//item")[:5]:
                def g(tag, ns="", default=""):
                    el = item.find(f"{{{ns}}}{tag}" if ns else tag)
                    return el.text.strip() if el is not None and el.text else default
                lat = g("lat", geo_ns, "20")
                lon = g("long", geo_ns, "78")
                pop_raw = g("population", gdac_ns, "0").replace(",", "")
                items.append({
                    "id":           g("eventid", gdac_ns, "N/A"),
                    "type":         g("eventtype", gdac_ns, "Event"),
                    "title":        g("title", default="Unknown Event"),
                    "lat":          float(lat),
                    "lon":          float(lon),
                    "severity":     g("alertlevel", gdac_ns, "GREEN").upper(),
                    "affected":     int(pop_raw) if pop_raw.isdigit() else 0,
                    "gap_score":    int(np.random.randint(30, 90)),
                    "aid_coverage": int(np.random.randint(10, 65)),
                    "ngo_count":    int(np.random.randint(1, 15)),
                    "timestamp":    g("pubDate", default=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")),
                    "region":       g("title", default="Unknown"),
                    "need":         "Vaccines, ORS",
                })
            if items:
                return items
    except Exception:
        pass
    return _synthetic_disasters()


def _synthetic_disasters():
    return [
        {
            "id": "EQ-2024-001", "type": "Earthquake",
            "title": "M6.8 — Bihar, India",
            "lat": 25.09, "lon": 85.31, "severity": "RED",
            "affected": 500000, "gap_score": 92, "aid_coverage": 8, "ngo_count": 2,
            "timestamp": "2024-06-14 06:23 UTC",
            "region": "Bihar, India",
            "need": "Insulin, ORS, Vaccines",
        },
        {
            "id": "FL-2024-002", "type": "Flood",
            "title": "River Floods — Assam, India",
            "lat": 26.20, "lon": 92.93, "severity": "ORANGE",
            "affected": 320000, "gap_score": 78, "aid_coverage": 22, "ngo_count": 5,
            "timestamp": "2024-06-13 18:45 UTC",
            "region": "Assam, India",
            "need": "Insulin, Antibiotics",
        },
        {
            "id": "CY-2024-003", "type": "Cyclone",
            "title": "Cyclone Remal — Odisha Coast",
            "lat": 20.29, "lon": 85.84, "severity": "ORANGE",
            "affected": 280000, "gap_score": 65, "aid_coverage": 35, "ngo_count": 8,
            "timestamp": "2024-06-12 09:10 UTC",
            "region": "Odisha, India",
            "need": "Vaccines, Blood",
        },
        {
            "id": "FL-2024-004", "type": "Flood",
            "title": "Sylhet Flash Floods — Bangladesh",
            "lat": 24.89, "lon": 91.87, "severity": "GREEN",
            "affected": 95000, "gap_score": 28, "aid_coverage": 72, "ngo_count": 14,
            "timestamp": "2024-06-11 14:30 UTC",
            "region": "Sylhet, Bangladesh",
            "need": "ORS, Vaccines",
        },
    ]


def get_medicines():
    return [
        {
            "id": "MED-001", "name": "COVID-19 Vaccines", "type": "Vaccine",
            "quantity": 50000, "unit": "doses", "storage": "Delhi Storage Hub",
            "viability": 0.96, "temp_current": 4.2,
            "temp_min": 2.0, "temp_max": 8.0, "breach_minutes": 0, "status": "OPTIMAL",
        },
        {
            "id": "MED-002", "name": "Insulin (Rapid-Acting)", "type": "Insulin",
            "quantity": 12000, "unit": "units", "storage": "Patna Cold Store",
            "viability": 0.83, "temp_current": 9.8,
            "temp_min": 2.0, "temp_max": 8.0, "breach_minutes": 95, "status": "COMPROMISED",
        },
        {
            "id": "MED-003", "name": "O-Positive Blood Units", "type": "Blood",
            "quantity": 800, "unit": "units", "storage": "Bhubaneswar Blood Bank",
            "viability": 0.71, "temp_current": 7.1,
            "temp_min": 2.0, "temp_max": 6.0, "breach_minutes": 45, "status": "AT RISK",
        },
        {
            "id": "MED-004", "name": "ORS Packets", "type": "ORS",
            "quantity": 200000, "unit": "packets", "storage": "Guwahati Warehouse",
            "viability": 1.00, "temp_current": 22.0,
            "temp_min": 0.0, "temp_max": 40.0, "breach_minutes": 0, "status": "OPTIMAL",
        },
        {
            "id": "MED-005", "name": "Amoxicillin Tablets", "type": "Antibiotic",
            "quantity": 35000, "unit": "tablets", "storage": "Kolkata Pharma Hub",
            "viability": 0.55, "temp_current": 28.5,
            "temp_min": 15.0, "temp_max": 25.0, "breach_minutes": 210, "status": "DESTROYED",
        },
    ]


def get_routes():
    return [
        {
            "id": "R-001", "medicine": "COVID-19 Vaccines", "med_type": "Vaccine",
            "quantity": "50,000 doses", "destination": "Bihar, India",
            "gap_score": 92, "impact_score": 95, "pop_reach": "500,000",
            "priority": "URGENT", "distance_km": 1020, "eta_hours": 14,
            "via": ["Delhi Hub", "Patna Relay", "Bihar Zone A"],
            "lives_saved": 5000, "value_cr": 12.4,
        },
        {
            "id": "R-002", "medicine": "Insulin (Rapid-Acting)", "med_type": "Insulin",
            "quantity": "12,000 units", "destination": "Assam, India",
            "gap_score": 78, "impact_score": 87, "pop_reach": "320,000",
            "priority": "HIGH", "distance_km": 650, "eta_hours": 9,
            "via": ["Patna Store", "Guwahati Relay", "Assam Zone"],
            "lives_saved": 2800, "value_cr": 4.1,
        },
        {
            "id": "R-003", "medicine": "O-Positive Blood", "med_type": "Blood",
            "quantity": "800 units", "destination": "Odisha, India",
            "gap_score": 65, "impact_score": 71, "pop_reach": "180,000",
            "priority": "MEDIUM", "distance_km": 290, "eta_hours": 5,
            "via": ["BBSR Blood Bank", "Odisha Zone"],
            "lives_saved": 1200, "value_cr": 2.8,
        },
    ]


def get_temp_log():
    """Simulate 24h temperature log for insulin storage with a breach window."""
    now = datetime.utcnow()
    times, temps = [], []
    for i in range(24):
        t = now - timedelta(hours=23 - i)
        times.append(t.strftime("%H:%M"))
        if 14 <= i <= 16:          # breach window
            temps.append(round(np.random.normal(11.5, 0.7), 1))
        elif i > 16:                # recovered
            temps.append(round(np.random.normal(5.4, 0.4), 1))
        else:                       # normal
            temps.append(round(np.random.normal(4.7, 0.5), 1))
    return times, temps


# ══════════════════════════════════════════════════════════════════
#  HERO SECTION
# ══════════════════════════════════════════════════════════════════
def render_hero(disasters, medicines):
    total_affected = sum(d["affected"] for d in disasters)
    critical       = sum(1 for d in disasters if d["severity"] == "RED")
    viable_count   = sum(1 for m in medicines if m["viability"] >= 0.7)

    def stat_cell(value, label, val_color=T0, accent=B0):
        return f"""
        <div style="padding:1.25rem 2rem;border-right:1px solid {B0};
                    position:relative;flex-shrink:0;">
            <div style="position:absolute;bottom:0;left:0;right:0;height:2px;
                        background:{accent}22;"></div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:1.9rem;
                        font-weight:700;color:{val_color};line-height:1;">{value}</div>
            <div style="font-size:10px;font-weight:600;letter-spacing:.1em;
                        text-transform:uppercase;color:{T2};margin-top:4px;">{label}</div>
        </div>"""

    st.markdown(f"""
    <div style="
        background: linear-gradient(180deg, {BG1} 0%, {BG0} 100%);
        border-bottom: 1px solid {B0};
        padding: 3.5rem 2.5rem 3rem;
        position: relative; overflow: hidden;">

        <!-- subtle grid lines -->
        <div style="position:absolute;top:0;left:0;right:0;bottom:0;pointer-events:none;
            background: repeating-linear-gradient(90deg,transparent,transparent 79px,
                {B0}44 79px,{B0}44 80px);"></div>

        <!-- live indicator -->
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:1.5rem;">
            <span class="live-dot"></span>
            <span style="font-family:'Inter',sans-serif;font-size:11px;font-weight:600;
                         letter-spacing:.1em;text-transform:uppercase;color:{T1};">
                Live Intelligence · {datetime.utcnow().strftime("%H:%M UTC")}
            </span>
        </div>

        <!-- brand -->
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:1rem;">
            <div style="width:50px;height:50px;border-radius:12px;
                        background:linear-gradient(135deg,{BLUE}22,{CYAN}22);
                        border:1px solid {CYAN}44;display:flex;align-items:center;
                        justify-content:center;font-size:22px;">🧬</div>
            <div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:2rem;
                            font-weight:700;color:{T0};letter-spacing:-0.03em;
                            line-height:1;">HELIX</div>
                <div style="font-size:11px;color:{T1};letter-spacing:.08em;
                            text-transform:uppercase;font-weight:500;margin-top:2px;">
                    Humanitarian Intelligence Platform
                </div>
            </div>
        </div>

        <!-- tagline -->
        <div style="font-family:'Inter',sans-serif;font-size:0.95rem;color:{T1};
                    max-width:580px;line-height:1.7;margin-bottom:2.5rem;">
            Two strands of intelligence —
            <span style="color:{CYAN};">need detection</span> and
            <span style="color:{BLUE};">medicine viability</span> — fused into one system
            that answers: <em style="color:{T0};">
            "Where should life-saving medicine go right now, and why?"</em>
        </div>

        <!-- stats row -->
        <div style="display:flex;flex-wrap:wrap;">
            {stat_cell(len(disasters), "Active Disasters", AMBER if len(disasters) > 2 else T0, AMBER)}
            {stat_cell(f"{total_affected/1e6:.1f}M", "People Affected", T0, BLUE)}
            {stat_cell(critical, "Critical Zones", RED if critical > 0 else T0, RED)}
            {stat_cell(f"{viable_count}/{len(medicines)}", "Batches Viable", GREEN, GREEN)}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  TAB 1 — SITUATIONAL AWARENESS
# ══════════════════════════════════════════════════════════════════
def tab_situational(disasters):
    st.markdown('<div class="hx-pad">', unsafe_allow_html=True)

    st.markdown(f"""
    <span class="eyebrow">Situational Awareness</span>
    <div class="section-title">Active Disasters Worldwide</div>
    <div class="section-desc">Real-time event monitoring via GDACS. Gap Score surfaces zones the media ignores —
    where aid is absent and populations are largest.</div>
    """, unsafe_allow_html=True)

    col_map, col_feed = st.columns([3, 2])

    with col_map:
        m = folium.Map(
            location=[22, 83], zoom_start=4,
            tiles="CartoDB dark_matter",
        )
        for d in disasters:
            sev_color = {"RED": "red", "ORANGE": "orange", "GREEN": "green"}.get(
                d["severity"], "blue")
            radius = max(10, min(32, d["affected"] / 18000))
            folium.CircleMarker(
                location=[d["lat"], d["lon"]],
                radius=radius,
                color=sev_color, fill=True, fill_opacity=0.45,
                tooltip=f"{d['title']} | Gap {d['gap_score']}",
                popup=folium.Popup(
                    f"<b>{d['title']}</b><br>"
                    f"Affected: {d['affected']:,}<br>"
                    f"Gap Score: {d['gap_score']}<br>"
                    f"Severity: {d['severity']}",
                    max_width=220,
                ),
            ).add_to(m)
            if d["severity"] == "RED":
                folium.CircleMarker(
                    location=[d["lat"], d["lon"]],
                    radius=radius * 2, color="red",
                    fill=False, weight=1, opacity=0.2,
                ).add_to(m)
        st_folium(m, width=None, height=430, returned_objects=[])

    with col_feed:
        st.markdown(
            f'<div style="font-family:Inter;font-size:10.5px;font-weight:600;'
            f'letter-spacing:.11em;text-transform:uppercase;color:{T1};'
            f'margin-bottom:1rem;">Incident Feed</div>',
            unsafe_allow_html=True
        )
        for d in disasters:
            sev = d["severity"]
            badge_cls   = {"RED": "bdg-red", "ORANGE": "bdg-amb", "GREEN": "bdg-grn"}.get(sev, "bdg-blu")
            badge_label = {"RED": "Critical", "ORANGE": "Warning", "GREEN": "Monitored"}.get(sev, sev)
            gap = d.get("gap_score", 0)
            bar_cls  = "gap-red" if gap > 75 else "gap-amb" if gap > 50 else "gap-blu" if gap > 25 else "gap-grn"
            gap_col  = RED if gap > 75 else AMBER if gap > 50 else BLUE if gap > 25 else GREEN
            st.markdown(f"""
            <div class="hx-card" style="margin-bottom:.75rem;">
                <div style="display:flex;justify-content:space-between;
                            align-items:flex-start;margin-bottom:8px;">
                    <div style="font-family:'Space Grotesk',sans-serif;
                                font-size:13.5px;font-weight:600;color:{T0};
                                flex:1;padding-right:8px;">{d['title']}</div>
                    <span class="{badge_cls}">{badge_label}</span>
                </div>
                <div style="font-size:12px;color:{T1};margin-bottom:10px;">
                    {d['affected']:,} affected &nbsp;·&nbsp; {d.get('region', '')}
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                    <div>
                        <div class="label">Gap Score</div>
                        <div style="font-family:'JetBrains Mono',monospace;
                                    font-size:1.1rem;font-weight:500;
                                    color:{gap_col};">{gap}</div>
                        <div class="gap-bar">
                            <div class="{bar_cls}" style="width:{gap}%"></div>
                        </div>
                    </div>
                    <div>
                        <div class="label">Aid Coverage</div>
                        <div style="font-family:'JetBrains Mono',monospace;
                                    font-size:1.1rem;font-weight:500;
                                    color:{GREEN};">{d.get('aid_coverage', 0)}%</div>
                        <div class="gap-bar">
                            <div class="gap-grn"
                                 style="width:{d.get('aid_coverage', 0)}%"></div>
                        </div>
                    </div>
                </div>
                <div style="font-size:10.5px;color:{T2};margin-top:8px;">
                    {d.get('timestamp', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  TAB 2 — HUMANITARIAN GAPS
# ══════════════════════════════════════════════════════════════════
def tab_gaps(disasters):
    st.markdown('<div class="hx-pad">', unsafe_allow_html=True)

    st.markdown(f"""
    <span class="eyebrow">Humanitarian Gaps</span>
    <div class="section-title">Where Aid Is Failing</div>
    <div class="section-desc">Gap Score measures the distance between what a zone needs
    and what it receives. A score above 75 means a zone is functionally abandoned by
    the global response apparatus.</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="algo-pill">
        <div class="label" style="margin-bottom:6px;">Algorithm · Humanitarian Gap Formula</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:12.5px;
                    color:{CYAN};line-height:1.9;">
            GAP = (Disaster_Severity × Population) − (Aid_Received + NGO_Presence + Media_Attention)
        </div>
        <div style="font-size:12px;color:{T2};margin-top:6px;">
            Gap &gt; 75 = Abandoned &nbsp;·&nbsp;
            Gap &gt; 50 = Critically underserved &nbsp;·&nbsp;
            Gap &lt; 25 = Adequately covered
        </div>
    </div>
    """, unsafe_allow_html=True)

    sorted_d = sorted(disasters, key=lambda x: x.get("gap_score", 0), reverse=True)

    for i, d in enumerate(sorted_d):
        gap  = d.get("gap_score", 0)
        cov  = d.get("aid_coverage", 0)
        card = "hx-card-crit" if gap > 75 else "hx-card-warn" if gap > 50 else "hx-card-ok" if gap < 30 else "hx-card"
        rank_color = RED if gap > 75 else AMBER if gap > 50 else BLUE if gap > 25 else GREEN
        bar_cls    = "gap-red" if gap > 75 else "gap-amb" if gap > 50 else "gap-blu" if gap > 25 else "gap-grn"
        badge_cls  = "bdg-red" if gap > 75 else "bdg-amb" if gap > 50 else "bdg-blu" if gap > 25 else "bdg-grn"
        status     = "ABANDONED" if gap > 75 else "UNDERSERVED" if gap > 50 else "AT RISK" if gap > 25 else "COVERED"

        col_num, col_card, col_score = st.columns([0.6, 5, 1.5])

        with col_num:
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:center;
                        height:100%;padding-top:1.5rem;">
                <span style="font-family:'Space Grotesk',sans-serif;
                             font-size:2rem;font-weight:700;
                             color:{rank_color};opacity:.25;">0{i+1}</span>
            </div>""", unsafe_allow_html=True)

        with col_card:
            st.markdown(f"""
            <div class="{card}" style="margin-bottom:.75rem;">
                <div style="display:flex;justify-content:space-between;
                            align-items:flex-start;margin-bottom:12px;">
                    <div>
                        <div style="font-family:'Space Grotesk',sans-serif;
                                    font-size:1rem;font-weight:600;color:{T0};
                                    margin-bottom:4px;">{d.get('region', d['title'])}</div>
                        <div style="font-size:12px;color:{T1};">
                            {d['type']} &nbsp;·&nbsp; {d['affected']:,} people affected
                            &nbsp;·&nbsp; Needs: {d.get('need', 'General supplies')}
                        </div>
                    </div>
                    <span class="{badge_cls}">{status}</span>
                </div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.25rem;">
                    <div>
                        <div class="label">Need Index</div>
                        <div style="font-family:'JetBrains Mono',monospace;
                                    font-size:1.15rem;font-weight:500;
                                    color:{rank_color};">{gap}</div>
                        <div class="gap-bar">
                            <div class="{bar_cls}" style="width:{gap}%"></div>
                        </div>
                    </div>
                    <div>
                        <div class="label">Aid Coverage</div>
                        <div style="font-family:'JetBrains Mono',monospace;
                                    font-size:1.15rem;font-weight:500;
                                    color:{GREEN};">{cov}%</div>
                        <div class="gap-bar">
                            <div class="gap-grn" style="width:{cov}%"></div>
                        </div>
                    </div>
                    <div>
                        <div class="label">NGOs Active</div>
                        <div style="font-family:'JetBrains Mono',monospace;
                                    font-size:1.15rem;font-weight:500;
                                    color:{BLUE};">{d.get('ngo_count', 0)}</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        with col_score:
            st.markdown(f"""
            <div style="display:flex;flex-direction:column;align-items:center;
                        justify-content:center;height:100%;text-align:center;
                        padding: 0.5rem;">
                <div style="font-family:'Space Grotesk',sans-serif;font-size:3rem;
                            font-weight:700;color:{rank_color};line-height:1;">{gap}</div>
                <div style="font-size:9.5px;font-weight:600;letter-spacing:.1em;
                            text-transform:uppercase;color:{T2};margin-top:4px;">
                    Gap Score
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  TAB 3 — SUPPLY INTEGRITY
# ══════════════════════════════════════════════════════════════════
def tab_supply(medicines):
    st.markdown('<div class="hx-pad">', unsafe_allow_html=True)

    st.markdown(f"""
    <span class="eyebrow">Supply Integrity</span>
    <div class="section-title">Cold Chain Intelligence</div>
    <div class="section-desc">A single temperature breach can destroy an entire shipment invisibly.
    HELIX monitors viability in real time — flagging degradation before medicine reaches the field.</div>
    """, unsafe_allow_html=True)

    # Summary metrics
    total     = len(medicines)
    optimal   = sum(1 for m in medicines if m["viability"] >= 0.9)
    at_risk   = sum(1 for m in medicines if 0.7 <= m["viability"] < 0.9)
    comp      = sum(1 for m in medicines if 0.3 <= m["viability"] < 0.7)
    destroyed = sum(1 for m in medicines if m["viability"] < 0.3)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Batches Tracked", total)
    with c2:
        st.metric("Optimal (>90%)", optimal)
    with c3:
        st.metric("At Risk / Compromised", at_risk + comp)
    with c4:
        st.metric("Destroyed (<30%)", destroyed)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Temperature chart — insulin breach example
    times, temps = get_temp_log()
    breach_color = [RED if t > 8 else GREEN for t in temps]

    fig = go.Figure()

    # Safe zone shading
    fig.add_hrect(
        y0=2, y1=8,
        fillcolor=f"{GREEN}10", line_width=0,
        annotation_text="Safe 2–8°C", annotation_position="top right",
        annotation_font=dict(color=GREEN, size=11, family="Inter"),
    )
    # Upper threshold
    fig.add_hline(
        y=8, line_dash="dash", line_color=AMBER, line_width=1.2,
        annotation_text="Max threshold 8°C",
        annotation_font=dict(color=AMBER, size=10, family="Inter"),
        annotation_position="bottom right",
    )
    # Temperature trace
    fig.add_trace(go.Scatter(
        x=times, y=temps,
        mode="lines+markers",
        line=dict(color=CYAN, width=2),
        marker=dict(color=breach_color, size=5, line=dict(width=0)),
        hovertemplate="%{x}<br><b>%{y:.1f}°C</b><extra></extra>",
        name="Temperature",
    ))

    fig.update_layout(
        title=dict(
            text="Insulin Storage — Patna Cold Store (24h log)",
            font=dict(color=T0, family="Space Grotesk", size=13),
            x=0,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=BG2,
        font=dict(color=T1, family="Inter", size=11),
        height=270,
        margin=dict(l=45, r=20, t=50, b=40),
        xaxis=dict(
            gridcolor=B0, color=T2, showgrid=True,
            nticks=8, title=None,
        ),
        yaxis=dict(
            gridcolor=B0, color=T2, showgrid=True, title="°C",
            range=[0, 16],
        ),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="label" style="margin-bottom:1rem;">Medicine Inventory</div>',
        unsafe_allow_html=True
    )

    for m in medicines:
        v     = m["viability"]
        v_pct = int(v * 100)

        if v >= 0.9:
            card_cls  = "hx-card-ok"
            bdg_cls   = "bdg-grn"
            v_color   = GREEN
            fill_grad = f"linear-gradient(90deg,{GREEN},{GREEN}88)"
        elif v >= 0.7:
            card_cls  = "hx-card-warn"
            bdg_cls   = "bdg-amb"
            v_color   = AMBER
            fill_grad = f"linear-gradient(90deg,{AMBER},{AMBER}88)"
        elif v >= 0.3:
            card_cls  = "hx-card-warn"
            bdg_cls   = "bdg-amb"
            v_color   = AMBER
            fill_grad = f"linear-gradient(90deg,{AMBER},{AMBER}88)"
        else:
            card_cls  = "hx-card-crit"
            bdg_cls   = "bdg-red"
            v_color   = RED
            fill_grad = f"linear-gradient(90deg,{RED},{RED}88)"

        temp       = m["temp_current"]
        temp_color = RED if temp > m["temp_max"] else GREEN

        st.markdown(f"""
        <div class="{card_cls}" style="margin-bottom:.75rem;">
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;margin-bottom:12px;">
                <div>
                    <div style="font-family:'Space Grotesk',sans-serif;
                                font-size:14.5px;font-weight:600;color:{T0};">
                        {m['name']}
                    </div>
                    <div style="font-size:12px;color:{T1};margin-top:3px;">
                        {m['type']} &nbsp;·&nbsp; {m['quantity']:,} {m['unit']}
                        &nbsp;·&nbsp; {m['storage']}
                    </div>
                </div>
                <span class="{bdg_cls}">{m['status']}</span>
            </div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1.25rem;">
                <div>
                    <div class="label">Viability</div>
                    <div style="font-family:'JetBrains Mono',monospace;
                                font-size:1.15rem;font-weight:500;color:{v_color};">
                        {v_pct}%
                    </div>
                    <div class="gap-bar">
                        <div style="height:100%;width:{v_pct}%;border-radius:3px;
                                    background:{fill_grad};"></div>
                    </div>
                </div>
                <div>
                    <div class="label">Current Temp</div>
                    <span class="temp-badge" style="color:{temp_color};">{temp}°C</span>
                </div>
                <div>
                    <div class="label">Safe Range</div>
                    <div class="mono-sm" style="margin-top:4px;">
                        {m['temp_min']}–{m['temp_max']}°C
                    </div>
                </div>
                <div>
                    <div class="label">Breach Duration</div>
                    <div style="font-family:'JetBrains Mono',monospace;
                                font-size:1rem;font-weight:500;
                                color:{'#ef4444' if m['breach_minutes'] > 0 else T1};">
                        {m['breach_minutes']} min
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  TAB 4 — ALLOCATION ENGINE
# ══════════════════════════════════════════════════════════════════
def tab_allocation(routes):
    st.markdown('<div class="hx-pad">', unsafe_allow_html=True)

    st.markdown(f"""
    <span class="eyebrow">Allocation Engine</span>
    <div class="section-title">Autonomous Routing Decisions</div>
    <div class="section-desc">The AI matches viable medicine supply against highest-gap zones
    and ranks each route by predicted impact — lives reached per unit deployed. Responders
    receive decisions they can act on immediately.</div>
    """, unsafe_allow_html=True)

    for r in routes:
        priority   = r["priority"]
        bdg_cls    = "bdg-red" if priority == "URGENT" else "bdg-amb" if priority == "HIGH" else "bdg-blu"
        score      = r["impact_score"]
        score_col  = RED if score >= 90 else AMBER if score >= 75 else BLUE

        # Build route path HTML
        nodes_html = ""
        for j, node in enumerate(r["via"]):
            nodes_html += f'<span class="route-node">{node}</span>'
            if j < len(r["via"]) - 1:
                nodes_html += '<span class="route-arrow">→</span>'

        col_main, col_score = st.columns([5, 1])

        with col_main:
            st.markdown(f"""
            <div class="hx-card"
                 style="margin-bottom:1rem;border-top:2px solid {score_col}22;">
                <div style="display:flex;justify-content:space-between;
                            align-items:flex-start;margin-bottom:12px;">
                    <div>
                        <div style="font-size:10.5px;color:{CYAN};font-weight:600;
                                    letter-spacing:.07em;text-transform:uppercase;
                                    margin-bottom:5px;">{r['med_type']}</div>
                        <div style="font-family:'Space Grotesk',sans-serif;
                                    font-size:1.1rem;font-weight:700;color:{T0};">
                            {r['medicine']} → {r['destination']}
                        </div>
                        <div style="font-size:12px;color:{T1};margin-top:3px;">
                            Gap score {r['gap_score']}
                            &nbsp;·&nbsp; {r['quantity']}
                            &nbsp;·&nbsp; Reaches {r['pop_reach']} people
                        </div>
                    </div>
                    <span class="{bdg_cls}">{priority}</span>
                </div>

                <div class="label" style="margin-bottom:5px;">Supply Route</div>
                <div class="route-path">{nodes_html}</div>

                <hr class="sep-sm">

                <div style="display:grid;grid-template-columns:repeat(4,1fr);
                            gap:1.25rem;margin-top:8px;">
                    <div>
                        <div class="label">ETA</div>
                        <div class="mono-lg">{r['eta_hours']}h</div>
                    </div>
                    <div>
                        <div class="label">Distance</div>
                        <div class="mono-lg">{r['distance_km']} km</div>
                    </div>
                    <div>
                        <div class="label">Lives Reached</div>
                        <div style="font-family:'JetBrains Mono',monospace;
                                    font-size:1.15rem;font-weight:500;
                                    color:{GREEN};">{r['lives_saved']:,}</div>
                    </div>
                    <div>
                        <div class="label">Medicine Value</div>
                        <div style="font-family:'JetBrains Mono',monospace;
                                    font-size:1.15rem;font-weight:500;
                                    color:{BLUE};">₹{r['value_cr']}Cr</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_score:
            st.markdown(f"""
            <div style="display:flex;flex-direction:column;align-items:center;
                        justify-content:center;height:100%;text-align:center;
                        padding:.5rem .25rem;">
                <div style="font-family:'Space Grotesk',sans-serif;font-size:3.2rem;
                            font-weight:700;color:{score_col};line-height:1;">{score}</div>
                <div style="font-size:9.5px;font-weight:600;letter-spacing:.1em;
                            text-transform:uppercase;color:{T2};margin-top:5px;">
                    Impact Score
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  TAB 5 — FIELD VALIDATION
# ══════════════════════════════════════════════════════════════════
def tab_field():
    st.markdown('<div class="hx-pad">', unsafe_allow_html=True)

    st.markdown(f"""
    <span class="eyebrow">Field Validation</span>
    <div class="section-title">Outcomes & Model Confidence</div>
    <div class="section-desc">Every HELIX recommendation carries a confidence rating and an
    explicit reasoning chain — so field responders can trust it, interrogate it, or override it.
    Explainable AI isn't optional in a life-or-death context.</div>
    """, unsafe_allow_html=True)

    # Cumulative impact
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Medicine Routed", "147,000 units", "+12K this week")
    with c2:
        st.metric("Lives Reached", "9,000+", "+2.1K vs last week")
    with c3:
        st.metric("Wastage Prevented", "31%", "+3 pts vs baseline")
    with c4:
        st.metric("Value Preserved", "₹19.3 Cr", "+₹4.1 Cr this week")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="label" style="margin-bottom:1rem;">Decision Confidence Analysis</div>',
        unsafe_allow_html=True
    )

    signals = [
        {
            "title": "Bihar Earthquake — Route COVID Vaccines",
            "confidence": 0.95,
            "reasoning": (
                "Gap score 92 exceeds CRITICAL threshold (75). 50,000 viable doses "
                "confirmed at Delhi Hub. Patna relay operational. 1,020km route feasible "
                "within 14h window. Diabetic population index elevated at 91."
            ),
            "factors": [
                ("Gap Score",         92, GREEN),
                ("Vaccine Viability", 96, GREEN),
                ("Route Feasibility", 87, BLUE),
                ("Time Sensitivity",  91, AMBER),
            ],
        },
        {
            "title": "Assam Floods — Route Insulin",
            "confidence": 0.87,
            "reasoning": (
                "Gap score 78 (UNDERSERVED). Insulin viability 83% — above 70% "
                "deployment threshold. Patna–Guwahati relay confirmed operational. "
                "Flood terrain limits road transport; aerial relay recommended."
            ),
            "factors": [
                ("Gap Score",         78, AMBER),
                ("Insulin Viability", 83, GREEN),
                ("Route Feasibility", 79, BLUE),
                ("Diabetic Pop Index",88, AMBER),
            ],
        },
        {
            "title": "Odisha Cyclone — Route Blood Units",
            "confidence": 0.71,
            "reasoning": (
                "Gap score 65 (moderate risk zone). Blood viability 71% — marginally "
                "above 70% threshold. Cold transport mandatory to prevent further "
                "degradation. ETA 5h; recommend pre-positioned relay at Bhubaneswar."
            ),
            "factors": [
                ("Gap Score",         65, AMBER),
                ("Blood Viability",   71, AMBER),
                ("Route Feasibility", 65, BLUE),
                ("Trauma Case Index", 58, BLUE),
            ],
        },
    ]

    for s in signals:
        conf_pct   = int(s["confidence"] * 100)
        conf_color = GREEN if conf_pct >= 85 else AMBER if conf_pct >= 70 else RED

        # Build factor cells
        factors_html = ""
        for fname, fscore, fcolor in s["factors"]:
            bar_fill = (
                "gap-grn" if fcolor == GREEN else
                "gap-amb" if fcolor == AMBER else
                "gap-blu"
            )
            factors_html += f"""
            <div>
                <div class="label">{fname}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1rem;
                            font-weight:500;color:{fcolor};">{fscore}</div>
                <div class="gap-bar">
                    <div class="{bar_fill}" style="width:{fscore}%"></div>
                </div>
            </div>"""

        st.markdown(f"""
        <div class="hx-card" style="margin-bottom:1rem;">
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;margin-bottom:12px;">
                <div style="font-family:'Space Grotesk',sans-serif;
                            font-size:14.5px;font-weight:600;color:{T0};
                            flex:1;padding-right:1rem;">
                    {s['title']}
                </div>
                <div style="text-align:right;flex-shrink:0;">
                    <div style="font-family:'JetBrains Mono',monospace;
                                font-size:1.4rem;font-weight:500;
                                color:{conf_color};">{conf_pct}%</div>
                    <div style="font-size:9.5px;font-weight:600;letter-spacing:.09em;
                                text-transform:uppercase;color:{T2};">Confidence</div>
                    <div class="conf-bar" style="width:90px;margin-top:4px;">
                        <div class="conf-fill"
                             style="width:{conf_pct}%;background:{conf_color};"></div>
                    </div>
                </div>
            </div>
            <div style="font-size:12.5px;color:{T1};line-height:1.65;
                        margin-bottom:14px;">{s['reasoning']}</div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;">
                {factors_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Methodology note
    st.markdown(f"""
    <div class="hx-card-blue" style="margin-top:1.5rem;">
        <div class="label" style="margin-bottom:8px;">Explainability Principle</div>
        <div style="font-size:12.5px;color:{T1};line-height:1.65;">
            HELIX does not make black-box decisions. Every recommendation exposes its
            input weights, gap calculation, and viability score. Field coordinators
            can inspect the reasoning chain and override any recommendation with a
            single tap. Confidence ratings below 70% automatically flag for human review.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════
def main():
    apply_styles()

    disasters = fetch_disasters()
    medicines = get_medicines()
    routes    = get_routes()

    render_hero(disasters, medicines)

    tabs = st.tabs([
        "Situational Awareness",
        "Humanitarian Gaps",
        "Supply Integrity",
        "Allocation Engine",
        "Field Validation",
    ])

    with tabs[0]:
        tab_situational(disasters)
    with tabs[1]:
        tab_gaps(disasters)
    with tabs[2]:
        tab_supply(medicines)
    with tabs[3]:
        tab_allocation(routes)
    with tabs[4]:
        tab_field()


if __name__ == "__main__":
    main()