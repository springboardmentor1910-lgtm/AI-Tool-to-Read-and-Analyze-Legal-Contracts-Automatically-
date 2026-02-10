# ---------------------------------------------------------
# FILE: planning.py (SEMANTIC INTENT ENGINE - EXPERT LEVEL)
# ---------------------------------------------------------
import os
import json
import re
from typing import List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field

load_dotenv()

# Initialize the Brain (Llama-3)
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,  # Zero temperature = Strict Logic
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- DATA STRUCTURES ---
class AgentTask(BaseModel):
    role: str = Field(description="Agent Name")
    objective: str = Field(description="Specific goal")

# --- STANDARD PROTOCOLS (The "Playbook") ---
# We define the "Standard Operating Procedure" for a full audit here.
# This ensures consistency whenever a general summary is requested.
FULL_AUDIT_PLAYBOOK = [
    {"role": "Legal Agent", "objective": "Summarize parties, jurisdiction, term length, and key liability clauses."},
    {"role": "Finance Agent", "objective": "Extract total contract value, payment schedule, late fees, and penalties."},
    {"role": "Compliance Agent", "objective": "Check for data privacy (GDPR/CCPA), security standards, and audit rights."},
    {"role": "Operations Agent", "objective": "List key deliverables, milestones, SLAs, and support obligations."}
]

def create_execution_plan(user_query):
    print(f"\n🧠 PLANNING: Classifying Intent for: '{user_query}'...")
    
    # --- STAGE 1: INTENT CLASSIFICATION (The "Manager") ---
    # We don't match words. We ask the AI to categorize the request.
    
    classification_prompt = """
    You are a Senior Project Manager. Classify the User's Query into one of two categories:
    
    1. **GLOBAL_AUDIT**: The user wants a summary, overview, briefing, or full analysis of the document.
       - Keywords (Examples only): "summarize", "explain", "what is this", "audit", "brief me", "review", "digest", "tl;dr".
       
    2. **TARGETED_QUERY**: The user is asking about a specific topic (money, laws, dates, risks).
       - Examples: "What are the payment terms?", "Is there an indemnity clause?", "When does this expire?"
    
    RETURN JSON ONLY: { "category": "GLOBAL_AUDIT" } or { "category": "TARGETED_QUERY" }
    """
    
    try:
        # Ask the AI to classify
        resp = llm.invoke([
            SystemMessage(content=classification_prompt),
            SystemMessage(content=f"User Query: {user_query}")
        ])
        
        # Safe Parse
        match = re.search(r"\{.*\}", resp.content, re.DOTALL)
        if match:
            intent_data = json.loads(match.group(0))
            category = intent_data.get("category", "TARGETED_QUERY")
        else:
            category = "TARGETED_QUERY" # Default to specific if unsure

        print(f"   🚀 CLASSIFICATION: {category}")

        # --- STAGE 2: EXECUTION STRATEGY ---
        
        if category == "GLOBAL_AUDIT":
            # If the user wants a summary, we ALWAYS run the full playbook.
            return FULL_AUDIT_PLAYBOOK

        else:
            # If it's a specific question, we use the "Chain of Thought" Router to pick agents.
            return generate_targeted_plan(user_query)

    except Exception as e:
        print(f"   ⚠️ Planner Error: {e}")
        # Universal Fallback -> Just run the Legal Agent
        return [{"role": "Legal Agent", "objective": "Analyze the user's request."}]

def generate_targeted_plan(query):
    """
    Helper function to map specific questions to specific agents.
    """
    router_prompt = """
    You are the Router. Map the specific question to the correct Expert Agent(s).
    
    ### AGENT DOMAINS
    - **Legal Agent**: Liability, Indemnity, IP, Termination, Jurisdiction.
    - **Finance Agent**: Fees, Payments, Taxes, Penalties, Budget.
    - **Compliance Agent**: GDPR, Security, Data Privacy, Audits.
    - **Operations Agent**: SLAs, Deliverables, Timelines, Support.
    
    ### INSTRUCTIONS
    1. Analyze the query.
    2. Select the BEST agent(s).
    3. Write a specific objective.
    
    OUTPUT JSON: { "tasks": [ {"role": "Agent Name", "objective": "Specific Task"} ] }
    """
    
    resp = llm.invoke([
        SystemMessage(content=router_prompt),
        SystemMessage(content=f"Query: {query}")
    ])
    
    match = re.search(r"\{.*\}", resp.content, re.DOTALL)
    if match:
        return json.loads(match.group(0)).get("tasks", [])
    else:
        return [{"role": "Legal Agent", "objective": f"Answer: {query}"}]