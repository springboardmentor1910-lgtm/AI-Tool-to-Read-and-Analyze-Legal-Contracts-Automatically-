"""Contract analysis system with planning module integration."""
import os
import uuid
import time
from typing import Dict, List, Optional
from document_parser import DocumentParser
from agents import AgentOrchestrator
from planning_module import PlanningModule
from langchain_huggingface import HuggingFaceEmbeddings
from concurrent.futures import ThreadPoolExecutor, as_completed

class ContractAnalyzer:
    """Main contract analysis system."""
    
    def __init__(self, use_free_model: bool = True):
        """Initialize analyzer with free models by default."""
        self.parser = DocumentParser()
        self.orchestrator = AgentOrchestrator(use_free_model=use_free_model)
        self.planner = PlanningModule(use_free_model=use_free_model)
        self.documents = {}
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = None
        self.vector_store_type = None
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        disable_pinecone = os.getenv("DISABLE_PINECONE", "0") == "1"
        if pinecone_api_key and not disable_pinecone:
            try:
                from pinecone import Pinecone as PineconeClient, ServerlessSpec
                from langchain_community.vectorstores import Pinecone
                pc = PineconeClient(api_key=pinecone_api_key)
                index_name = os.getenv("PINECONE_INDEX_NAME", "contracts")
                existing = [i.name for i in pc.list_indexes()]
                if index_name not in existing:
                    pc.create_index(
                        name=index_name,
                        dimension=384,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud=os.getenv("PINECONE_CLOUD", "aws"),
                            region=os.getenv("PINECONE_REGION", "us-east-1")
                        )
                    )
                self.vector_store = Pinecone.from_existing_index(
                    index_name=index_name,
                    embedding=self.embeddings
                )
                self.vector_store_type = "pinecone"
            except Exception as e:
                print(f"Failed to initialize Pinecone: {e}")
        if self.vector_store is None:
            try:
                from langchain_community.vectorstores import Chroma
                self.vector_store = Chroma(
                    collection_name="contracts",
                    embedding_function=self.embeddings,
                    persist_directory=".chroma"
                )
                self.vector_store_type = "chroma"
            except Exception:
                class _MemoryStore:
                    def __init__(self):
                        self.items = []
                    def add_texts(self, texts: List[str], metadatas: List[Dict], ids: Optional[List[str]] = None):
                        for i, t in enumerate(texts):
                            self.items.append({"text": t, "metadata": metadatas[i] if i < len(metadatas) else {}})
                    def similarity_search(self, query: str, k: int = 5):
                        res = []
                        for it in self.items:
                            if query.lower() in it["text"].lower():
                                class _Doc:
                                    def __init__(self, text, meta):
                                        self.page_content = text
                                        self.metadata = meta
                                res.append(_Doc(it["text"], it["metadata"]))
                        return res[:k]
                self.vector_store = _MemoryStore()
                self.vector_store_type = "memory"
    
    def upload_document(self, file_path: str, document_id: Optional[str] = None, skip_indexing: bool = False) -> str:
        """
        Upload and process a contract document.
        
        Args:
            file_path: Path to the document file
            document_id: Optional custom document ID (auto-generated if not provided)
        
        Returns:
            Document ID
        """
        if document_id is None:
            document_id = str(uuid.uuid4())
        
        parsed = self.parser.parse_document(file_path)
        text = parsed["text"]
        metadata = parsed["metadata"]
        
        if not skip_indexing:
            chunks = self.parser.chunk_text(text, chunk_size=1000, chunk_overlap=200)
            texts = [c["text"] for c in chunks]
            metas = [{**metadata, "chunk_index": c["chunk_index"], "document_id": document_id} for c in chunks]
            self.vector_store.add_texts(texts=texts, metadatas=metas, ids=[f"{document_id}_{c['chunk_index']}" for c in chunks])
            if self.vector_store_type == "chroma":
                self.vector_store.persist()
            num_chunks = len(chunks)
        else:
            num_chunks = 0

        self.documents[document_id] = {
            "file_path": file_path,
            "metadata": metadata,
            "num_chunks": num_chunks,
            "text_length": len(text)
        }
        
        return document_id
    
    def analyze_contract(self, document_id: str, agent_roles: Optional[List[str]] = None) -> Dict:
        """
        Analyze a contract using AI agents with planning module coordination.
        
        Args:
            document_id: ID of the document to analyze
            agent_roles: List of agent roles to use (default: all, determined by planning)
        
        Returns:
            Analysis results with planning information
        """
        if document_id not in self.documents:
            raise ValueError(f"Document {document_id} not found")
        
        doc_info = self.documents[document_id]
        parsed = self.parser.parse_document(doc_info["file_path"])
        full_text = parsed["text"]
        metadata = doc_info.get("metadata", {})
        
        planning_info = self.planner.generate_agent_plan(full_text, metadata)
        
        if agent_roles is None:
            agent_roles = []
            agents_info = planning_info.get("agents", {})
            for agent_name, agent_info in agents_info.items():
                if self.planner.should_activate_agent(agent_name, planning_info):
                    agent_roles.append(agent_name)
        
        analysis_results = self.orchestrator.analyze_contract(
            full_text, 
            planning_info=planning_info,
            agent_roles=agent_roles
        )
        
        analysis_results["document_id"] = document_id
        analysis_results["document_metadata"] = metadata
        analysis_results["planning_info"] = planning_info
        analysis_results["domain"] = planning_info.get("domain", "Unknown")
        
        return analysis_results
    
    def classify_domain(self, document_id: str) -> Dict:
        """
        Classify contract domain without full analysis.
        
        Args:
            document_id: ID of the document to classify
        
        Returns:
            Domain classification and planning information
        """
        if document_id not in self.documents:
            raise ValueError(f"Document {document_id} not found")
        
        doc_info = self.documents[document_id]
        parsed = self.parser.parse_document(doc_info["file_path"])
        full_text = parsed["text"]
        metadata = doc_info.get("metadata", {})
        
        planning_info = self.planner.generate_agent_plan(full_text, metadata)
        
        return {
            "document_id": document_id,
            "domain": planning_info.get("domain", "Unknown"),
            "domain_confidence": planning_info.get("domain_confidence", "medium"),
            "analysis_plan": {
                "agents": planning_info.get("agents", {}),
                "analysis_sequence": planning_info.get("analysis_sequence", []),
                "coordination_strategy": planning_info.get("coordination_strategy", {}),
                "expected_outputs": planning_info.get("expected_outputs", {})
            },
            "coordination_points": planning_info.get("coordination_points", [])
        }

    
    def build_fast_context(self, text: str, max_chars: int = 4000) -> str:
        lower = text.lower()
        keywords = [
            "gdpr", "hipaa", "regulatory", "compliance", "data protection", "export control", "confidentiality",
            "payment terms", "pricing", "late fees", "penalties", "pricing mechanism", "budget", "invoice",
            "indemnification", "liability", "intellectual property", "governing law", "dispute", "termination", "warranty",
            "service level", "sla", "delivery", "timeline", "acceptance", "change management", "performance", "metrics"
        ]
        segments = []
        seen = set()
        for kw in keywords:
            start = 0
            k = kw.lower()
            while True:
                idx = lower.find(k, start)
                if idx == -1:
                    break
                s = max(0, idx - 400)
                e = min(len(text), idx + 400)
                seg = text[s:e].strip()
                if seg and seg not in seen:
                    segments.append(seg)
                    seen.add(seg)
                start = idx + len(k)
                if len("".join(segments)) >= max_chars * 2:
                    break
        if not segments:
            return text[:max_chars]
        condensed = "\n\n".join(segments)
        if len(condensed) > max_chars:
            condensed = condensed[:max_chars]
        return condensed

    def extract_clauses_parallel(self, document_id: str, domains: Optional[List[str]] = None, k: int = 5) -> Dict[str, List[Dict]]:
        if document_id not in self.documents:
            raise ValueError(f"Document {document_id} not found")
        queries = {
            "compliance": [
                "GDPR compliance", "HIPAA privacy", "regulatory obligations", "data protection", "export control", "confidentiality"
            ],
            "finance": [
                "payment terms", "pricing", "late fees", "penalties", "pricing mechanism", "budget"
            ],
            "legal": [
                "indemnification", "liability", "intellectual property", "governing law", "dispute resolution", "termination"
            ],
            "operations": [
                "service level agreement", "SLA", "delivery timeline", "acceptance criteria", "change management", "performance metrics"
            ],
        }
        if domains is None:
            domains = ["compliance", "finance", "legal", "operations"]
        results: Dict[str, List[Dict]] = {d: [] for d in domains}
        def run_query(q: str):
            try:
                return self.search(q, k=k)
            except Exception:
                return []
        with ThreadPoolExecutor(max_workers=min(sum(len(queries[d]) for d in domains), 8)) as ex:
            future_map = {}
            for domain in domains:
                for q in queries.get(domain, []):
                    future_map[ex.submit(run_query, q)] = (domain, q)
            for fut in as_completed(future_map):
                domain, q = future_map[fut]
                hits = fut.result()
                seen_texts = set()
                for h in hits:
                    if h["text"] not in seen_texts:
                        results[domain].append({"query": q, "text": h["text"], "document_id": h["document_id"], "chunk_index": h["chunk_index"]})
                        seen_texts.add(h["text"])
        return results

    def store_intermediate_results(self, document_id: str, items: List[Dict], stage: str, agent: str) -> None:
        """Store intermediate results (clauses, partial analyses) into vector store."""
        texts = [it.get("text", "") for it in items]
        if not texts:
            return
        metas = []
        for idx, it in enumerate(items):
            metas.append({
                "document_id": document_id,
                "stage": stage,
                "agent": agent,
                "item_index": idx,
                "source_chunk_index": it.get("chunk_index", -1),
                "query": it.get("query", "")
            })
        if texts:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.vector_store.add_texts(texts=texts, metadatas=metas)
                    if self.vector_store_type == "chroma":
                        self.vector_store.persist()
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"[ERROR] Failed to store intermediate results after {max_retries} attempts: {e}")
                    else:
                        time.sleep(2 * (attempt + 1))

    def compliance_risk_pipeline(self, document_id: str, k: int = 5) -> Dict:
        clauses = self.extract_clauses_parallel(document_id, domains=["compliance"], k=k)["compliance"]
        self.store_intermediate_results(document_id, clauses, stage="extraction", agent="compliance")
        if clauses:
            contract_text = "\n\n".join([c["text"] for c in clauses])
        else:
            contract_text = self.parser.parse_document(self.documents[document_id]["file_path"])["text"]
            
        parallel = self.orchestrator.analyze_contract_parallel(contract_text, agent_roles=["compliance"])
        analyses = parallel.get("analyses", {})
        items = [{"text": v.get("analysis", ""), "query": "compliance-analysis", "chunk_index": -1} for v in analyses.values()]
        self.store_intermediate_results(document_id, items, stage="analysis", agent="compliance")
        return {"clauses": clauses, "analyses": analyses}

    def financial_risk_pipeline(self, document_id: str, k: int = 5) -> Dict:
        clauses = self.extract_clauses_parallel(document_id, domains=["finance"], k=k)["finance"]
        self.store_intermediate_results(document_id, clauses, stage="extraction", agent="finance")
        if clauses:
            contract_text = "\n\n".join([c["text"] for c in clauses])
        else:
            contract_text = self.parser.parse_document(self.documents[document_id]["file_path"])["text"]
            
        parallel = self.orchestrator.analyze_contract_parallel(contract_text, agent_roles=["finance"])
        items = [{"text": v.get("analysis", ""), "query": "finance-analysis", "chunk_index": -1} for v in parallel.get("analyses", {}).values()]
        self.store_intermediate_results(document_id, items, stage="analysis", agent="finance")
        return {"clauses": clauses, "analyses": parallel.get("analyses", {})}

    def simulate_multi_turn(self, document_id: str) -> Dict:
        parsed = self.parser.parse_document(self.documents[document_id]["file_path"])
        text = parsed["text"]
        comp = self.orchestrator.agents["compliance"].analyze(text, None)
        
        from langchain_core.messages import HumanMessage, SystemMessage
        finance_agent = self.orchestrator.agents["finance"]
        
        follow_msg = f"""Compliance Agent found the following risks:
{comp['analysis'][:1000]}

Based on these compliance findings, please assess the specific financial exposure related to penalties, remediation costs, and operational impact."""
        
        messages = [
            SystemMessage(content=finance_agent.system_prompt),
            HumanMessage(content=follow_msg)
        ]
        
        fin_resp = finance_agent.llm.invoke(messages)
        fin_analysis = fin_resp.content
        
        from prompt_templates import AgentRole, PromptTemplates
        second_msg = f"""Finance Agent raised these cost concerns:
{fin_analysis[:1000]}

Please provide specific compliance mitigation strategies that could reduce these financial risks."""

        compliance_agent = self.orchestrator.agents["compliance"]
        messages2 = [
            SystemMessage(content=compliance_agent.system_prompt),
            HumanMessage(content=second_msg)
        ]
        
        comp_resp = compliance_agent.llm.invoke(messages2)
        comp_analysis_2 = comp_resp.content

        return {
            "round1_compliance": comp["analysis"],
            "round1_finance": fin_analysis,
            "round2_compliance": comp_analysis_2
        }
