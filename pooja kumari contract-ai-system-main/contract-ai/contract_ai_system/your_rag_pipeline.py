from contract_ai_system.extract_pdf import extract_pdf
from contract_ai_system.planning.domain_classifier import classify_domain
from contract_ai_system.planning.planner import plan_agents
from contract_ai_system.agents.legal_agent import legal_agent
from contract_ai_system.reporting.report_builder import ReportBuilder
from contract_ai_system.reporting.pdf_generator import PDFGenerator



def run_full_pipeline(pdf_path):

    # 1. Extract PDF text
    contract_text = extract_pdf(pdf_path)

    # 2. Classify domain
    domain = classify_domain(contract_text)

    # 3. Plan agents
    agents = plan_agents(domain)

    # 4. Run agents
    results = {}
    if "LegalAgent" in agents:
        results["LegalAgent"] = legal_agent(contract_text)

    # 5. Create report
    rb = ReportBuilder()
    summary_text = rb.build_summary(domain, results)

    pdf = PDFGenerator()
    pdf_file = pdf.create_pdf(summary_text)

    return {
        "contract_text": contract_text,
        "domain": domain,
        "agents": agents,
        "results": results,
        "pdf_report": pdf_file
    }
