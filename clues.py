# clues.py
# Module 3: Multi-Domain Clause Extraction & Classification (Complete)

import re

# 1. DEFINE THE EXPANDED KEYWORDS (Updated Keys)
AGENT_KEYWORDS = {
    "Compliance Agent": [
        "gdpr", "regulation", "compliance", "audit", "policy", "standard", "law",
        "hipaa", "ccpa", "iso", "security", "privacy", "protection", "governance", 
        "risk assessment", "data breach", "regulatory", "statutory", "consent"
    ],
    "Finance Agent": [
        "penalty", "cost", "price", "revenue", "fee", "payment", "net 30", 
        "invoice", "tax", "budget", "currency", "expense", "interest", "billing", 
        "remittance", "financial", "bank", "monetary", "reimbursement", "funding"
    ],
    "Legal Agent": [
        "contract", "agreement", "terminate", "liability", "clause", "indemnity", 
        "jurisdiction", "arbitration", "litigation", "breach", "warranty", 
        "confidentiality", "intellectual property", "force majeure", "governing law", 
        "dispute", "waiver", "severability", "representation"
    ],
    "Operations Agent": [
        "process", "implement", "update", "execute", "timeline", "delivery", 
        "support", "maintenance", "sla", "service level", "uptime", "milestone", 
        "deployment", "training", "logistics", "schedule", "performance", "vendor",
        "technical", "requirements"
    ]
}

# 2. HELPER FUNCTION (CRITICAL for agent_graph.py)
def get_agent_keywords(role):
    """
    Returns the list of keywords for a given agent role.
    Used by the Graph to perform 'Hybrid Search'.
    """
    # Fallback to Legal if role is not found
    return AGENT_KEYWORDS.get(role, AGENT_KEYWORDS["Legal Agent"])

# 3. CLASSIFICATION LOGIC (The "Router")
def classify_clause(clause_text):
    """
    Scans a text chunk and assigns it to an Agent based on keywords.
    """
    clause_lower = clause_text.lower()
    
    # Check against our keyword dictionary
    for agent, keywords in AGENT_KEYWORDS.items():
        if any(k in clause_lower for k in keywords):
            return agent
            
    # Default fallback
    return "Operations Agent"

# 4. DOMAIN-SPECIFIC AGENT FUNCTIONS (The "Analyzers")
# Updated to match the new key names (e.g., checking "Compliance Agent")

def compliance_agent_scan(clause):
    """Checks for High Risk compliance terms"""
    risk_level = "High" if any(x in clause.lower() for x in ["must", "shall", "prohibited", "strict"]) else "Medium"
    return {
        "agent": "Compliance Agent",
        "risk": risk_level,
        "analysis": f"Regulatory obligation identified: '{clause[:60]}...'"
    }

def finance_agent_scan(clause):
    """Checks for money-related exposure"""
    return {
        "agent": "Finance Agent",
        "exposure": "Monetary",
        "analysis": f"Financial impact detected: '{clause[:60]}...'"
    }

def legal_agent_scan(clause):
    """Checks for binding obligations"""
    return {
        "agent": "Legal Agent",
        "obligation": True,
        "analysis": f"Legal clause detected: '{clause[:60]}...'"
    }

def operations_agent_scan(clause):
    """Checks for tasks"""
    return {
        "agent": "Operations Agent",
        "action_required": True,
        "analysis": f"Operational task identified: '{clause[:60]}...'"
    }

# 5. THE MAIN PIPELINE FUNCTION
def analyze_clause_with_clues(clause_text):
    """
    Takes a text chunk, classifies it, and runs the specific agent scan.
    """
    # Step A: Identify who handles this
    agent_type = classify_clause(clause_text)
    
    # Step B: Route to the specific function
    if agent_type == "Compliance Agent":
        return compliance_agent_scan(clause_text)
    elif agent_type == "Finance Agent":
        return finance_agent_scan(clause_text)
    elif agent_type == "Legal Agent":
        return legal_agent_scan(clause_text)
    else:
        return operations_agent_scan(clause_text)

# --- TEST BLOCK ---
if __name__ == "__main__":
    print("--- TESTING MODULE 3: CLUES ENGINE (COMPLETE) ---")
    
    # Test 1: Finance
    t1 = "Vendor shall submit an invoice within 5 business days."
    print(f"\n1. Input: {t1}\n   Result: {analyze_clause_with_clues(t1)}")
    
    # Test 2: Helper Function Check
    print(f"\n2. Keywords Check: {get_agent_keywords('Compliance Agent')[:3]}")