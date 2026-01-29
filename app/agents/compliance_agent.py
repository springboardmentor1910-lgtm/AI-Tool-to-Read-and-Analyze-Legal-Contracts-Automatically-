def compliance_agent(context: str, legal_result: dict, finance_result: dict):
    compliance_risks = [
        "Regulatory references are incomplete"
    ]

    # 🔗 Multi-turn dependency
    if any("payment" in r.lower() for r in finance_result["financial_risks"]):
        compliance_risks.append("Payment non-compliance may violate financial regulations")

    return {
        "agent": "Compliance",
        "used_inputs": {
            "legal": legal_result["key_findings"],
            "finance": finance_result["financial_risks"]
        },
        "checks_performed": compliance_risks
    }
