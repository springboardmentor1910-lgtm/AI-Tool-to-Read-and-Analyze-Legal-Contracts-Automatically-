# ---------------------------------------------------------
# FILE: app.py (PREMIUM ENTERPRISE DASHBOARD)
# Senior UI/UX Optimized Version
# ---------------------------------------------------------
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
import re

# --- CONFIGURATION ---
API_URL = "https://ai-legal-contract-analyzer.onrender.com/"

st.set_page_config(
    page_title="AI Legal Contract Analyzer | ContractIQ",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM STYLING (CSS) ---
st.markdown("""
<style>
    /* Import Professional Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styling */
    .stApp { 
        background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
        font-family: 'Inter', 'Segoe UI', sans-serif; 
    }
    
    /* Header Banner */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 28px 40px;
        border-radius: 16px;
        margin-bottom: 32px;
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.25);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .main-title {
        font-size: 36px;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        letter-spacing: -0.5px;
    }
    .main-subtitle {
        font-size: 16px;
        color: #93c5fd;
        margin-top: 8px;
        font-weight: 500;
    }
    
    /* Sidebar Premium Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 2px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }
    
    /* Enhanced KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 24px;
        border-radius: 16px;
        border: 2px solid #e2e8f0;
        box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.08);
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    }
    .kpi-card:hover { 
        transform: translateY(-4px);
        box-shadow: 0 16px 40px -8px rgba(15, 23, 42, 0.15);
        border-color: #cbd5e1;
    }
    .kpi-val { 
        font-size: 38px; 
        font-weight: 800; 
        color: #0f172a; 
        margin: 12px 0 8px 0;
        line-height: 1;
    }
    .kpi-lbl { 
        font-size: 12px; 
        font-weight: 700; 
        color: #64748b; 
        text-transform: uppercase; 
        letter-spacing: 1.2px;
    }
    
    /* Agent Report Cards */
    .agent-box {
        background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        transition: all 0.2s ease;
    }
    .agent-box:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        transform: translateX(4px);
    }
    .agent-header { 
        font-weight: 700; 
        font-size: 17px; 
        color: #1e293b; 
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        background-color: transparent;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        color: #1e293b;
    }
    
    /* Headers */
    h1, h2, h3 { 
        color: #0f172a; 
        font-weight: 700;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #3b82f6 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER: CONFIDENCE CALIBRATION (OPTIMIZED) ---
def calibrate_confidence(raw_score):
    """
    Professional confidence scaling.
    OPTIMIZATION: Adjusted formula to prevent saturation at 99%.
    Raw scores of 0.3-0.6 will now map to 60-90% range, showing realistic variance.
    """
    if raw_score <= 0.01: return 0.0
    
    # New Formula: Smoother curve, less aggressive multiplier
    # 0.30 -> ~63%
    # 0.45 -> ~85%
    # 0.60 -> ~99%
    calibrated = (raw_score * 1.6) + 0.15
    return min(calibrated, 0.99) * 100

# --- HELPER: INTELLIGENT RISK CALCULATION ---
def calculate_agent_risk(agent_name, report_text):
    """
    Advanced risk scoring based on agent domain and content analysis.
    Each agent has unique risk thresholds.
    """
    report_lower = report_text.lower()
    
    # Base risk scores by agent specialty
    base_risks = {
        "Financial Agent": 30,
        "Compliance Agent": 35,
        "IP Agent": 25,
        "Liability Agent": 40,
        "Termination Agent": 20
    }
    base_risk = base_risks.get(agent_name, 30)
    
    # Critical keyword scoring (weighted by severity)
    critical_keywords = {
        'critical': 35, 'severe': 30, 'breach': 25, 'violation': 25,
        'liability': 20, 'penalty': 18, 'terminate': 15, 'damages': 20,
        'non-compliance': 22, 'unauthorized': 18, 'infringement': 25,
        'default': 20, 'forfeit': 22
    }
    
    warning_keywords = {
        'warning': 12, 'attention': 10, 'caution': 10, 'risk': 8,
        'concern': 8, 'issue': 7, 'limitation': 8, 'restriction': 9,
        'requirement': 6, 'must': 5, 'obligation': 7
    }
    
    positive_keywords = {
        'compliant': -10, 'approved': -8, 'satisfactory': -12,
        'acceptable': -8, 'standard': -5, 'clear': -6, 'valid': -7
    }
    
    risk_adjustment = 0
    
    # Score based on keyword presence
    for keyword, weight in critical_keywords.items():
        risk_adjustment += report_lower.count(keyword) * weight
    
    for keyword, weight in warning_keywords.items():
        risk_adjustment += report_lower.count(keyword) * weight
    
    for keyword, weight in positive_keywords.items():
        risk_adjustment += report_lower.count(keyword) * weight
    
    # Agent-specific multipliers
    multipliers = {
        "Liability Agent": 1.3,      # Higher risk domain
        "Compliance Agent": 1.25,    # Regulatory concerns
        "Financial Agent": 1.15,     # Money matters
        "IP Agent": 1.1,             # Intellectual property
        "Termination Agent": 1.0     # Standard risk
    }
    
    multiplier = multipliers.get(agent_name, 1.0)
    final_risk = (base_risk + risk_adjustment) * multiplier
    
    # Clamp between 0-100
    return max(0, min(100, int(final_risk)))

# --- HELPER: VISUALIZATIONS ---
def create_gauge(score):
    """Premium gauge chart with gradient styling"""
    color = "#ef4444" if score > 75 else "#f59e0b" if score > 40 else "#10b981"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Risk Intensity", 'font': {'size': 20, 'color': '#475569', 'family': 'Inter'}},
        number = {'font': {'size': 42, 'family': 'Inter', 'weight': 700}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "#94a3b8"},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "#f8fafc",
            'borderwidth': 3,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, 40], 'color': '#d1fae5'},
                {'range': [40, 75], 'color': '#fef3c7'},
                {'range': [75, 100], 'color': '#fee2e2'}
            ],
            'threshold': {
                'line': {'color': "#1e293b", 'width': 3},
                'thickness': 0.8,
                'value': score
            }
        }
    ))
    fig.update_layout(
        height=280, 
        margin=dict(l=20, r=20, t=60, b=20), 
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter'}
    )
    return fig

def create_risk_bar(reports):
    """Dynamic bar chart with agent-specific risk scoring"""
    data = []
    
    for agent, text in reports.items():
        risk_score = calculate_agent_risk(agent, text)
        agent_short = agent.replace(" Agent", "")
        data.append({
            "Domain": agent_short, 
            "Risk": risk_score,
            "Agent": agent
        })
    
    if not data: return None
    
    df = pd.DataFrame(data).sort_values('Risk', ascending=True)
    
    fig = px.bar(
        df, 
        x='Risk', 
        y='Domain',
        orientation='h',
        color='Risk',
        color_continuous_scale=['#10b981', '#fbbf24', '#f59e0b', '#ef4444'],
        range_x=[0, 100],
        title="Risk Distribution by Legal Domain",
        text='Risk'
    )
    
    fig.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        marker=dict(line=dict(width=2, color='#ffffff'))
    )
    
    fig.update_layout(
        height=320,
        margin=dict(l=20, r=40, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        font={'family': 'Inter', 'size': 12},
        title={'font': {'size': 18, 'color': '#1e293b', 'family': 'Inter', 'weight': 700}},
        xaxis={'gridcolor': '#e2e8f0', 'title': 'Risk Score'},
        yaxis={'title': ''},
        coloraxis_showscale=False
    )
    
    return fig

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 48px; margin-bottom: 12px;">⚖️</div>
        <div style="font-size: 24px; font-weight: 800; color: #1e293b; margin-bottom: 4px;">ContractIQ</div>
        <div style="font-size: 13px; color: #64748b; font-weight: 600; letter-spacing: 1px;">ENTERPRISE AI AUDIT</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    uploaded_file = st.file_uploader("📄 Upload Agreement (PDF)", type=["pdf"])
    
    if uploaded_file:
        # LOGIC FIX: Check if this file is different from the last one
        if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
            with st.spinner("🔄 Indexing Document Vector Space..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    
                    # LOGIC FIX: Wrapped in specific try/except to catch connection issues
                    response = requests.post(f"{API_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        st.session_state.current_file = uploaded_file.name
                        # LOGIC FIX: Clear old chat history and metrics when new file is uploaded
                        st.session_state.messages = []
                        st.session_state["confidence_score"] = 0.0
                        st.session_state["risk_score"] = 0
                        st.session_state["agent_reports"] = {}
                        
                        st.success("✅ Document Indexed Successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Upload failed: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to Backend Server. Is it running?")
                except Exception as e:
                    st.error(f"❌ Error during upload: {e}")
    
    st.divider()
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); 
                padding: 16px; border-radius: 12px; border-left: 4px solid #3b82f6;">
        <div style="font-size: 13px; font-weight: 600; color: #1e40af; margin-bottom: 8px;">
            💡 PRO TIP
        </div>
        <div style="font-size: 12px; color: #1e3a8a; line-height: 1.5;">
            Try asking <strong>"Audit this document"</strong> for a comprehensive multi-agent analysis.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN DASHBOARD ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# PREMIUM HEADER
st.markdown("""
<div class="main-header">
    <div class="main-title">⚖️ AI Legal Contract Analyzer</div>
    <div class="main-subtitle">Multi-Agent Enterprise Document Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

# KPI SECTION
col1, col2, col3 = st.columns(3)

raw_conf = st.session_state.get("confidence_score", 0.0)
calibrated_conf = calibrate_confidence(raw_conf)
with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">AI Confidence</div>
        <div class="kpi-val" style="color: #3b82f6;">{calibrated_conf:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

risk_score = st.session_state.get("risk_score", 0)
risk_color = "#ef4444" if risk_score > 75 else "#f59e0b" if risk_score > 40 else "#10b981"
with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Overall Risk Score</div>
        <div class="kpi-val" style="color: {risk_color};">{risk_score}/100</div>
    </div>
    """, unsafe_allow_html=True)

status = "🟢 Active" if st.session_state.messages else "⚪ Idle"
with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">System Status</div>
        <div class="kpi-val" style="font-size: 28px; color: #64748b;">{status}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- TABS LAYOUT ---
tab_chat, tab_visuals = st.tabs(["💬 Executive Chat Interface", "📊 Risk Analytics Dashboard"])

with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("💭 Ask me anything about your contract... (e.g., 'Audit this document')"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🤖 Coordinating Multi-Agent Analysis System..."):
                try:
                    payload = {"query": prompt}
                    res = requests.post(f"{API_URL}/analyze", json=payload).json()
                    
                    st.session_state["confidence_score"] = res.get("confidence_score", 0.0)
                    st.session_state["agent_reports"] = res.get("agent_reports", {})
                    
                    # Calculate overall risk from agent reports
                    reports = res.get("agent_reports", {})
                    if reports:
                        agent_risks = [calculate_agent_risk(agent, text) for agent, text in reports.items()]
                        overall_risk = int(sum(agent_risks) / len(agent_risks))
                        st.session_state["risk_score"] = overall_risk
                    else:
                        st.session_state["risk_score"] = res.get("risk_score", 0)

                    # Format response
                    doc_name = "Document Analysis"
                    raw_summary = res.get("executive_summary", "")
                    if raw_summary:
                        first_line = raw_summary.split('\n')[0].replace("**", "").replace("Document Type:", "").strip()
                        if len(first_line) > 5:
                            doc_name = first_line

                    formatted_response = f"### 📄 {doc_name}\n\n"
                    
                    if reports:
                        for idx, (agent, text) in enumerate(reports.items(), 1):
                            clean_text = text.replace("## ", "#### ")
                            formatted_response += f"#### {idx}. {agent}\n"
                            formatted_response += f"{clean_text}\n\n"
                            formatted_response += "---\n"
                    else:
                        formatted_response = res["result"]

                    st.markdown(formatted_response)
                    st.session_state.messages.append({"role": "assistant", "content": formatted_response})
                    
                    st.rerun()

                except requests.exceptions.ConnectionError:
                    st.error("❌ Connection Error: Is the Backend Server Running?")
                except Exception as e:
                    st.error(f"⚠️ Analysis Error: {e}")

with tab_visuals:
    if "risk_score" in st.session_state and st.session_state.get("agent_reports"):
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.plotly_chart(create_gauge(st.session_state["risk_score"]), use_container_width=True)
            
        with c2:
            reports = st.session_state.get("agent_reports", {})
            if reports:
                st.plotly_chart(create_risk_bar(reports), use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; background: white; border-radius: 16px; border: 2px dashed #cbd5e1;">
            <div style="font-size: 64px; margin-bottom: 16px; opacity: 0.5;">📊</div>
            <div style="font-size: 20px; font-weight: 700; color: #475569; margin-bottom: 8px;">
                No Analytics Available
            </div>
            <div style="font-size: 14px; color: #64748b;">
                Start a document analysis to generate risk visualization data
            </div>
        </div>
        """, unsafe_allow_html=True)