def finance_agent(context: str, legal_result: dict):
    risks = [
        "Delayed payments may affect cash flow"
    ]

    # 🔗 Multi-turn dependency
    if "Identified termination clauses" in legal_result["key_findings"]:
        risks.append("Termination may trigger penalty or settlement costs")

    return {
        "agent": "Finance",
        "used_legal_findings": legal_result["key_findings"],
        "financial_risks": risks
    }
