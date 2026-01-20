import gradio as gr
from _3_unstruct_struct_parsing import read_doc_pro
from _4_clause_extraction import extract_clause as extract_clauses
from _5_keyword_classifier import classify_clause
from _6_langgraph import app, db_clause
from _7_embedding_pinecone import upsert_db, query_db

# -------------------------------------------------
# UPDATED HIGH-CONTRAST TABBED CARD CSS
# -------------------------------------------------
custom_css = """
.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    background: #e0f2fe !important;
}

.compact-header {
    background: white;
    padding: 15px 40px;
    margin: 15px 20px;
    border-radius: 12px;
    border-bottom: 4px solid #2563eb;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}
.compact-header h1 { color: #1e40af; font-size: 2rem; font-weight: 900; margin: 0; }
.compact-header p { color: #2563eb; font-size: 0.85rem; margin-top: 2px; font-weight: 700; text-transform: uppercase; }

.tab-card-container {
    background: white !important;
    margin: 0 20px 20px 20px !important;
    border-radius: 15px !important;
    padding: 10px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
}

.inner-card {
    background: #ffffff !important;
    border-radius: 10px !important;
    padding: 20px !important;
    border-top: 5px solid #10b981; 
    box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
}

.btn-yellow { 
    background: #facc15 !important; 
    color: #1e293b !important; 
    font-weight: 800 !important; 
    border: none !important;
    box-shadow: 0 4px 0 #ca8a04 !important;
}

.risk-high { border-left: 8px solid #ef4444; background: #fff1f2; }
.risk-med { border-left: 8px solid #facc15; background: #fefce8; }
.risk-low { border-left: 8px solid #10b981; background: #f0fdf4; }
"""

# -------------------------------------------------
# LOGIC
# -------------------------------------------------
def handle_ingestion(file):
    if not file: return "Error: No file.", "0"
    db_clause.clear()
    elements = read_doc_pro(file.name)
    clauses = extract_clauses(elements)
    for clause in clauses:
        for ctype in classify_clause(clause):
            app.invoke({"clause": clause, "clause_type": ctype})
    upsert_db()
    return f"COMPLETED: {len(db_clause)} points indexed.", f"{len(db_clause)}"

def handle_analysis(query, depth, focus):
    if not query: return "Enter query..."
    # The 'depth' and 'focus' variables now contain the user's dropdown choices
    results = query_db(query)
    html = ""
    for m in results.get("matches", []):
        md = m["metadata"]
        risk = md['risk'].upper()
        r_class = "risk-high" if "HIGH" in risk else "risk-med" if "MEDIUM" in risk else "risk-low"
        html += f"""
        <div style="padding:15px; border-radius:8px; margin-bottom:12px; border:1px solid #e5e7eb;" class="{r_class}">
            <div style="display:flex; justify-content:space-between; font-weight:800; font-size:0.75rem; color:#1e40af; margin-bottom:5px;">
                <span>AGENT: {md['agent'].upper()} ({focus})</span>
                <span>{risk} RISK</span>
            </div>
            <p style="color:#111827; font-size:1rem; font-weight:600; line-height:1.4;">"{md['clause']}"</p>
            <p style="margin-top:8px; font-size:0.9rem; color:#4b5563;">{md['analysis']}</p>
        </div>
        """
    return html

# -------------------------------------------------
# UI CONSTRUCTION
# -------------------------------------------------
with gr.Blocks(css=custom_css, title="Contract Analyzer Executive Suite") as demo:
    
    with gr.Column(elem_classes=["compact-header"]):
        gr.Markdown("# Contract Analyzer")
        gr.Markdown("<p>Executive Contract Intelligence Suite</p>")

    with gr.Tabs(elem_classes=["tab-card-container"]):
        
        # TAB 1: INGESTION
        with gr.Tab("Ingestion"):
            with gr.Row(elem_id="dashboard-grid"):
                with gr.Column(elem_classes=["inner-card"], scale=1):
                    gr.Markdown("### 1. Document Source")
                    file_input = gr.File(label=None)
                    # Initialize button removed; now only RUN AUDIT remains
                    btn_audit = gr.Button("RUN AUDIT", elem_classes=["btn-yellow"])
                
                with gr.Column(elem_classes=["inner-card"], scale=1):
                    gr.Markdown("### 2. Status Monitor")
                    status_out = gr.Textbox(label="Operational Status", interactive=False)
                    stats_out = gr.Label(label="Index Density")

        # TAB 2: ANALYSIS
        with gr.Tab("Semantic Audit"):
            with gr.Row(elem_id="dashboard-grid"):
                with gr.Column(elem_classes=["inner-card"], scale=1):
                    gr.Markdown("### 3. Parameters")
                    query_in = gr.Textbox(label="Semantic Query", placeholder="e.g. Liability...")
                    
                    # Introduces options as requested
                    depth_opt = gr.Dropdown(
                        choices=["Standard", "Detailed", "Executive Summary"], 
                        label="Depth", 
                        value="Standard"
                    )
                    focus_opt = gr.Dropdown(
                        choices=["Legal", "Finance", "Compliance", "Operations"], 
                        label="Focus", 
                        value="Legal"
                    )
                    
                    btn_run = gr.Button("GENERATE ANALYSIS", elem_classes=["btn-yellow"])
                
                with gr.Column(elem_classes=["inner-card"], scale=2):
                    gr.Markdown("### 4. Intelligence Synthesis")
                    search_out = gr.HTML("<div style='text-align:center; padding:30px; color:#2563eb;'>Awaiting query...</div>")

    btn_audit.click(handle_ingestion, inputs=file_input, outputs=[status_out, stats_out])
    btn_run.click(handle_analysis, inputs=[query_in, depth_opt, focus_opt], outputs=search_out)

if __name__ == "__main__":
    demo.launch()