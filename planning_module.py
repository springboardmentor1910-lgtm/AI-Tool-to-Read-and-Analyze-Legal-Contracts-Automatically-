"""Planning Module for generating and coordinating specialized agents."""
from typing import Dict, List, Optional, Any
import json
from enum import Enum
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from free_llm_provider import FreeLLMProvider
from prompt_templates import PromptTemplates, AgentRole


class ContractDomain(Enum):
    """Contract domain classification."""
    TECHNOLOGY = "Technology/IT Services"
    HEALTHCARE = "Healthcare/Medical"
    FINANCIAL = "Financial Services"
    MANUFACTURING = "Manufacturing/Supply Chain"
    REAL_ESTATE = "Real Estate"
    EMPLOYMENT = "Employment/Labor"
    GENERAL = "General Business"
    OTHER = "Other"


class PlanningModule:
    """Planning module to generate and coordinate specialized agents."""
    
    def __init__(self, use_free_model: bool = True):
        """
        Initialize planning module.
        
        Args:
            use_free_model: Whether to use free LLM models
        """
        self.llm = self._initialize_llm(use_free_model)
        self.system_prompt = PromptTemplates.get_system_prompt(AgentRole.PLANNER)
    
    def _initialize_llm(self, use_free_model: bool) -> BaseChatModel:
        """Initialize LLM for planning."""
        if use_free_model:
            free_llm = FreeLLMProvider.get_free_llm()
            if free_llm:
                return free_llm
        
        raise Exception("LLM initialization failed. Set GROQ_API_KEY in .env")
    
    def classify_domain(self, contract_text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Classify contract domain and determine required agents.
        
        Args:
            contract_text: Contract text (can be excerpt for classification)
            metadata: Optional document metadata
        
        Returns:
            Dictionary with domain classification and agent plan
        """
        prompt = PromptTemplates.create_planning_prompt(contract_text, metadata)
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        response_text = response.content
        
        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            plan = json.loads(response_text)
        except (json.JSONDecodeError, ValueError):
            plan = self._create_default_plan(contract_text)
        
        return plan
    
    def _create_default_plan(self, contract_text: str) -> Dict[str, Any]:
        text_lower = contract_text.lower()
        
        domain = ContractDomain.GENERAL.value
        if any(kw in text_lower for kw in ['software', 'it', 'technology', 'api', 'system']):
            domain = ContractDomain.TECHNOLOGY.value
        elif any(kw in text_lower for kw in ['health', 'medical', 'patient', 'hipaa']):
            domain = ContractDomain.HEALTHCARE.value
        elif any(kw in text_lower for kw in ['financial', 'bank', 'loan', 'payment', 'currency']):
            domain = ContractDomain.FINANCIAL.value
        elif any(kw in text_lower for kw in ['manufacturing', 'supply', 'production', 'inventory']):
            domain = ContractDomain.MANUFACTURING.value
        elif any(kw in text_lower for kw in ['property', 'real estate', 'lease', 'rent']):
            domain = ContractDomain.REAL_ESTATE.value
        elif any(kw in text_lower for kw in ['employee', 'employment', 'labor', 'worker']):
            domain = ContractDomain.EMPLOYMENT.value
        
        return {
            "domain": domain,
            "domain_confidence": "medium",
            "agents": {
                "compliance": {
                    "priority": "high",
                    "focus_areas": ["regulatory compliance", "industry standards"],
                    "dependencies": []
                },
                "finance": {
                    "priority": "high",
                    "focus_areas": ["payment terms", "pricing", "financial obligations"],
                    "dependencies": []
                },
                "legal": {
                    "priority": "high",
                    "focus_areas": ["legal terms", "liability", "intellectual property"],
                    "dependencies": []
                },
                "operations": {
                    "priority": "medium",
                    "focus_areas": ["service levels", "delivery", "operational requirements"],
                    "dependencies": []
                }
            },
            "analysis_sequence": ["compliance", "finance", "legal", "operations"],
            "coordination_points": ["Share compliance findings with legal", 
                                   "Cross-reference financial terms with operations"]
        }
    
    def generate_agent_plan(self, contract_text: str, 
                           metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a complete agent coordination plan.
        
        Args:
            contract_text: Contract text
            metadata: Optional document metadata
        
        Returns:
            Complete planning information including domain, agent priorities, and sequence
        """
        plan = self.classify_domain(contract_text, metadata)
        
        plan["coordination_strategy"] = self._determine_coordination_strategy(plan)
        plan["expected_outputs"] = self._determine_expected_outputs(plan)
        
        return plan
    
    def _determine_coordination_strategy(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Determine coordination strategy based on plan."""
        agents = plan.get("agents", {})
        high_priority_agents = [
            name for name, info in agents.items() 
            if info.get("priority", "medium") == "high"
        ]
        
        return {
            "parallel_execution": len(high_priority_agents) <= 2,
            "sequential_execution": len(high_priority_agents) > 2,
            "coordination_required": any(
                len(info.get("dependencies", [])) > 0 
                for info in agents.values()
            ),
            "primary_agents": high_priority_agents
        }
    
    def _determine_expected_outputs(self, plan: Dict[str, Any]) -> Dict[str, List[str]]:
        """Determine expected outputs for each agent."""
        agents = plan.get("agents", {})
        expected = {}
        
        for agent_name, agent_info in agents.items():
            focus_areas = agent_info.get("focus_areas", [])
            expected[agent_name] = [
                f"Analysis of {area}" for area in focus_areas
            ] + ["Risk assessment", "Recommendations"]
        
        return expected
    
    def should_activate_agent(self, agent_name: str, plan: Dict[str, Any]) -> bool:
        """
        Determine if an agent should be activated based on the plan.
        
        Args:
            agent_name: Name of the agent
            plan: Planning information
        
        Returns:
            True if agent should be activated
        """
        agents = plan.get("agents", {})
        if agent_name not in agents:
            return False
        
        agent_info = agents[agent_name]
        priority = agent_info.get("priority", "medium")
        
        return True
    

