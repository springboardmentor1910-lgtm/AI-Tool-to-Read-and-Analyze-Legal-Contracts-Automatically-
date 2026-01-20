import re

RAW_AGENT_KEYWORDS = {

    "compliance": [
        # Obligations & modality
        "shall", "must", "required", "mandatory", "obligation", "obligatory",
        "prohibited", "restricted", "permitted", "authorized",

        # Regulatory terms
        "regulation", "regulatory", "guideline", "circular", "directive",
        "framework", "policy", "rule", "norm", "standard",

        # Audits & controls
        "audit", "auditor", "inspection", "review", "monitoring",
        "oversight", "control", "compliance",

        # Laws & standards
        "gdpr", "dpdp", "iso", "iso27001", "sox",
        "basel", "rbi", "sebi", "fema", "aml", "kyc"
    ],

    "finance": [
        # Money & value
        "cost", "capital", "expense", "expenditure", "pricing",
        "price", "revenue", "income", "profit", "loss",

        # Credit & exposure
        "exposure", "loan", "advance", "credit", "debt",
        "repayment", "disbursement", "outstanding", "principal",

        # Charges & penalties
        "fee", "fees", "penalty", "interest", "tax",
        "levy", "fine", "invoice", "billing",

        # Accounting & valuation
        "valuation", "provision", "writeoff", "impairment",
        "cashflow", "cashflows", "capitalization", "roi"
    ],

    "legal": [
        # Agreements
        "agreement", "contract", "arrangement", "deed",
        "undertaking", "memorandum",

        # Clauses & rights
        "clause", "article", "section", "provision",
        "right", "obligation", "covenant",

        # Liability & risk
        "liability", "indemnity", "damages", "breach",
        "default", "penalty", "remedy",

        # Termination & enforcement
        "terminate", "termination", "rescission",
        "jurisdiction", "governing law", "arbitration",
        "litigation", "dispute", "enforcement",

        # Parties
        "lender", "borrower", "counterparty", "debtor", "creditor"
    ],

    "operations": [
        # Execution & processes
        "process", "procedure", "workflow", "implementation",
        "execution", "operation", "operational",

        # Timelines & phases
        "timeline", "milestone", "phase", "schedule",
        "turnaround", "delivery", "deployment",

        # Systems & support
        "system", "platform", "infrastructure", "service",
        "support", "maintenance", "uptime", "downtime",

        # Performance & control
        "sla", "kpi", "performance", "efficiency",
        "capacity", "resource", "staffing",

        # Change & updates
        "update", "upgrade", "migration", "rollout",
        "transition", "integration"
    ]
}

def normalize_keywords(agent_keywords):
    normalized = {}
    for agent, keywords in agent_keywords.items():
        normalized[agent] = [re.sub(r"\s+", " ", k.strip().lower()) for k in keywords]

    return normalized
    
AGENT_KEYWORDS = normalize_keywords(RAW_AGENT_KEYWORDS)


def classify_clause(clause: str):
    clause = clause.lower()
    matches = [a for a, kws in AGENT_KEYWORDS.items() if any(k in clause for k in kws)]
    return matches or ["operations"]




