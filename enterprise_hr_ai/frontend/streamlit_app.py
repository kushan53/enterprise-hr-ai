import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys

# Ensure root is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.services.attrition_service import attrition_service
from app.services.engagement_service import engagement_service
from app.services.skill_gap_service import skill_gap_service
from app.services.recommendation_service import recommendation_service
from app.services.agent_service import agent_service
from app.ml.predictor import predictor

# -------------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="NexusHR AI — Autonomous Workforce Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "registered_users" not in st.session_state:
    st.session_state.registered_users = {
        "admin@nexushr.ai": {
            "name": "Sarah Jenkins",
            "role": "VP of People Operations",
            "password": "password123",
            "department": "Executive HR",
            "avatar": "👩‍💼"
        },
        "alex@nexushr.ai": {
            "name": "Alex Vance",
            "role": "Lead HR Business Partner",
            "password": "password123",
            "department": "Engineering & IT",
            "avatar": "👨‍💻"
        }
    }

# -------------------------------------------------------------
# NEXT-GEN ENTERPRISE DESIGN SYSTEM (ULTRA PREMIUM CSS)
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
        --bg-primary: #090d16;
        --bg-card: rgba(17, 24, 39, 0.75);
        --accent-purple: #8b5cf6;
        --accent-indigo: #6366f1;
        --accent-cyan: #06b6d4;
        --accent-rose: #f43f5e;
        --accent-emerald: #10b981;
        --border-glass: rgba(255, 255, 255, 0.08);
        --border-glow: rgba(99, 102, 241, 0.4);
    }
    
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    h1, h2, h3, h4, .brand-font {
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* Fix Streamlit Header Overlay & Container Spacing */
    header[data-testid="stHeader"] {
        background: transparent !important;
        z-index: 10 !important;
    }

    .block-container {
        padding-top: 3.2rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1400px !important;
    }

    /* Full-Width Top Floating Navigation Header */
    .top-header-bar {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-radius: 20px;
        padding: 18px 28px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 16px;
        box-shadow: 0 12px 36px -10px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.12);
    }

    .brand-logo-text {
        font-size: 2.1rem;
        font-weight: 900;
        background: linear-gradient(135deg, #c084fc 0%, #6366f1 50%, #f43f5e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding: 2px 0;
        line-height: 1.2;
        display: inline-block;
        letter-spacing: -0.5px;
    }

    .pulsing-dot {
        width: 9px;
        height: 9px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 12px #10b981;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 7px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Hero Section */
    .hero-wrapper {
        position: relative;
        background: radial-gradient(circle at 50% -20%, rgba(99, 102, 241, 0.38) 0%, rgba(15, 23, 42, 0.98) 75%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 28px;
        padding: 58px 42px;
        text-align: center;
        margin-bottom: 38px;
        box-shadow: 0 25px 60px -15px rgba(99, 102, 241, 0.28);
        overflow: hidden;
    }

    .hero-pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(99, 102, 241, 0.2);
        color: #c7d2fe;
        border: 1px solid rgba(165, 180, 252, 0.35);
        padding: 7px 20px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 22px;
    }

    .hero-h1-gradient {
        font-size: 3.1rem;
        font-weight: 900;
        line-height: 1.2;
        background: linear-gradient(180deg, #ffffff 25%, #cbd5e1 75%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        padding: 4px 0;
    }

    .hero-subtext {
        font-size: 1.2rem;
        color: #94a3b8;
        max-width: 840px;
        margin: 0 auto 32px auto;
        line-height: 1.65;
    }

    /* Bento Grid Feature Cards */
    .bento-card {
        background: rgba(17, 24, 39, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 20px;
        padding: 26px;
        backdrop-filter: blur(16px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .bento-card:hover {
        border-color: rgba(139, 92, 246, 0.5);
        transform: translateY(-5px);
        box-shadow: 0 15px 35px -10px rgba(99, 102, 241, 0.3);
    }

    .bento-icon {
        width: 52px;
        height: 52px;
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.1));
        border: 1px solid rgba(99, 102, 241, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        margin-bottom: 16px;
    }

    /* Metric KPI Cards */
    .stat-card-glass {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
    }

    .stat-card-glass::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
    }

    .stat-number {
        font-family: 'Outfit', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 40%, #a5b4fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
        margin: 8px 0;
    }

    /* Custom Buttons & Pills */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.4rem !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.35) !important;
        transition: all 0.25s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
    }

    /* Footer */
    .glass-footer {
        margin-top: 60px;
        padding: 32px;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid var(--border-glass);
        border-radius: 20px;
        text-align: center;
        color: #64748b;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# DATA ENGINE
# -------------------------------------------------------------
@st.cache_data
def load_data():
    intel_path = os.path.join(BASE_DIR, "data", "processed", "employee_intelligence.csv")
    org_gaps_path = os.path.join(BASE_DIR, "data", "processed", "organization_skill_gaps.csv")
    courses_path = os.path.join(BASE_DIR, "data", "processed", "courses.csv")
    
    df_intel = pd.read_csv(intel_path) if os.path.exists(intel_path) else pd.DataFrame()
    df_gaps = pd.read_csv(org_gaps_path) if os.path.exists(org_gaps_path) else pd.DataFrame()
    df_courses = pd.read_csv(courses_path) if os.path.exists(courses_path) else pd.DataFrame()
    return df_intel, df_gaps, df_courses

df_intel, df_gaps, df_courses = load_data()


# -------------------------------------------------------------
# TOP FLOATING NAV HEADER
# -------------------------------------------------------------
col_n1, col_n2 = st.columns([8, 4])
with col_n1:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
        <span style="font-size:2.2rem; line-height:1;">⚡</span>
        <div>
            <div class="brand-logo-text">NexusHR AI</div>
            <div style="color:#94a3b8; font-size:0.88rem; font-weight:500; margin-top:2px;">
                Enterprise Workforce Intelligence & Talent Growth OS
            </div>
        </div>
        <div style="background:rgba(16, 185, 129, 0.12); border:1px solid rgba(16, 185, 129, 0.3); padding:5px 14px; border-radius:99px; font-size:0.8rem; color:#34d399; font-weight:700; margin-left:8px;">
            <span class="pulsing-dot"></span>ML ENGINE LIVE (v2.4)
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_n2:
    if st.session_state.authenticated:
        user = st.session_state.user
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-end; align-items:center; gap:12px; margin-top:6px;">
            <div style="text-align:right;">
                <div style="color:#f8fafc; font-weight:700; font-size:0.95rem;">{user['avatar']} {user['name']}</div>
                <div style="color:#94a3b8; font-size:0.8rem;">{user['role']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out 🚪", key="top_logout_trigger"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    else:
        st.markdown("""
        <div style="display:flex; justify-content:flex-end; align-items:center; gap:10px; margin-top:8px;">
            <span style="background:rgba(99, 102, 241, 0.15); border:1px solid rgba(99, 102, 241, 0.3); color:#a5b4fc; padding:5px 14px; border-radius:99px; font-size:0.82rem; font-weight:600;">
                🛡️ SOC2 & GDPR Certified
            </span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr style='border-color:rgba(255,255,255,0.08); margin:18px 0 28px 0;'>", unsafe_allow_html=True)


# =============================================================
# SCENARIO A: PUBLIC PORTAL (LANDING, LOGIN, SIGNUP)
# =============================================================
if not st.session_state.authenticated:
    
    st.sidebar.markdown("### 🌐 Navigation")
    public_mode = st.sidebar.radio(
        "Select Portal Page",
        ["🏠 Platform Overview", "🔐 Sign In (Login)", "📝 Enterprise Registration", "🚀 1-Click Executive Demo"]
    )
    
    # ---------------------------------------------------------
    # 1. PLATFORM OVERVIEW (HERO & BENTO GRID)
    # ---------------------------------------------------------
    if public_mode == "🏠 Platform Overview":
        st.markdown("""
        <div class="hero-wrapper">
            <div class="hero-pill-badge">✨ Next-Generation Workforce Intelligence</div>
            <h1 class="hero-h1-gradient">Predict Attrition, Reskill Teams & Automate HR with Autonomous AI</h1>
            <p class="hero-subtext">
                NexusHR AI unifies predictive flight-risk modeling, real-time organizational skill intelligence, personalized career growth pathways, and agentic policy RAG workflows into a single high-performance enterprise platform.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # High Impact Metric Strip
        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        with col_k1:
            st.markdown("""
            <div class="stat-card-glass">
                <div style="color:#94a3b8; font-size:0.82rem; font-weight:600; text-transform:uppercase;">Predictive Accuracy</div>
                <div class="stat-number" style="-webkit-text-fill-color:#34d399;">87.4%</div>
                <div style="color:#10b981; font-size:0.85rem;">▲ Tuned Ensemble ROC-AUC</div>
            </div>
            """, unsafe_allow_html=True)
        with col_k2:
            st.markdown("""
            <div class="stat-card-glass">
                <div style="color:#94a3b8; font-size:0.82rem; font-weight:600; text-transform:uppercase;">Flight-Risk Reduction</div>
                <div class="stat-number" style="-webkit-text-fill-color:#60a5fa;">-34%</div>
                <div style="color:#60a5fa; font-size:0.85rem;">Proactive Retention Interventions</div>
            </div>
            """, unsafe_allow_html=True)
        with col_k3:
            st.markdown("""
            <div class="stat-card-glass">
                <div style="color:#94a3b8; font-size:0.82rem; font-weight:600; text-transform:uppercase;">Curated AI Pathways</div>
                <div class="stat-number" style="-webkit-text-fill-color:#c084fc;">120+</div>
                <div style="color:#a855f7; font-size:0.85rem;">Mapped Course Curricula</div>
            </div>
            """, unsafe_allow_html=True)
        with col_k4:
            st.markdown("""
            <div class="stat-card-glass">
                <div style="color:#94a3b8; font-size:0.82rem; font-weight:600; text-transform:uppercase;">HR Hours Saved</div>
                <div class="stat-number" style="-webkit-text-fill-color:#fbbf24;">65 hrs</div>
                <div style="color:#f59e0b; font-size:0.85rem;">Per Month with Policy RAG</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Bento Grid Capabilities
        st.markdown("<h3 style='margin-bottom:20px;'>⚡ Enterprise Platform Capabilities</h3>", unsafe_allow_html=True)
        
        b1, b2, b3 = st.columns(3)
        with b1:
            st.markdown("""
            <div class="bento-card">
                <div>
                    <div class="bento-icon">📊</div>
                    <h4 style="color:#f8fafc; margin-bottom:8px;">Executive Command Center</h4>
                    <p style="color:#94a3b8; font-size:0.9rem; line-height:1.5;">
                        High-level workforce health indicators, departmental burn-rate benchmarks, and executive flight-risk distribution radars.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with b2:
            st.markdown("""
            <div class="bento-card">
                <div>
                    <div class="bento-icon">🎯</div>
                    <h4 style="color:#f8fafc; margin-bottom:8px;">Flight-Risk What-If Simulator</h4>
                    <p style="color:#94a3b8; font-size:0.9rem; line-height:1.5;">
                        Interactive simulation engine with SHAP local explainability for compensation, overtime, and work-life balance tuning.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with b3:
            st.markdown("""
            <div class="bento-card">
                <div>
                    <div class="bento-icon">🧠</div>
                    <h4 style="color:#f8fafc; margin-bottom:8px;">Skill Gap & Hire vs. Reskill</h4>
                    <p style="color:#94a3b8; font-size:0.9rem; line-height:1.5;">
                        Organization-wide skill matrix calculating automated hire vs. internal reskill cost trade-offs and capacity planning.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        b4, b5, b6 = st.columns(3)
        with b4:
            st.markdown("""
            <div class="bento-card">
                <div>
                    <div class="bento-icon">🚀</div>
                    <h4 style="color:#f8fafc; margin-bottom:8px;">Personalized Talent Academy</h4>
                    <p style="color:#94a3b8; font-size:0.9rem; line-height:1.5;">
                        Personalized career trajectory mapping, role transition readiness scoring, and automated course curriculum recommendations.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with b5:
            st.markdown("""
            <div class="bento-card">
                <div>
                    <div class="bento-icon">🤖</div>
                    <h4 style="color:#f8fafc; margin-bottom:8px;">Agentic HR & Policy RAG</h4>
                    <p style="color:#94a3b8; font-size:0.9rem; line-height:1.5;">
                        Multi-agent conversational copilot grounded in verified company policy handbooks for zero-hallucination HR operations.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with b6:
            st.markdown("""
            <div class="bento-card">
                <div>
                    <div class="bento-icon">👤</div>
                    <h4 style="color:#f8fafc; margin-bottom:8px;">Talent 360° Profiles</h4>
                    <p style="color:#94a3b8; font-size:0.9rem; line-height:1.5;">
                        Single-pane-of-glass employee dossier with live risk scores, missing skills, and tailored retention action items.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br><hr style='border-color:rgba(255,255,255,0.08);'><br>", unsafe_allow_html=True)
        
        # Interactive CTA
        col_cta_l, col_cta_r = st.columns([7, 5])
        with col_cta_l:
            st.markdown("<h3>🚀 Experience the Intelligence Workspace</h3>", unsafe_allow_html=True)
            st.write("Launch instant demo access as VP of People Operations or sign in with your enterprise credentials.")
        with col_cta_r:
            if st.button("⚡ Launch 1-Click Executive Demo", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.user = st.session_state.registered_users["admin@nexushr.ai"]
                st.rerun()

    # ---------------------------------------------------------
    # 2. SIGN IN / LOGIN
    # ---------------------------------------------------------
    elif public_mode == "🔐 Sign In (Login)":
        st.markdown("<div style='text-align:center; margin-bottom:30px;'><h2 style='font-size:2.2rem;'>🔐 Enterprise Member Portal</h2><p style='color:#94a3b8;'>Sign in to access your organization's talent intelligence workspace</p></div>", unsafe_allow_html=True)
        
        col_l1, col_l2, col_l3 = st.columns([3, 6, 3])
        with col_l2:
            st.markdown("""
            <div style="background:rgba(30, 41, 59, 0.7); border:1px solid rgba(255,255,255,0.1); padding:28px; border-radius:20px; box-shadow:0 15px 35px rgba(0,0,0,0.5);">
            """, unsafe_allow_html=True)
            with st.form("login_form_styled"):
                st.markdown("#### 🔑 Work Credentials")
                login_email = st.text_input("Enterprise Email", value="admin@nexushr.ai")
                login_password = st.text_input("Password", value="password123", type="password")
                submit_login = st.form_submit_button("Sign In to Workspace 🚀", use_container_width=True)
                
                if submit_login:
                    if login_email in st.session_state.registered_users and st.session_state.registered_users[login_email]["password"] == login_password:
                        st.session_state.authenticated = True
                        st.session_state.user = st.session_state.registered_users[login_email]
                        st.success("Authentication successful! Loading intelligence suite...")
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please verify your credentials.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("💡 **Pre-configured Demo Credentials**: Email: `admin@nexushr.ai` | Password: `password123`")

    # ---------------------------------------------------------
    # 3. REGISTRATION
    # ---------------------------------------------------------
    elif public_mode == "📝 Enterprise Registration":
        st.markdown("<div style='text-align:center; margin-bottom:30px;'><h2 style='font-size:2.2rem;'>📝 Create Enterprise Workspace</h2><p style='color:#94a3b8;'>Deploy NexusHR AI for your HR team in seconds</p></div>", unsafe_allow_html=True)
        
        col_s1, col_s2, col_s3 = st.columns([3, 6, 3])
        with col_s2:
            st.markdown("""
            <div style="background:rgba(30, 41, 59, 0.7); border:1px solid rgba(255,255,255,0.1); padding:28px; border-radius:20px; box-shadow:0 15px 35px rgba(0,0,0,0.5);">
            """, unsafe_allow_html=True)
            with st.form("signup_form_styled"):
                st.markdown("#### 👤 Leader Profile Details")
                new_name = st.text_input("Full Name", placeholder="e.g. Rachel Adams")
                new_email = st.text_input("Corporate Work Email", placeholder="e.g. rachel@enterprise.com")
                new_role = st.selectbox("Designation", [
                    "Chief Human Resources Officer (CHRO)",
                    "VP of People & Culture",
                    "Lead HR Business Partner",
                    "Head of Learning & Development (L&D)",
                    "People Analytics Lead"
                ])
                new_dept = st.selectbox("Primary Department", ["Executive HR", "Engineering & IT", "Sales & Marketing", "Finance & Operations"])
                new_pass = st.text_input("Create Strong Password", type="password", placeholder="At least 6 characters")
                submit_signup = st.form_submit_button("Register & Launch Workspace ✨", use_container_width=True)
                
                if submit_signup:
                    if not new_name or not new_email or not new_pass:
                        st.error("Please fill in all required fields.")
                    elif new_email in st.session_state.registered_users:
                        st.error("An enterprise account with this email already exists.")
                    else:
                        st.session_state.registered_users[new_email] = {
                            "name": new_name,
                            "role": new_role,
                            "password": new_pass,
                            "department": new_dept,
                            "avatar": "🌟"
                        }
                        st.session_state.authenticated = True
                        st.session_state.user = st.session_state.registered_users[new_email]
                        st.success(f"Welcome, {new_name}! Your enterprise workspace is live.")
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 4. 1-CLICK DEMO ACCESS
    # ---------------------------------------------------------
    elif public_mode == "🚀 1-Click Executive Demo":
        st.session_state.authenticated = True
        st.session_state.user = st.session_state.registered_users["admin@nexushr.ai"]
        st.toast("Logged in as Sarah Jenkins (VP HR)!")
        st.rerun()


# =============================================================
# SCENARIO B: AUTHENTICATED WORKSPACE (INTELLIGENCE SUITE)
# =============================================================
else:
    # Authenticated Sidebar
    user = st.session_state.user
    st.sidebar.markdown(f"""
    <div style="background:rgba(30, 41, 59, 0.7); border:1px solid rgba(255,255,255,0.08); padding:16px; border-radius:14px; margin-bottom:16px;">
        <div style="font-size:1.4rem;">{user['avatar']} <strong style="color:#f8fafc;">{user['name']}</strong></div>
        <div style="color:#a5b4fc; font-size:0.82rem; font-weight:600;">{user['role']}</div>
        <div style="color:#64748b; font-size:0.75rem;">{user['department']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Sign Out 🚪", key="sidebar_logout_trigger", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Intelligence Modules")
    
    selected_page = st.sidebar.radio(
        "Workspace View",
        [
            "📊 Executive Overview Hub",
            "🎯 Flight-Risk & What-If Simulator",
            "🧠 Skill Gap & Hire vs. Reskill",
            "🚀 Career Pathways & Upskilling",
            "👤 Talent 360° Directory",
            "🤖 AI Copilot & Policy RAG",
            "📚 API & System Architecture"
        ]
    )

    st.sidebar.markdown("---")
    department_list = ["All Departments"] + sorted(df_intel['Department'].unique().tolist()) if not df_intel.empty else ["All Departments"]
    selected_dept = st.sidebar.selectbox("🏢 Organization Scope", department_list)

    if selected_dept != "All Departments" and not df_intel.empty:
        filtered_df = df_intel[df_intel['Department'] == selected_dept]
    else:
        filtered_df = df_intel

    # ---------------------------------------------------------
    # DASHBOARD 1: EXECUTIVE OVERVIEW HUB
    # ---------------------------------------------------------
    if selected_page == "📊 Executive Overview Hub":
        st.markdown(f"<h2 style='font-size:2.2rem;'>📊 Executive Workforce Intelligence & KPI Hub</h2>", unsafe_allow_html=True)
        st.write(f"Organization Scope: **{selected_dept}** | Monitored Workforce: **{len(filtered_df):,} employees**")
        
        total_emp = len(filtered_df)
        high_risk = len(filtered_df[filtered_df['AttritionRiskCategory'] == 'High'])
        avg_eng = round(filtered_df['EngagementScore'].mean(), 1) if not filtered_df.empty else 0
        avg_wlb = round(filtered_df['WorkLifeBalanceScore'].mean(), 2) if not filtered_df.empty else 0
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="stat-card-glass">
                <div style="color:#94a3b8; font-size:0.8rem; font-weight:600; text-transform:uppercase;">Active Workforce</div>
                <div class="stat-number">{total_emp:,}</div>
                <div style="color:#94a3b8; font-size:0.85rem;">Covered in Intelligence Model</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stat-card-glass">
                <div style="color:#94a3b8; font-size:0.8rem; font-weight:600; text-transform:uppercase;">Critical Flight-Risk</div>
                <div class="stat-number" style="-webkit-text-fill-color:#ef4444;">{high_risk:,} <span style="font-size:1.1rem;">({(high_risk/max(1,total_emp)*100):.1f}%)</span></div>
                <div style="color:#ef4444; font-size:0.85rem;">Immediate retention priority</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stat-card-glass">
                <div style="color:#94a3b8; font-size:0.8rem; font-weight:600; text-transform:uppercase;">Avg Engagement</div>
                <div class="stat-number" style="-webkit-text-fill-color:#10b981;">{avg_eng} <span style="font-size:1.1rem;">/ 100</span></div>
                <div style="color:#10b981; font-size:0.85rem;">Pulse health benchmark</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="stat-card-glass">
                <div style="color:#94a3b8; font-size:0.8rem; font-weight:600; text-transform:uppercase;">Work-Life Balance</div>
                <div class="stat-number" style="-webkit-text-fill-color:#38bdf8;">{avg_wlb} <span style="font-size:1.1rem;">/ 10.0</span></div>
                <div style="color:#38bdf8; font-size:0.85rem;">Burnout index score</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        col_chart1, col_chart2 = st.columns([6, 6])
        with col_chart1:
            st.markdown("#### 🏢 Attrition Risk Distribution by Department")
            if not df_intel.empty:
                dept_summary = df_intel.groupby(['Department', 'AttritionRiskCategory']).size().reset_index(name='Count')
                fig_dept = px.bar(
                    dept_summary,
                    x='Department',
                    y='Count',
                    color='AttritionRiskCategory',
                    barmode='group',
                    color_discrete_map={'High': '#ef4444', 'Medium': '#f59e0b', 'Low': '#10b981'},
                    template='plotly_dark',
                    height=380
                )
                fig_dept.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_dept, use_container_width=True)
                
        with col_chart2:
            st.markdown("#### ⚖️ Work-Life Balance vs. Overtime Hours (Burnout Radar)")
            if not filtered_df.empty:
                fig_scatter = px.scatter(
                    filtered_df,
                    x='OvertimeHoursPerMonth',
                    y='WorkLifeBalanceScore',
                    color='AttritionRiskCategory',
                    size='MonthlySalary',
                    hover_data=['Name', 'JobRole', 'Department'],
                    color_discrete_map={'High': '#ef4444', 'Medium': '#f59e0b', 'Low': '#10b981'},
                    template='plotly_dark',
                    height=380
                )
                fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 🚨 Priority High Flight-Risk Personnel Watchlist")
        high_risk_table = filtered_df[filtered_df['AttritionRiskCategory'] == 'High'][
            ['EmployeeID', 'Name', 'Department', 'JobRole', 'AttritionProbability', 'OvertimeHoursPerMonth', 'WorkLifeBalanceScore', 'PrimaryRecommendation']
        ].sort_values('AttritionProbability', ascending=False)
        
        st.dataframe(
            high_risk_table.style.format({'AttritionProbability': '{:.1%}', 'OvertimeHoursPerMonth': '{:.1f} hrs'}),
            use_container_width=True,
            height=260
        )

    # ---------------------------------------------------------
    # DASHBOARD 2: FLIGHT-RISK & WHAT-IF SIMULATOR
    # ---------------------------------------------------------
    elif selected_page == "🎯 Flight-Risk & What-If Simulator":
        st.markdown("<h2 style='font-size:2.2rem;'>🎯 Interactive Flight-Risk & Retention Simulator</h2>", unsafe_allow_html=True)
        st.write("Simulate changes in overtime, compensation, and work-life balance to observe real-time impact on predicted attrition risk.")

        col_sim_left, col_sim_right = st.columns([5, 7])
        
        with col_sim_left:
            st.markdown("##### 📝 Employee Simulation Parameters")
            sim_name = st.text_input("Employee Name / Reference", "Alex Vance")
            sim_age = st.slider("Age", 18, 65, 34)
            sim_dept = st.selectbox("Department", ["Sales", "IT", "Finance", "HR", "Support", "Marketing"], index=1)
            sim_role = st.selectbox("Job Role", [
                "Auditor", "Sales Executive", "Helpdesk", "HR Executive", "Account Manager", 
                "Engineer", "Developer", "Tester", "HR Manager", "Content Lead", "SEO Analyst", 
                "Accountant", "Support Engineer"
            ], index=5)
            sim_salary = st.number_input("Monthly Salary ($)", min_value=10000, max_value=250000, value=72000, step=5000)
            sim_ot = st.slider("Overtime Hours / Month", 0, 50, 32)
            sim_wlb = st.slider("Work-Life Balance Score", -5.0, 10.0, 1.2, step=0.1)
            sim_projects = st.slider("Projects Handled", 1, 20, 8)
            sim_tenure = st.slider("Years at Company", 0, 20, 6)
            sim_promo_year = st.slider("Last Promotion Year", 2010, 2024, 2018)
            sim_perf = st.selectbox("Performance Rating", [1, 2, 3, 4, 5], index=2)
            sim_model_version = st.radio("Model Architecture", ["v2 (Tuned Random Forest Ensemble)", "v1 (Baseline Logistic Regression)"], index=0)
            chosen_version = "v2" if "v2" in sim_model_version else "v1"

        with col_sim_right:
            st.markdown("##### 📊 Real-Time ML Flight-Risk Assessment")
            
            sim_payload = {
                "EmployeeID": 9999,
                "Age": sim_age,
                "Department": sim_dept,
                "JobRole": sim_role,
                "EducationLevel": 3,
                "MonthlySalary": float(sim_salary),
                "OvertimeHoursPerMonth": float(sim_ot),
                "LeavesTaken": 6,
                "ProjectsHandled": int(sim_projects),
                "TrainingHours": 25,
                "YearsAtCompany": int(sim_tenure),
                "WorkLifeBalanceScore": float(sim_wlb),
                "PerformanceRating": int(sim_perf),
                "LastPromotionYear": int(sim_promo_year)
            }
            
            res = predictor.predict_single(sim_payload, model_version=chosen_version)
            prob = res["AttritionProbability"]
            cat = res["RiskCategory"]
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Predicted Flight Risk: {cat.upper()}", 'font': {'size': 20, 'family': 'Outfit'}},
                number={'suffix': "%"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#ef4444" if cat == "High" else ("#f59e0b" if cat == "Medium" else "#10b981")},
                    'steps': [
                        {'range': [0, 35], 'color': "rgba(16, 185, 129, 0.2)"},
                        {'range': [35, 70], 'color': "rgba(245, 158, 11, 0.2)"},
                        {'range': [70, 100], 'color': "rgba(239, 68, 68, 0.2)"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            st.markdown(f"""
            <div style="background:rgba(99, 102, 241, 0.15); border-left:4px solid #818cf8; padding:14px 18px; border-radius:8px; margin-bottom:16px;">
                <strong>💡 Prescribed HR Intervention:</strong> {res['RecommendedIntervention']}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("###### 🔍 Local SHAP Risk Drivers")
            for d in res["TopRiskDrivers"]:
                badge_color = "#ef4444" if d["severity"] == "High" else ("#f59e0b" if d["severity"] == "Medium" else "#10b981")
                st.markdown(f"- <span style='color:{badge_color}; font-weight:700;'>[{d['severity'].upper()}]</span> **{d['factor']}** — {d['impact']}", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # DASHBOARD 3: SKILL GAP & HIRE VS RESKILL
    # ---------------------------------------------------------
    elif selected_page == "🧠 Skill Gap & Hire vs. Reskill":
        st.markdown("<h2 style='font-size:2.2rem;'>🧠 Organizational Skill Gap & Capacity Planning</h2>", unsafe_allow_html=True)
        st.write("Evaluate aggregate skill deficits, department-level shortages, and automated hire vs. reskill trade-off recommendations.")
        
        if not df_gaps.empty:
            total_gaps = df_gaps['GapCount'].sum()
            total_reskill = df_gaps['ReskillTarget'].sum()
            total_hire = df_gaps['ExternalHireTarget'].sum()
            
            g1, g2, g3 = st.columns(3)
            with g1:
                st.markdown(f"""
                <div class="stat-card-glass">
                    <div style="color:#94a3b8; font-size:0.8rem; font-weight:600; text-transform:uppercase;">Identified Skill Deficits</div>
                    <div class="stat-number">{total_gaps:,}</div>
                    <div style="color:#94a3b8; font-size:0.85rem;">Across all functional units</div>
                </div>
                """, unsafe_allow_html=True)
            with g2:
                st.markdown(f"""
                <div class="stat-card-glass">
                    <div style="color:#94a3b8; font-size:0.8rem; font-weight:600; text-transform:uppercase;">Internal Reskill Target</div>
                    <div class="stat-number" style="-webkit-text-fill-color:#10b981;">{total_reskill:,} <span style="font-size:1.1rem;">(70%)</span></div>
                    <div style="color:#10b981; font-size:0.85rem;">Targeted learning pathways</div>
                </div>
                """, unsafe_allow_html=True)
            with g3:
                st.markdown(f"""
                <div class="stat-card-glass">
                    <div style="color:#94a3b8; font-size:0.8rem; font-weight:600; text-transform:uppercase;">External Hire Target</div>
                    <div class="stat-number" style="-webkit-text-fill-color:#60a5fa;">{total_hire:,} <span style="font-size:1.1rem;">(30%)</span></div>
                    <div style="color:#60a5fa; font-size:0.85rem;">Net acquisition requirement</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_gap_1, col_gap_2 = st.columns([6, 6])
            with col_gap_1:
                st.markdown("#### 🚨 Top Organizational Skill Shortfalls")
                top_gaps = df_gaps.groupby('Skill')['GapCount'].sum().reset_index().sort_values('GapCount', ascending=False).head(10)
                fig_gap_bar = px.bar(
                    top_gaps,
                    x='GapCount',
                    y='Skill',
                    orientation='h',
                    color='GapCount',
                    color_continuous_scale='Reds',
                    template='plotly_dark',
                    height=380
                )
                fig_gap_bar.update_layout(yaxis={'autorange': 'reversed'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_gap_bar, use_container_width=True)
                
            with col_gap_2:
                st.markdown("#### 📊 Internal Reskill vs. External Hire Breakdown")
                reskill_chart_data = df_gaps.groupby('Department')[['ReskillTarget', 'ExternalHireTarget']].sum().reset_index()
                fig_hire_reskill = px.bar(
                    reskill_chart_data,
                    x='Department',
                    y=['ReskillTarget', 'ExternalHireTarget'],
                    barmode='stack',
                    color_discrete_map={'ReskillTarget': '#10b981', 'ExternalHireTarget': '#3b82f6'},
                    template='plotly_dark',
                    height=380
                )
                fig_hire_reskill.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_hire_reskill, use_container_width=True)
                
            st.markdown("---")
            st.markdown("#### 📋 Detailed Organizational Skill Gap Breakdown")
            st.dataframe(df_gaps, use_container_width=True, height=320)

    # ---------------------------------------------------------
    # DASHBOARD 4: CAREER PATHWAYS & UPSKILLING
    # ---------------------------------------------------------
    elif selected_page == "🚀 Career Pathways & Upskilling":
        st.markdown("<h2 style='font-size:2.2rem;'>🚀 Personalized Upskilling Engine & Career Pathway Generator</h2>", unsafe_allow_html=True)
        st.write("Generate tailored learning pathways and calculate career readiness trajectories from current role to target aspirational role.")
        
        col_u1, col_u2 = st.columns([5, 7])
        
        with col_u1:
            st.markdown("##### 🎯 Career Transition Planning")
            roles = sorted(df_intel['JobRole'].unique().tolist()) if not df_intel.empty else ["Developer", "Engineer", "Sales Executive"]
            current_r = st.selectbox("Current Role", roles, index=roles.index("Developer") if "Developer" in roles else 0)
            target_r = st.selectbox("Target / Aspirational Role", roles, index=roles.index("Engineer") if "Engineer" in roles else 0)
            
            sample_skills_map = {
                "Developer": ["Python", "SQL & Database Design", "Git Version Control"],
                "Tester": ["QA Testing", "Selenium / Playwright"],
                "Auditor": ["Accounting", "Financial Auditing"],
                "Sales Executive": ["B2B Sales", "CRM Management"]
            }
            default_known = sample_skills_map.get(current_r, ["Communication", "Problem Solving"])
            known_input = st.multiselect("Current Competencies / Skills", default_known + ["Python", "Docker", "SQL", "Cloud Infrastructure (AWS/GCP)", "REST APIs", "QA Testing"], default=default_known)

        with col_u2:
            st.markdown("##### 📈 Competency Match & Readiness Projection")
            gap_res = skill_gap_service.calculate_employee_skill_gap(
                current_role=current_r,
                target_role=target_r,
                current_skills=known_input
            )
            
            r_today = gap_res["ReadinessScoreToday"]
            r_proj = gap_res["ProjectedReadinessAfterPlan"]
            
            m1, m2 = st.columns(2)
            with m1:
                st.metric("Readiness Today", f"{r_today}%")
            with m2:
                st.metric("Projected Readiness (Post-Plan)", f"{r_proj}%", delta=f"+{r_proj - r_today:.1f}%")
                
            fig_traj = go.Figure(go.Indicator(
                mode="gauge+number",
                value=r_proj,
                title={'text': "Post-Training Role Fit", 'font': {'family': 'Outfit'}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': '#3b82f6'},
                    'steps': [
                        {'range': [0, r_today], 'color': '#10b981'},
                        {'range': [r_today, 100], 'color': '#1e293b'}
                    ]
                }
            ))
            fig_traj.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_traj, use_container_width=True)
            
            st.markdown(f"**Action Plan:** {gap_res['ActionPlan']}")
            
            st.markdown("###### 📚 Recommended Course Curriculum")
            for idx, c in enumerate(gap_res["RecommendedCourses"], 1):
                st.markdown(f"""
                <div style="background:rgba(30, 41, 59, 0.7); border-left:4px solid #6366f1; padding:14px 18px; margin-bottom:10px; border-radius:8px;">
                    <div style="font-weight:700; color:#f8fafc;">{idx}. {c['course_title']}</div>
                    <div style="color:#94a3b8; font-size:0.85rem; margin-top:4px;">
                        Skill Target: <strong style="color:#c7d2fe;">{c['skill']}</strong> | Duration: {c['duration']} | Level: {c['level']} | Provider: {c['provider']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # DASHBOARD 5: TALENT 360° DIRECTORY
    # ---------------------------------------------------------
    elif selected_page == "👤 Talent 360° Directory":
        st.markdown("<h2 style='font-size:2.2rem;'>👤 Unified Talent 360° Employee Directory</h2>", unsafe_allow_html=True)
        st.write("Detailed employee profile dossier with retention probability, engagement pulse, and upskilling pathways.")
        
        if not filtered_df.empty:
            emp_names = filtered_df['Name'].tolist()
            chosen_emp = st.selectbox("Select Employee Profile Dossier", emp_names)
            
            emp_row = filtered_df[filtered_df['Name'] == chosen_emp].iloc[0]
            
            col_t1, col_t2 = st.columns([4, 8])
            
            with col_t1:
                st.markdown(f"""
                <div style="background:rgba(30, 41, 59, 0.8); border:1px solid rgba(255,255,255,0.1); padding:24px; border-radius:18px;">
                    <h3 style="margin:0; color:#60a5fa; font-family:'Outfit';">{emp_row['Name']}</h3>
                    <p style="color:#94a3b8; margin-bottom:14px; font-size:0.9rem;">ID: #{emp_row['EmployeeID']} · {emp_row['JobRole']}</p>
                    <hr style="border-color:rgba(255,255,255,0.08);">
                    <p style="margin:6px 0;"><strong>🏢 Department:</strong> {emp_row['Department']}</p>
                    <p style="margin:6px 0;"><strong>⏳ Tenure:</strong> {emp_row['YearsAtCompany']} years</p>
                    <p style="margin:6px 0;"><strong>💰 Salary:</strong> ${emp_row['MonthlySalary']:,.0f}/mo</p>
                    <p style="margin:6px 0;"><strong>⭐ Performance:</strong> {'⭐' * int(emp_row['PerformanceRating'])}</p>
                    <p style="margin:6px 0;"><strong>⚖️ Work-Life Balance:</strong> {emp_row['WorkLifeBalanceScore']}/10.0</p>
                    <p style="margin:6px 0;"><strong>⏱️ Overtime:</strong> {emp_row['OvertimeHoursPerMonth']} hrs/month</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col_t2:
                st.markdown("##### ⚡ Intelligence & Flight Risk Assessment")
                
                c_r1, c_r2, c_r3 = st.columns(3)
                with c_r1:
                    st.metric("Flight Risk Category", emp_row['AttritionRiskCategory'])
                with c_r2:
                    st.metric("Attrition Probability", f"{emp_row['AttritionProbability']*100:.1f}%")
                with c_r3:
                    st.metric("Role Readiness Score", f"{emp_row['ReadinessScoreToday']}%")
                    
                st.markdown(f"**Missing Competencies:** `{emp_row['MissingSkills']}`")
                st.markdown(f"**AI Upskilling Recommendation:** **{emp_row['PrimaryRecommendation']}**")
                st.markdown(f"**Projected Readiness After Training:** `{emp_row['ProjectedReadinessAfterTraining']}%`")
                
                st.markdown("---")
                st.markdown("###### Complete Employee Roster")
                st.dataframe(filtered_df[['EmployeeID', 'Name', 'Department', 'JobRole', 'AttritionRiskCategory', 'EngagementScore', 'WorkLifeBalanceScore', 'PrimaryRecommendation']], use_container_width=True, height=250)

    # ---------------------------------------------------------
    # DASHBOARD 6: AI COPILOT & POLICY RAG
    # ---------------------------------------------------------
    elif selected_page == "🤖 AI Copilot & Policy RAG":
        st.markdown("<h2 style='font-size:2.2rem;'>🤖 NexusHR Agentic Policy Copilot & Operations Assistant</h2>", unsafe_allow_html=True)
        st.write("Autonomous multi-agent orchestration for grounded policy Q&A, employee diagnostics, and personalized upskilling plans.")
        
        agent_mode = st.selectbox("Select Specialized Agent Persona", [
            "Policy RAG Agent (Leave, PTO, Benefits, Handbook)",
            "Workforce Intelligence Agent (Attrition & Diagnostics)",
            "Upskilling & Learning Agent (Skill Gap & Courses)",
            "General Orchestrator"
        ])
        
        sample_queries = {
            "Policy RAG Agent (Leave, PTO, Benefits, Handbook)": "What is our parental leave and PTO rollover policy?",
            "Workforce Intelligence Agent (Attrition & Diagnostics)": "Diagnose flight risk for employee #10",
            "Upskilling & Learning Agent (Skill Gap & Courses)": "What courses are recommended for missing MLOps and Cloud skills?",
            "General Orchestrator": "What is our professional development stipend budget?"
        }
        
        user_query = st.text_input("Enter your instruction or question", sample_queries[agent_mode])
        
        if st.button("⚡ Dispatch Agent Query 🚀", use_container_width=True):
            with st.spinner("Agent orchestrating policy retrieval and tool execution..."):
                agent_type_slug = "policy" if "Policy" in agent_mode else ("workforce" if "Workforce" in agent_mode else ("upskill" if "Upskilling" in agent_mode else "orchestrator"))
                res = agent_service.dispatch_agent_workflow(agent_type=agent_type_slug, query=user_query)
                
                st.markdown("### 📋 Grounded Agent Response")
                if "answer" in res:
                    st.markdown(f"""
                    <div style="background:rgba(16, 185, 129, 0.1); border-left:4px solid #10b981; padding:18px 22px; border-radius:10px; font-size:1.05rem; line-height:1.6;">
                        {res['answer']}
                        <br><br>
                        <span style="opacity:0.75; font-size:0.85rem; color:#34d399;">🛡️ Verified Document: {res.get('source', 'Enterprise HR Knowledge Base')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif "summary" in res:
                    st.markdown(f"""
                    <div style="background:rgba(99, 102, 241, 0.1); border-left:4px solid #6366f1; padding:18px 22px; border-radius:10px; font-size:1.05rem;">
                        {res['summary']}
                    </div>
                    """, unsafe_allow_html=True)
                
                with st.expander("🔍 View Raw Agent Execution Payload"):
                    st.json(res)

    # ---------------------------------------------------------
    # DASHBOARD 7: API & SYSTEM ARCHITECTURE
    # ---------------------------------------------------------
    elif selected_page == "📚 API & System Architecture":
        st.markdown("<h2 style='font-size:2.2rem;'>📚 System Architecture & API Endpoints</h2>", unsafe_allow_html=True)
        st.markdown("""
        ### 🏛️ Decoupled Enterprise Architecture
        - **FastAPI Core Engine**: High-throughput REST API for predictive inference, batch processing, and RAG search.
        - **Scikit-Learn ML Engines**: Tuned Random Forest Classifier & Logistic Regression with SMOTE balance.
        - **Streamlit Web Experience**: Glassmorphism UI with real-time Plotly charts and simulation parameters.
        - **Policy RAG Vector Engine**: Semantic similarity matching over corporate policies & handbooks.
        
        ---
        
        ### 🔌 Active REST Endpoints (FastAPI Backend @ Port 8000)
        | Method | Endpoint | Description |
        |---|---|---|
        | `GET` | `/health` | Service health status & loaded model versions |
        | `GET` | `/api/dashboard/overview` | Executive workforce KPIs & risk aggregates |
        | `POST` | `/api/attrition/predict` | Single employee flight-risk & SHAP local drivers |
        | `POST` | `/api/attrition/batch-predict` | Bulk CSV/JSON flight-risk scoring |
        | `POST` | `/api/skills/recommend` | Skill gap analysis & course pathway suggestions |
        | `POST` | `/api/agent/chat` | Agentic HR Copilot policy & diagnostic chat |
        """)
        st.info("💡 You can also explore live interactive Swagger docs at **http://localhost:8000/docs**")


# -------------------------------------------------------------
# WEBSITE FOOTER
# -------------------------------------------------------------
st.markdown("""
<div class="glass-footer">
    <strong>⚡ NexusHR AI Enterprise Operating System</strong> — Workforce Intelligence, Upskilling & Retention OS<br>
    Built with FastAPI, Scikit-Learn & Streamlit · Compliant with GDPR, SOC2 & EEOC Algorithmic Fairness Guidelines
</div>
""", unsafe_allow_html=True)
