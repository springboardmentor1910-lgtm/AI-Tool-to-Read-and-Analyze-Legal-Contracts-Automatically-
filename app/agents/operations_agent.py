def operations_agent(
    context: str,
    legal_result: dict,
    finance_result: dict,
    compliance_result: dict
):
    operational_risks = [
        "Service delivery depends on payment timelines"
    ]

    # 🔗 Multi-turn dependency
    if "Early termination risk" in legal_result["risks"]:
        operational_risks.append("Early termination may disrupt operations")

    return {
        "agent": "Operations",
        "dependencies_used": {
            "legal": legal_result["risks"],
            "finance": finance_result["financial_risks"],
            "compliance": compliance_result["checks_performed"]
        },
        "optimization_suggestions": operational_risks
    }
