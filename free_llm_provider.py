"""Free LLM provider support."""
import os
from dotenv import load_dotenv

load_dotenv()


class FreeLLMProvider:
    """Manages free LLM providers."""
    
    @staticmethod
    def get_free_llm():
        """Get a free LLM provider. Tries Groq first, then Hugging Face."""
        if os.getenv("DISABLE_EXTERNAL_LLM", "0") == "1":
            print("⚙️  External LLMs disabled via env; using DummyLLM.")
        else:
            groq_api_key = os.getenv("GROQ_API_KEY")
            if groq_api_key:
                try:
                    from langchain_groq import ChatGroq
                    llm = ChatGroq(
                        model="llama-3.1-8b-instant",
                        temperature=0.3,
                        groq_api_key=groq_api_key
                    )
                    print("✅ Using Groq (free tier)")
                    return llm
                except ImportError:
                    print("⚠️  Groq not installed")
                except Exception as e:
                    print(f"⚠️  Groq failed: {e}")
            
            hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
            if hf_token:
                try:
                    from langchain_huggingface import ChatHuggingFace
                    llm = ChatHuggingFace(
                        model_id="mistralai/Mistral-7B-Instruct-v0.2",
                        huggingface_api_token=hf_token,
                        temperature=0.3,
                        timeout=60
                    )
                    print("✅ Using Hugging Face (free tier)")
                    return llm
                except ImportError:
                    print("⚠️  Hugging Face not installed")
                except Exception as e:
                    print(f"⚠️  Hugging Face failed: {e}")
            
            try:
                try:
                    from langchain_ollama import ChatOllama
                except ImportError:
                    from langchain_community.chat_models import ChatOllama
                    
                llm = ChatOllama(model="llama3.1", temperature=0.3)
                from langchain_core.messages import HumanMessage
                llm.invoke([HumanMessage(content="test")])
                print("✅ Using Ollama (local)")
                return llm
            except Exception as e:
                print(f"⚠️  Ollama failed: {e}")
                print("   (Make sure Ollama is installed and running: https://ollama.com/)")
        
        try:
            from langchain_core.messages import AIMessage
        except Exception:
            AIMessage = None
        
        class DummyLLM:
            """Lightweight offline LLM for validation without external providers."""
            def invoke(self, messages):
                human_contents = [m.content for m in messages if hasattr(m, "content")]
                prompt_text = human_contents[-1] if human_contents else ""
                if "Respond in JSON format" in prompt_text or "Create an analysis plan" in prompt_text or "Contract Excerpt" in prompt_text:
                    text_lower = prompt_text.lower()
                    domain = "General Business"
                    if any(kw in text_lower for kw in ["software", "it", "technology", "api", "system", "service level", "sla"]):
                        domain = "Technology/IT Services"
                    elif any(kw in text_lower for kw in ["health", "medical", "patient", "hipaa"]):
                        domain = "Healthcare/Medical"
                    elif any(kw in text_lower for kw in ["financial", "bank", "loan", "payment", "currency", "price"]):
                        domain = "Financial Services"
                    elif any(kw in text_lower for kw in ["manufacturing", "supply", "production", "inventory"]):
                        domain = "Manufacturing/Supply Chain"
                    elif any(kw in text_lower for kw in ["property", "real estate", "lease", "rent"]):
                        domain = "Real Estate"
                    elif any(kw in text_lower for kw in ["employee", "employment", "labor", "worker"]):
                        domain = "Employment/Labor"
                    content = (
                        '{'
                        f'"domain": "{domain}",'
                        '"domain_confidence": "medium",'
                        '"agents": {'
                        '"compliance": {"priority": "high", "focus_areas": ["regulatory compliance", "industry standards"], "dependencies": ["legal"]},'
                        '"finance": {"priority": "high", "focus_areas": ["payment terms", "pricing", "financial obligations"], "dependencies": []},'
                        '"legal": {"priority": "high", "focus_areas": ["legal terms", "liability", "intellectual property"], "dependencies": []},'
                        '"operations": {"priority": "medium", "focus_areas": ["service levels", "delivery", "operational requirements"], "dependencies": []}'
                        '},'
                        '"analysis_sequence": ["compliance", "finance", "legal", "operations"],'
                        '"coordination_points": ["Share compliance findings with legal", "Cross-reference financial terms with operations"]'
                        '}'
                    )
                else:
                    content = "This is an offline validation response synthesizing the provided context and prompts."
                if AIMessage is not None:
                    return AIMessage(content=content)
                class Response:
                    pass
                r = Response()
                r.content = content
                return r
        
        print("✅ Using DummyLLM (offline fallback)")
        return DummyLLM()
