from langgraph.graph import StateGraph, END
from huggingface_hub import InferenceClient

from planning.domain_classifier import DomainClassifier
from planning.planner import Planner
from agents.prompts import (
    LEGAL_AGENT_PROMPT,
    COMPLIANCE_AGENT_PROMPT,
    FINANCE_AGENT_PROMPT,
    OPERATIONS_AGENT_PROMPT
)

HF_API_KEY = "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"

# ------------------------------
# LLM Setup
# ------------------------------
llm = InferenceClient(model="HuggingFaceH4/zephyr-7b-beta", token=HF_API_KEY)
classifier = DomainClassifier(HF_API_KEY)
planner = Planner()

# ------------------------------
# Shared State
# ------------------------------
class State(dict):
    contract_text: str
    domain: str
    agents: list
    results: dict


# ------------------------------
# Agent Functions
# ------------------------------
def legal_agent(state: State):
    prompt = LEGAL_AGENT_PROMPT + "\nContract:\n" + state["contract_text"]
    resp = llm.chat_completion([{"role": "user", "content": prompt}], max_tokens=500)
    result = resp.choices[0].message["content"]
    state["results"]["LegalAgent"] = result
    return state


def compliance_agent(state: State):
    prompt = COMPLIANCE_AGENT_PROMPT + "\nContract:\n" + state["contract_text"]
    resp = llm.chat_completion([{"role": "user", "content": prompt}], max_tokens=500)
    result = resp.choices[0].message["content"]
    state["results"]["ComplianceAgent"] = result
    return state


def finance_agent(state: State):
    prompt = FINANCE_AGENT_PROMPT + "\nContract:\n" + state["contract_text"]
    resp = llm.chat_completion([{"role": "user", "content": prompt}], max_tokens=500)
    result = resp.choices[0].message["content"]
    state["results"]["FinanceAgent"] = result
    return state


def operations_agent(state: State):
    prompt = OPERATIONS_AGENT_PROMPT + "\nContract:\n" + state["contract_text"]
    resp = llm.chat_completion([{"role": "user", "content": prompt}], max_tokens=500)
    result = resp.choices[0].message["content"]
    state["results"]["OperationsAgent"] = result
    return state


# ------------------------------
# Workflow Logic Functions
# ------------------------------

def step_domain_classifier(state: State):
    domain = classifier.classify(state["contract_text"])
    state["domain"] = domain
    return state


def step_planner(state: State):
    agents = planner.plan(state["domain"])
    state["agents"] = agents
    state["results"] = {}
    return state


# ------------------------------
# Build Graph
# ------------------------------
graph = StateGraph(State)

graph.add_node("DomainClassifier", step_domain_classifier)
graph.add_node("Planner", step_planner)
graph.add_node("LegalAgent", legal_agent)
graph.add_node("ComplianceAgent", compliance_agent)
graph.add_node("FinanceAgent", finance_agent)
graph.add_node("OperationsAgent", operations_agent)

graph.set_entry_point("DomainClassifier")
graph.add_edge("DomainClassifier", "Planner")

# Dynamic edges based on planner
graph.add_conditional_edges(
    "Planner",
    lambda state: state["agents"],
    {
        "LegalAgent": "LegalAgent",
        "ComplianceAgent": "ComplianceAgent",
        "FinanceAgent": "FinanceAgent",
        "OperationsAgent": "OperationsAgent",
    }
)

# After last agent → END
graph.add_edge("LegalAgent", END)
graph.add_edge("ComplianceAgent", END)
graph.add_edge("FinanceAgent", END)
graph.add_edge("OperationsAgent", END)

workflow = graph.compile()
