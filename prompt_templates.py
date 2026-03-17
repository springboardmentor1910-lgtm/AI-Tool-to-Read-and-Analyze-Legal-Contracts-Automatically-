"""Prompt templates for agent communication and coordination."""
from typing import Dict, List, Optional
from enum import Enum


class AgentRole(Enum):
    """Agent role enumeration."""
    COMPLIANCE = "compliance"
    FINANCE = "finance"
    LEGAL = "legal"
    OPERATIONS = "operations"
    PLANNER = "planner"
    COORDINATOR = "coordinator"


class PromptTemplates:
    """Structured prompt templates for agent communication."""
    
    SYSTEM_PROMPTS = {
        AgentRole.COMPLIANCE: """You are a Compliance Analyst specializing in regulatory compliance, 
industry standards, and legal requirements. Your role is to analyze contracts and identify 
compliance-related information, risks, and opportunities. Provide clear, actionable insights 
with specific regulatory references when possible.""",
        
        AgentRole.FINANCE: """You are a Finance Analyst specializing in financial terms, pricing, 
payment structures, and financial risks. Your role is to analyze contracts from a financial 
perspective, identifying costs, revenues, risks, and opportunities. Provide detailed financial 
analysis with specific numbers and recommendations.""",
        
        AgentRole.LEGAL: """You are a Legal Analyst specializing in legal terms, liability, 
intellectual property, and contract law. Your role is to review contracts for legal implications, 
identifying risks, obligations, and rights. Provide comprehensive legal analysis with specific 
clause references and recommendations.""",
        
        AgentRole.OPERATIONS: """You are an Operations Analyst specializing in operational 
requirements, delivery, service levels, and execution. Your role is to evaluate contracts from 
an operational perspective, identifying requirements, dependencies, and execution risks. 
Provide practical operational analysis with actionable insights.""",
        
        AgentRole.PLANNER: """You are a Planning Agent responsible for analyzing contract 
requirements and determining which specialized agents should be involved in the analysis. 
You classify contracts by domain and create an analysis plan.""",
        
        AgentRole.COORDINATOR: """You are a Coordination Agent responsible for managing 
inter-agent communication, synthesizing results from multiple agents, and ensuring 
comprehensive analysis coverage."""
    }
    
    @staticmethod
    def get_system_prompt(role: AgentRole) -> str:
        """Get system prompt for a specific agent role."""
        return PromptTemplates.SYSTEM_PROMPTS.get(role, "")
    
    @staticmethod
    def create_analysis_prompt(role: AgentRole, contract_text: str, 
                               context: Optional[Dict] = None) -> str:
        """
        Create analysis prompt for an agent.
        
        Args:
            role: The agent role
            contract_text: The contract text to analyze
            context: Optional context from other agents or previous analysis
        
        Returns:
            Formatted analysis prompt
        """
        base_prompt = f"""Analyze the following contract text from a {role.value} perspective:

{contract_text[:5000]}

"""
        
        if context:
            base_prompt += f"""Additional Context:
{context}

"""
        
        analysis_instructions = {
            AgentRole.COMPLIANCE: """Focus on:
- Regulatory compliance requirements (GDPR, HIPAA, SOX, etc.)
- Industry standards adherence (ISO, NIST, etc.)
- Data protection and privacy compliance
- Export control and trade compliance
- Environmental and safety regulations
- Any compliance risks or gaps

Provide a structured analysis with:
1. Key compliance findings
2. Specific regulatory references
3. Risk assessment
4. Recommendations for compliance improvement
5. Confidence Score: [0-100] (based on clarity and completeness of the contract text)""",
            
            AgentRole.FINANCE: """Focus on:
- Payment terms and schedules
- Pricing structures and pricing mechanisms
- Financial obligations and liabilities
- Currency and exchange rate considerations
- Penalties, late fees, and financial penalties
- Budget implications and cost analysis
- Financial risks and contingencies

Provide a detailed financial analysis with:
1. Financial summary (costs, revenues, payment terms)
2. Risk assessment (financial risks, contingencies)
3. Budget impact analysis
4. Recommendations for financial optimization
5. Confidence Score: [0-100] (based on clarity and completeness of the contract text)""",
            
            AgentRole.LEGAL: """Focus on:
- Legal terms and conditions
- Liability and indemnification clauses
- Intellectual property rights and ownership
- Dispute resolution and governing law
- Termination and breach conditions
- Confidentiality and non-disclosure terms
- Legal risks and potential issues

Provide a comprehensive legal analysis with:
1. Key legal terms and clauses
2. Risk assessment (legal risks, liabilities)
3. Clause-by-clause analysis of critical sections
4. Recommendations for legal protection
5. Confidence Score: [0-100] (based on clarity and completeness of the contract text)""",
            
            AgentRole.OPERATIONS: """Focus on:
- Service level agreements (SLAs) and performance metrics
- Delivery timelines and milestones
- Resource requirements and capacity planning
- Operational processes and procedures
- Quality standards and acceptance criteria
- Change management and modification procedures
- Operational risks and dependencies

Provide a practical operational analysis with:
1. Operational requirements summary
2. Timeline and milestone analysis
3. Resource and capacity assessment
4. Recommendations for operational efficiency
5. Confidence Score: [0-100] (based on clarity and completeness of the contract text)"""
        }
        
        base_prompt += analysis_instructions.get(role, "Provide a comprehensive analysis.")
        
        return base_prompt
    
    @staticmethod
    def create_planning_prompt(contract_text: str, metadata: Optional[Dict] = None) -> str:
        """
        Create prompt for planning agent to classify contract and determine analysis plan.
        
        Args:
            contract_text: The contract text (can be excerpt)
            metadata: Optional document metadata
        
        Returns:
            Planning prompt
        """
        prompt = f"""Analyze the following contract and create an analysis plan:

Contract Excerpt:
{contract_text[:3000]}

"""
        
        if metadata:
            prompt += f"""Document Metadata:
- File Name: {metadata.get('file_name', 'Unknown')}
- File Type: {metadata.get('file_type', 'Unknown')}
- File Size: {metadata.get('file_size', 0)} bytes

"""
        
        prompt += """Based on the contract content, determine:

1. Contract Domain Classification:
   - Technology/IT Services
   - Healthcare/Medical
   - Financial Services
   - Manufacturing/Supply Chain
   - Real Estate
   - Employment/Labor
   - General Business
   - Other (specify)

2. Required Agent Analysis:
   For each agent (Compliance, Finance, Legal, Operations), determine:
   - Priority: High, Medium, Low
   - Focus Areas: Specific aspects to analyze
   - Dependencies: Any inter-agent dependencies

3. Analysis Plan:
   - Recommended analysis sequence
   - Information sharing requirements between agents
   - Expected coordination points

Respond in JSON format:
{
    "domain": "contract domain",
    "domain_confidence": "high/medium/low",
    "agents": {
        "compliance": {
            "priority": "high/medium/low",
            "focus_areas": ["area1", "area2"],
            "dependencies": ["agent_name"]
        },
        "finance": {...},
        "legal": {...},
        "operations": {...}
    },
    "analysis_sequence": ["agent1", "agent2", ...],
    "coordination_points": ["description1", "description2"]
}"""
        
        return prompt
    
    @staticmethod
    def create_coordination_prompt(agent_results: Dict[str, Dict], 
                                   planning_info: Optional[Dict] = None) -> str:
        """
        Create prompt for coordination agent to synthesize results.
        
        Args:
            agent_results: Results from individual agents
            planning_info: Optional planning information
        
        Returns:
            Coordination prompt
        """
        prompt = """Synthesize the following agent analysis results into a comprehensive contract analysis:

"""
        
        for agent_name, result in agent_results.items():
            prompt += f"""--- {agent_name.upper()} ANALYSIS ---
{result.get('analysis', 'No analysis available')}

"""
        
        if planning_info:
            prompt += f"""--- PLANNING INFORMATION ---
Domain: {planning_info.get('domain', 'Unknown')}
Analysis Sequence: {', '.join(planning_info.get('analysis_sequence', []))}

"""
        
        prompt += """Provide a synthesized analysis that:
1. Identifies cross-cutting themes and issues
2. Highlights conflicts or contradictions between agent analyses
3. Prioritizes critical findings across all domains
4. Provides integrated recommendations
5. Identifies any gaps in the analysis
6. Overall Confidence Score: [0-100] (based on agent agreement and analysis quality)

Format your response as:
- Executive Summary
- Key Findings (by domain)
- Critical Issues and Risks
- Integrated Recommendations
- Analysis Gaps (if any)
- Overall Confidence Score: [Score]"""
        
        return prompt
    
    @staticmethod
    def create_inter_agent_message(sender: AgentRole, receiver: AgentRole, 
                                   message: str, context: Optional[Dict] = None) -> str:
        """
        Create formatted message for inter-agent communication.
        
        Args:
            sender: Sending agent role
            receiver: Receiving agent role
            message: Message content
            context: Optional context data
        
        Returns:
            Formatted inter-agent message
        """
        formatted = f"""--- INTER-AGENT MESSAGE ---
From: {sender.value.upper()} Agent
To: {receiver.value.upper()} Agent

Message:
{message}

"""
        
        if context:
            formatted += f"""Context:
{context}

"""
        
        formatted += "--- END MESSAGE ---"
        
        return formatted

