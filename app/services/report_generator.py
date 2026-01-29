import datetime

def generate_report(
    legal: dict,
    finance: dict,
    compliance: dict,
    operations: dict,
    tone: str = "formal",
    focus: str = "full",
    structure: str = "structured"
):
    """
    Generate a professional, multi-domain analysis report.
    Tones: formal, concise, executive, risk-focused
    Focus: full, legal, finance, compliance, operations
    Structure: structured, bulleted
    """

    sections = {
        "legal": legal,
        "finance": finance,
        "compliance": compliance,
        "operations": operations
    }

    # Filter by focus
    if focus != "full":
        if focus in sections:
            sections = {focus: sections[focus]}
        else:
            # Fallback if invalid focus
            pass

    # Header Generation based on tone
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    titles = {
        "formal": "Comprehensive Contract Analysis Report",
        "concise": "Contract Summary Brief",
        "executive": "Executive Risk & Opportunity Overview",
        "risk-focused": "High-Priority Risk Assessment Report"
    }
    
    title = titles.get(tone, titles["formal"])
    
    report = f"{'='*60}\n"
    report += f"{title.upper()}\n"
    report += f"Generated on: {timestamp}\n"
    report += f"{'='*60}\n\n"

    # Tone-based Introduction
    intros = {
        "formal": "This report provides a detailed multi-domain analysis of the contractual agreement, covering legal, financial, compliance, and operational aspects.",
        "concise": "High-level summary of key contract points and risks.",
        "executive": "Strategic overview of the contract's impact on business operations and financial stability.",
        "risk-focused": "Critical focus on liability, compliance failures, and financial exposure identified in the contract."
    }
    report += intros.get(tone, intros["formal"]) + "\n\n"

    for domain, content in sections.items():
        report += f"[{domain.upper()} ANALYSIS]\n"
        report += f"{'-'*len(domain) + '-----------'}\n"
        
        if structure == "bulleted":
            for key, value in content.items():
                if isinstance(value, list):
                    report += f"• {key.replace('_', ' ').title()}:\n"
                    for item in value:
                        report += f"  - {item}\n"
                else:
                    report += f"• {key.replace('_', ' ').title()}: {value}\n"
        else: # structured
            for key, value in content.items():
                label = key.replace('_', ' ').title()
                if isinstance(value, list):
                    report += f"{label}:\n"
                    for item in value:
                        report += f"  - {item}\n"
                else:
                    report += f"{label}: {value}\n"
        report += "\n"

    # Executive Summary (Simulated synthesis)
    if tone in ["executive", "formal"]:
        report += f"{'='*60}\n"
        report += "EXECUTIVE SUMMARY & RECOMMENDATIONS\n"
        report += f"{'='*60}\n"
        
        # Real logic would use an LLM to synthesize this.
        # For now, we provide a template based on counts.
        risk_count = 0
        for data in sections.values():
            for k, v in data.items():
                if "risk" in k.lower() and isinstance(v, list):
                    risk_count += len(v)
        
        if risk_count > 5:
            report += "STATUS: HIGH ATTENTION REQUIRED\n"
            report += "Recommendation: Re-negotiate key liability and termination clauses before proceeding.\n"
        elif risk_count > 2:
            report += "STATUS: MODERATE RISK\n"
            report += "Recommendation: Proceed with caution; ensure all compliance documentation is in order.\n"
        else:
            report += "STATUS: LOW RISK\n"
            report += "Recommendation: Contract appears standard. Proceed to standard review board.\n"

    return report
