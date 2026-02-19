"""Streamlit UI for Contract Analysis."""
import streamlit as st
import tempfile
import os
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from contract_analyzer import ContractAnalyzer
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

st.set_page_config(page_title="Contract Analysis", page_icon="📄", layout="wide")

# Load CSS from external file
def load_css():
    """Load CSS from external file."""
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero-layout">
        <div class="hero-title">AI-powered contract intelligence dashboard</div>
        <div class="hero-subtitle">
            Upload contracts and review coordinated insights from compliance, finance, legal, and operations agents,
            with confidence scores and a unified overview.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def get_analyzer():
    return ContractAnalyzer(use_free_model=True)

def extract_confidence_score(analysis_text: str) -> Optional[float]:
    """
    Extract confidence score from analysis text using multiple patterns.
    Returns None if no valid score found.
    """
    if not analysis_text:
        return None
    
    # Multiple patterns to catch different formats
    patterns = [
        r"Confidence(?:\s+Score)?\s*[:\-]?\s*\[?\s*(\d{1,3})\s*%?\]?",
        r"Confidence\s*[:\-]\s*(\d{1,3})",
        r"Confidence\s*=\s*(\d{1,3})",
        r"\[Confidence:\s*(\d{1,3})\]",
        r"Confidence\s*\((\d{1,3})\)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, analysis_text, re.IGNORECASE)
        if match:
            try:
                value = int(match.group(1))
                if 0 <= value <= 100:
                    return float(value)
            except (ValueError, IndexError):
                continue
    
    return None

def calculate_fallback_confidence(analysis_text: str) -> float:
    """
    Calculate fallback confidence based on analysis quality indicators.
    """
    if not analysis_text:
        return 30.0
    
    score = 50.0
    
    length = len(analysis_text)
    if length > 500:
        score += 15
    elif length > 300:
        score += 10
    elif length > 150:
        score += 5
    elif length < 50:
        score -= 20
    
    has_numbers = bool(re.search(r'\d+', analysis_text))
    has_bullets = bool(re.search(r'[-•*]\s+', analysis_text) or re.search(r'\d+\.\s+', analysis_text))
    has_sections = bool(re.search(r'[:\n]\s*[A-Z]', analysis_text))
    
    if has_numbers:
        score += 5
    if has_bullets:
        score += 5
    if has_sections:
        score += 5
    
    quality_keywords = ['recommendation', 'risk', 'assessment', 'analysis', 'finding', 'issue', 'term']
    keyword_count = sum(1 for keyword in quality_keywords if keyword.lower() in analysis_text.lower())
    score += min(keyword_count * 2, 10)
    
    return max(0, min(100, score))

def get_agent_confidence(analysis_data: Dict) -> float:
    """
    Get confidence score for an agent, with fallback calculation.
    """
    if not isinstance(analysis_data, dict):
        return 50.0
    
    explicit_conf = analysis_data.get("confidence")
    if isinstance(explicit_conf, (int, float)) and 0 <= explicit_conf <= 100:
        return float(explicit_conf)
    
    analysis_text = analysis_data.get("analysis", "")
    if analysis_text:
        extracted = extract_confidence_score(analysis_text)
        if extracted is not None:
            return extracted
        
        return calculate_fallback_confidence(analysis_text)
    
    return 50.0

def calculate_overall_confidence(analyses: Dict) -> float:
    """
    Calculate weighted overall confidence score.
    """
    agent_confidences = []
    weights = []
    
    agent_weights = {
        "compliance": 1.2,
        "legal": 1.2,
        "finance": 1.0,
        "operations": 1.0,
    }
    
    for agent_name, analysis_data in analyses.items():
        if agent_name == "coordination":
            continue
        
        if isinstance(analysis_data, dict):
            conf = get_agent_confidence(analysis_data)
            weight = agent_weights.get(agent_name, 1.0)
            agent_confidences.append(conf)
            weights.append(weight)
    
    if not agent_confidences:
        return 50.0
    
    total_weighted = sum(conf * weight for conf, weight in zip(agent_confidences, weights))
    total_weight = sum(weights)
    
    return total_weighted / total_weight if total_weight > 0 else 50.0

def get_confidence_class_and_label(confidence: float) -> Tuple[str, str]:
    """Get CSS class and label for confidence score."""
    if confidence >= 80:
        return "conf-good", "Good"
    elif confidence >= 50:
        return "conf-moderate", "Moderate"
    else:
        return "conf-bad", "Low"

def get_agent_conf_html(confidence: float) -> str:
    """Generate HTML for agent confidence badge."""
    if confidence >= 80:
        cls = "agent-conf-good"
        text = "Good"
    elif confidence >= 50:
        cls = "agent-conf-moderate"
        text = "Moderate"
    else:
        cls = "agent-conf-bad"
        text = "Low"
    return f"<span class='agent-conf-pill {cls}'>{confidence:.1f}% · {text}</span>"

def display_agent_analysis(col, agent_name: str, agent_display: str, analysis_data: Dict, expanded: bool = False):
    """Display agent analysis in a column."""
    with col:
        conf = get_agent_confidence(analysis_data)
        conf_html = get_agent_conf_html(conf)
        with st.expander(f"{agent_display} analysis", expanded=expanded):
            st.markdown(
                f"<div class='agent-header-row'><div><div class='agent-label'>Agent</div><div class='agent-name'>{agent_name.title()}</div></div><div>{conf_html}</div></div>",
                unsafe_allow_html=True,
            )
            st.write(analysis_data.get("analysis", ""))

if 'document_history' not in st.session_state:
    st.session_state.document_history = []

if 'stored_results' not in st.session_state:
    st.session_state.stored_results = {}

analyzer = get_analyzer()

with st.sidebar:
    st.header("📚 Document History")
    
    if st.session_state.document_history:
        for idx, doc in enumerate(st.session_state.document_history):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{doc['name'][:40]}**")
                st.caption(f"📅 {doc['date']}")
            with col2:
                if st.button("📄", key=f"view_{idx}", help="View analysis"):
                    st.session_state.selected_doc_id = doc['id']
                    st.rerun()
            st.divider()
    else:
        st.info("No documents uploaded yet")

st.markdown(
    "<div class='upload-card'>",
    unsafe_allow_html=True,
)
uploaded_file = st.file_uploader("Upload Contract (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
st.markdown(
    "<div class='upload-helper'>Supported formats: PDF, DOCX, TXT</div></div>",
    unsafe_allow_html=True,
)

if 'selected_doc_id' in st.session_state:
    doc_id = st.session_state.selected_doc_id
    if doc_id in st.session_state.stored_results:
        results = st.session_state.stored_results[doc_id]
        doc_info = next((d for d in st.session_state.document_history if d['id'] == doc_id), None)
        
        if doc_info:
            analyses = results.get("analyses", {})
            overall_confidence = calculate_overall_confidence(analyses)
            overall_class, label = get_confidence_class_and_label(overall_confidence)
            
            st.markdown(
                f"""<div class="confidence-badge {overall_class}">
                    <span class="conf-dot"></span>
                    <span>{overall_confidence:.1f}% overall confidence · {label}</span>
                </div>""",
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)
            
            if "compliance" in analyses:
                display_agent_analysis(col1, "Compliance", "🔒 Compliance", analyses["compliance"], expanded=True)
            if "finance" in analyses:
                display_agent_analysis(col1, "Finance", "💰 Finance", analyses["finance"])
            if "legal" in analyses:
                display_agent_analysis(col2, "Legal", "⚖️ Legal", analyses["legal"])
            if "operations" in analyses:
                display_agent_analysis(col2, "Operations", "⚙️ Operations", analyses["operations"])
            
            if st.button("Back to Upload"):
                del st.session_state.selected_doc_id
                st.rerun()

if uploaded_file:
    available_roles = ["compliance", "finance", "legal", "operations"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    if st.button("Analyze Contract", type="primary"):
        with st.spinner("Analyzing with AI agents..."):
            try:
                document_id = analyzer.upload_document(tmp_path, skip_indexing=True)
                doc_info = analyzer.documents[document_id]
                parsed = analyzer.parser.parse_document(doc_info["file_path"])
                full_text = parsed["text"]
                condensed = analyzer.build_fast_context(full_text, max_chars=4000)
                fast_results = analyzer.orchestrator.analyze_contract_parallel(condensed, available_roles)
                results = {
                    "success": True,
                    "document_id": document_id,
                    "domain": None,
                    "analyses": fast_results.get("analyses", {}),
                    "coordination_messages": fast_results.get("coordination_messages", []),
                    "completed_agents": fast_results.get("completed_agents", []),
                    "planning_info": {}
                }
                
                st.session_state.document_history.insert(0, {
                    'id': document_id,
                    'name': uploaded_file.name,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'metadata': results.get('document_metadata', {})
                })
                
                st.session_state.stored_results[document_id] = results
                
                if len(st.session_state.document_history) > 20:
                    old_doc = st.session_state.document_history.pop()
                    if old_doc['id'] in st.session_state.stored_results:
                        del st.session_state.stored_results[old_doc['id']]
                
                st.success("✅ Analysis Complete!")

                analyses = results.get("analyses", {})
                overall_confidence = calculate_overall_confidence(analyses)
                overall_class, label = get_confidence_class_and_label(overall_confidence)
                
                st.markdown(
                    f"<div class='confidence-badge {overall_class}'><span class='conf-dot'></span>"
                    f"<span>{overall_confidence:.1f}% overall confidence · {label}</span></div>",
                    unsafe_allow_html=True,
                )

                col1, col2 = st.columns(2)
                
                if "compliance" in analyses:
                    display_agent_analysis(col1, "Compliance", "🔒 Compliance", analyses["compliance"], expanded=True)
                if "finance" in analyses:
                    display_agent_analysis(col1, "Finance", "💰 Finance", analyses["finance"])
                if "legal" in analyses:
                    display_agent_analysis(col2, "Legal", "⚖️ Legal", analyses["legal"])
                if "operations" in analyses:
                    display_agent_analysis(col2, "Operations", "⚙️ Operations", analyses["operations"])
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("💡 Get free Groq API key: https://console.groq.com/")
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
