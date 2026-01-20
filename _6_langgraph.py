# _6_langgraph.py

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
from _2_llm_setup import llm
import json

# -------------------------------------------------
# State definition
# -------------------------------------------------
class State(TypedDict):
    clause: str
    clause_type: str
    details: dict

# -------------------------------------------------
# In-memory clause store (used by Streamlit + Pinecone)
# -------------------------------------------------
db_clause = []

# -------------------------------------------------
# Clause Type Classifier Node
# -------------------------------------------------
def classify_clause_node(state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        """
        Classify the following clause into EXACTLY ONE word:

        compliance
        legal
        finance
        operations

        Clause:
        {clause}

        Rules:
        - Respond with ONE word only
        - No punctuation
        - No explanation
        """
    )

    chain = prompt | llm
    raw = chain.invoke({"clause": state["clause"]}).content

    cleaned = raw.strip().lower().replace(".", "")
    if cleaned not in {"compliance", "legal", "finance", "operations"}:
        cleaned = "operations"

    return {**state, "clause_type": cleaned}

# -------------------------------------------------
# Generic Risk Agent Node Factory
# -------------------------------------------------
def agent_node(agent_name: str):
    def run(state: State) -> State:
        prompt = ChatPromptTemplate.from_template(
            """
            You are a RISK ANALYSIS AGENT.

            Agent type:
            {agent}

            Respond ONLY in valid JSON:
            {{
              "risk": "High | Medium | Low",
              "obligations": true,
              "severity": "Critical | Major | Moderate | Minor",
              "analysis": "2-3 lines explaining the impact"
            }}

            Rules:
            - Output VALID JSON ONLY
            - No markdown
            - No extra text

            Clause:
            {clause}
            """
        )

        chain = prompt | llm
        raw = chain.invoke({
            "clause": state["clause"],
            "agent": agent_name.upper()
        }).content

        try:
            details = json.loads(raw)
        except Exception:
            details = {
                "risk": "Unknown",
                "obligations": False,
                "severity": "Minor",
                "analysis": "JSON parsing failed"
            }

        # Save for vector DB / UI
        db_clause.append({
            "clause": state["clause"],
            "agent": agent_name,
            "risk": details["risk"],
            "obligations": details["obligations"],
            "severity": details["severity"],
            "analysis": details["analysis"]
        })

        return {**state, "details": details}

    return run

# -------------------------------------------------
# Build LangGraph Workflow
# -------------------------------------------------
workflow = StateGraph(State)

# Nodes
workflow.add_node("classifier", classify_clause_node)

for agent in ["compliance", "legal", "finance", "operations"]:
    workflow.add_node(agent, agent_node(agent))

# Router
def router(state: State) -> str:
    return state["clause_type"]

# Edges
workflow.add_edge(START, "classifier")

workflow.add_conditional_edges(
    "classifier",
    router,
    {
        "compliance": "compliance",
        "legal": "legal",
        "finance": "finance",
        "operations": "operations"
    }
)

for agent in ["compliance", "legal", "finance", "operations"]:
    workflow.add_edge(agent, END)

# -------------------------------------------------
# Compile App
# -------------------------------------------------
app = workflow.compile()
