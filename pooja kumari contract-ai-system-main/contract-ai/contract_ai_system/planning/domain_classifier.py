def classify_domain(contract_text: str) -> str:
    contract_lower = contract_text.lower()

    if any(word in contract_lower for word in ["invoice", "payment", "amount", "bank", "interest"]):
        return "Finance"
    if any(word in contract_lower for word in ["confidential", "liability", "arbitration", "law", "legal"]):
        return "Legal"
    if any(word in contract_lower for word in ["compliance", "policy", "standards", "regulatory"]):
        return "Compliance"
    if any(word in contract_lower for word in ["delivery", "operations", "service level", "sla"]):
        return "Operations"

    return "Legal"  # default fallback
