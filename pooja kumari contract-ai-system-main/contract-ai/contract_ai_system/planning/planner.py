def plan_agents(domain: str) -> list:
    domain = domain.strip().lower()

    if domain == "legal":
        return ["LegalAgent"]
    elif domain == "finance":
        return ["FinanceAgent", "LegalAgent"]
    elif domain == "compliance":
        return ["ComplianceAgent", "LegalAgent"]
    elif domain == "operations":
        return ["OperationsAgent", "LegalAgent"]
    
    return ["LegalAgent"]  # default fallback
