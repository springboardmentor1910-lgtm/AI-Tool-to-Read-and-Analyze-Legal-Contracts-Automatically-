"""AI Analyst Agents for contract analysis with LangGraph coordination."""
from typing import Dict, List, Any, TypedDict, Annotated, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from dotenv import load_dotenv
from free_llm_provider import FreeLLMProvider
from prompt_templates import PromptTemplates, AgentRole
from langgraph.graph import StateGraph, END

load_dotenv()


def merge_dicts(left: Dict, right: Dict) -> Dict:
    """Merge two dictionaries."""
    return {**left, **right}

def merge_lists(left: List, right: List) -> List:
    """Merge two lists, avoiding duplicates."""
    combined = left + right
    seen = set()
    result = []
    for item in combined:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

class AgentState(TypedDict):
    """State for LangGraph agent coordination."""
    contract_text: str
    planning_info: Dict[str, Any]
    agent_results: Annotated[Dict[str, Dict], merge_dicts]
    coordination_messages: Annotated[List[str], merge_lists]
    current_agent: str
    completed_agents: Annotated[List[str], merge_lists]
    agent_roles: List[str]


class BaseAgent:
    """Base class for AI analyst agents."""
    
    def __init__(self, role: str, expertise: str, agent_role: AgentRole, use_free_model: bool = True):
        self.role = role
        self.expertise = expertise
        self.agent_role = agent_role
        self.llm = self._initialize_llm()
        self.system_prompt = PromptTemplates.get_system_prompt(agent_role)
    
    def _initialize_llm(self) -> BaseChatModel:
        """Initialize LLM - use free models by default."""
        free_llm = FreeLLMProvider.get_free_llm()
        if free_llm:
            return free_llm
        raise Exception("No working LLM found. Please set GROQ_API_KEY in .env, OR ensure Ollama is installed and running (https://ollama.com/).")
    
    def analyze(self, contract_text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze contract text from the agent's perspective."""
        prompt = PromptTemplates.create_analysis_prompt(self.agent_role, contract_text, context)
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        content = response.content
        
        confidence = None
        import re
        match = re.search(
            r"(?:Overall\s+)?Confidence(?:\s+Score)?\s*[:\-]?\s*\[?\s*(\d{1,3})",
            content,
            re.IGNORECASE,
        )
        if match:
            try:
                value = int(match.group(1))
                if 0 <= value <= 100:
                    confidence = value
            except ValueError:
                confidence = None
        
        result: Dict[str, Any] = {
            "role": self.role,
            "analysis": content,
        }
        if confidence is not None:
            result["confidence"] = confidence
        return result


class ComplianceAgent(BaseAgent):
    """Compliance Analyst Agent."""
    
    def __init__(self, use_free_model: bool = True):
        super().__init__(
            role="Compliance Analyst",
            expertise="regulatory compliance, industry standards, and legal requirements",
            agent_role=AgentRole.COMPLIANCE,
            use_free_model=use_free_model
        )


class FinanceAgent(BaseAgent):
    """Finance Analyst Agent."""
    
    def __init__(self, use_free_model: bool = True):
        super().__init__(
            role="Finance Analyst",
            expertise="financial terms, pricing, payment structures, and financial risks",
            agent_role=AgentRole.FINANCE,
            use_free_model=use_free_model
        )


class LegalAgent(BaseAgent):
    """Legal Analyst Agent."""
    
    def __init__(self, use_free_model: bool = True):
        super().__init__(
            role="Legal Analyst",
            expertise="legal terms, liability, intellectual property, and contract law",
            agent_role=AgentRole.LEGAL,
            use_free_model=use_free_model
        )


class OperationsAgent(BaseAgent):
    """Operations Analyst Agent."""
    
    def __init__(self, use_free_model: bool = True):
        super().__init__(
            role="Operations Analyst",
            expertise="operational requirements, delivery, service levels, and execution",
            agent_role=AgentRole.OPERATIONS,
            use_free_model=use_free_model
        )


class AgentOrchestrator:
    """Orchestrates 4 AI agents for contract analysis using LangGraph."""
    
    def __init__(self, use_free_model: bool = True):
        self.agents = {
            "compliance": ComplianceAgent(use_free_model=use_free_model),
            "finance": FinanceAgent(use_free_model=use_free_model),
            "legal": LegalAgent(use_free_model=use_free_model),
            "operations": OperationsAgent(use_free_model=use_free_model)
        }
        self.use_free_model = use_free_model
        self.graph = self._build_graph()
        self._parallel_pool = None
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph for agent coordination."""
        workflow = StateGraph(AgentState)
        
        workflow.add_node("compliance", self._compliance_node)
        workflow.add_node("finance", self._finance_node)
        workflow.add_node("legal", self._legal_node)
        workflow.add_node("operations", self._operations_node)
        workflow.add_node("coordinate", self._coordinate_node)
        
        workflow.set_entry_point("compliance")
        
        workflow.add_edge("compliance", "finance")
        workflow.add_edge("finance", "legal")
        workflow.add_edge("legal", "operations")
        workflow.add_edge("operations", "coordinate")
        workflow.add_edge("coordinate", END)
        
        return workflow.compile()
    
    def _compliance_node(self, state: AgentState) -> Dict[str, Any]:
        """Compliance agent node."""
        agent_roles = state.get("agent_roles", list(self.agents.keys()))
        if "compliance" not in agent_roles:
            return {"current_agent": "compliance"}
        
        agent = self.agents["compliance"]
        context = self._get_agent_context("compliance", state)
        result = agent.analyze(state["contract_text"], context)
        
        updates = {
            "agent_results": {"compliance": result},
            "completed_agents": ["compliance"],
            "current_agent": "compliance"
        }
        
        if "legal" in state.get("planning_info", {}).get("agents", {}).get("compliance", {}).get("dependencies", []):
            message = PromptTemplates.create_inter_agent_message(
                AgentRole.COMPLIANCE, AgentRole.LEGAL,
                f"Compliance analysis complete. Key findings: {result['analysis'][:200]}...",
                {"agent": "compliance", "status": "complete"}
            )
            updates["coordination_messages"] = [message]
        
        return updates
    
    def _finance_node(self, state: AgentState) -> Dict[str, Any]:
        """Finance agent node."""
        agent_roles = state.get("agent_roles", list(self.agents.keys()))
        if "finance" not in agent_roles:
            return {"current_agent": "finance"}
        
        agent = self.agents["finance"]
        context = self._get_agent_context("finance", state)
        result = agent.analyze(state["contract_text"], context)
        
        return {
            "agent_results": {"finance": result},
            "completed_agents": ["finance"],
            "current_agent": "finance"
        }
    
    def _legal_node(self, state: AgentState) -> Dict[str, Any]:
        """Legal agent node."""
        agent_roles = state.get("agent_roles", list(self.agents.keys()))
        if "legal" not in agent_roles:
            return {"current_agent": "legal"}
        
        agent = self.agents["legal"]
        context = self._get_agent_context("legal", state)
        result = agent.analyze(state["contract_text"], context)
        
        return {
            "agent_results": {"legal": result},
            "completed_agents": ["legal"],
            "current_agent": "legal"
        }
    
    def _operations_node(self, state: AgentState) -> Dict[str, Any]:
        """Operations agent node."""
        agent_roles = state.get("agent_roles", list(self.agents.keys()))
        if "operations" not in agent_roles:
            return {"current_agent": "operations"}
        
        agent = self.agents["operations"]
        context = self._get_agent_context("operations", state)
        result = agent.analyze(state["contract_text"], context)
        
        return {
            "agent_results": {"operations": result},
            "completed_agents": ["operations"],
            "current_agent": "operations"
        }
    
    def _coordinate_node(self, state: AgentState) -> Dict[str, Any]:
        """Coordination node to synthesize results."""
        coordinator_prompt = PromptTemplates.create_coordination_prompt(
            state["agent_results"],
            state.get("planning_info")
        )
        
        coordinator_llm = FreeLLMProvider.get_free_llm()
        coordinator_system = PromptTemplates.get_system_prompt(AgentRole.COORDINATOR)
        
        messages = [
            SystemMessage(content=coordinator_system),
            HumanMessage(content=coordinator_prompt)
        ]
        
        response = coordinator_llm.invoke(messages)
        content = response.content
        
        overall_confidence = None
        import re
        match = re.search(
            r"Overall\s+Confidence(?:\s+Score)?\s*[:\-]?\s*\[?\s*(\d{1,3})",
            content,
            re.IGNORECASE,
        )
        if match:
            try:
                value = int(match.group(1))
                if 0 <= value <= 100:
                    overall_confidence = value
            except ValueError:
                overall_confidence = None
        
        coord_result: Dict[str, Any] = {
            "role": "Coordinator",
            "analysis": content,
        }
        if overall_confidence is not None:
            coord_result["confidence"] = overall_confidence
        
        return {
            "agent_results": {
                "coordination": coord_result
            }
        }
    
    def _get_agent_context(self, agent_name: str, state: AgentState) -> Optional[Dict]:
        """Get context for an agent from other agents' results."""
        context = {}
        planning_info = state.get("planning_info", {})
        dependencies = planning_info.get("agents", {}).get(agent_name, {}).get("dependencies", [])
        
        for dep_agent in dependencies:
            if dep_agent in state["agent_results"]:
                context[dep_agent] = state["agent_results"][dep_agent].get("analysis", "")
        
        return context if context else None
    
    def analyze_contract(self, contract_text: str, planning_info: Optional[Dict] = None, 
                        agent_roles: List[str] = None) -> Dict[str, Any]:
        """
        Analyze contract using multiple agents with LangGraph coordination.
        
        Args:
            contract_text: The contract text to analyze
            planning_info: Optional planning information from PlanningModule
            agent_roles: List of agent roles to use (default: all)
        
        Returns:
            Combined analysis results from all agents
        """
        if agent_roles is None:
            agent_roles = list(self.agents.keys())
        else:
            agent_roles = [r.lower() for r in agent_roles]
        
        initial_state: AgentState = {
            "contract_text": contract_text,
            "planning_info": planning_info or {},
            "agent_results": {},
            "coordination_messages": [],
            "current_agent": "",
            "completed_agents": [],
            "agent_roles": agent_roles
        }
        
        final_state = self.graph.invoke(initial_state)
        
        return {
            "analyses": final_state["agent_results"],
            "coordination_messages": final_state["coordination_messages"],
            "completed_agents": final_state["completed_agents"]
        }

    def analyze_contract_parallel(self, contract_text: str, agent_roles: List[str]) -> Dict[str, Any]:
        """Run selected agents in parallel and return combined analyses."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        roles = [r for r in agent_roles if r in self.agents]
        analyses: Dict[str, Dict[str, str]] = {}
        with ThreadPoolExecutor(max_workers=min(len(roles), 4)) as ex:
            futures = {}
            for role in roles:
                agent = self.agents[role]
                futures[ex.submit(agent.analyze, contract_text, None)] = role
            for fut in as_completed(futures):
                role = futures[fut]
                try:
                    analyses[role] = fut.result()
                except Exception as e:
                    analyses[role] = {"role": role, "analysis": f"Error: {e}"}
        return {"analyses": analyses, "completed_agents": roles, "coordination_messages": []}
