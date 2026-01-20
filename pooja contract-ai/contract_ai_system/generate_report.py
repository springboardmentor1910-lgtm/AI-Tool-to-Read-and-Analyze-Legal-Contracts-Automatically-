from graph.multi_agent_graph import workflow
from reporting.report_builder import ReportBuilder
from reporting.pdf_generator import PDFGenerator

contract_text = """
This contract is between the client and vendor.
Legal obligations include confidentiality and arbitration.
Payment terms are 30 days.
"""

# Run workflow
result = workflow.invoke({"contract_text": contract_text})

domain = result.get("domain", "Unknown")
agents = result.get("agents", [])
agent_results = result.get("results", {})

# Build summary
report = ReportBuilder()
summary_text = report.build_summary(domain, agent_results)

# Save PDF
pdf = PDFGenerator()
pdf_path = pdf.create_pdf(summary_text)

print("\n==== REPORT GENERATED ====")
print(summary_text)
print(f"\nPDF saved as: {pdf_path}")
