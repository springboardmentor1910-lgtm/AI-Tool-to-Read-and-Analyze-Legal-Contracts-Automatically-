from fastapi import FastAPI, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio
import uuid

from app.services.parser import parse_pdf
from app.services.classifier import classify_contract
from app.services.embeddings import store_embeddings
from app.services.retriever import retrieve_context
from app.services.report_generator import generate_report

from app.agents.legal_agent import legal_agent
from app.agents.finance_agent import finance_agent
from app.agents.compliance_agent import compliance_agent
from app.agents.operations_agent import operations_agent
from app.services.agent_memory import store_agent_result
from app.services.history_manager import add_action, get_history

app = FastAPI(title="ClauseSense AI")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Initialize systems and pre-load large models in the background
    to avoid blocking the main thread.
    """
    print("Initializing ClauseSense AI Backend...")
    
    async def load_models():
        from app.services.embeddings import get_model
        from app.services.classifier import get_classifier
        
        try:
            # We call these to trigger the lazy loading
            await asyncio.to_thread(get_model)
            await asyncio.to_thread(get_classifier)
            print("Successfully initialized AI models.")
        except Exception as e:
            print(f"Non-critical error during model warm-up: {e}")
    
    asyncio.create_task(load_models())

@app.get("/")
async def root():
    return {"status": "online", "name": "ClauseSense AI API"}

@app.post("/upload")
async def upload_contract(file: UploadFile, background_tasks: BackgroundTasks):
    # Get text from PDF
    text = await asyncio.to_thread(parse_pdf, file)
    
    # Run classification on the first few pages/paragraphs
    classification = await asyncio.to_thread(classify_contract, text[:2000])

    doc_id = str(uuid.uuid4())
    
    # Process embeddings in background
    background_tasks.add_task(store_embeddings, text, doc_id)

    add_action("UPLOAD", {
        "filename": file.filename,
        "doc_id": doc_id,
        "classification": classification
    })

    return {
        "status": "success",
        "doc_id": doc_id,
        "classification": classification,
        "preview": text[:500]
    }

@app.post("/analyze")
async def analyze_contract(
    doc_id: str,
    tone: str = "formal",
    focus: str = "full",
    structure: str = "structured"
):
    # Fetch relevant chunks from vector store
    context = await asyncio.to_thread(retrieve_context, doc_id)

    # Sequence of specialized agents
    # Legal analyzes first
    legal = await asyncio.to_thread(legal_agent, context)
    await asyncio.to_thread(store_agent_result, doc_id, "legal", legal)

    # Finance builds on legal
    finance = await asyncio.to_thread(finance_agent, context, legal)
    await asyncio.to_thread(store_agent_result, doc_id, "finance", finance)

    # Compliance checks both
    compliance = await asyncio.to_thread(compliance_agent, context, legal, finance)
    await asyncio.to_thread(store_agent_result, doc_id, "compliance", compliance)

    # Operations looks at the whole picture
    operations = await asyncio.to_thread(operations_agent, context, legal, finance, compliance)
    await asyncio.to_thread(store_agent_result, doc_id, "operations", operations)

    # Compile the final report
    report = generate_report(
        legal=legal,
        finance=finance,
        compliance=compliance,
        operations=operations,
        tone=tone,
        focus=focus,
        structure=structure
    )

    add_action("ANALYZE", {
        "doc_id": doc_id,
        "tone": tone,
        "focus": focus,
        "structure": structure
    })

    return {
        "doc_id": doc_id,
        "analysis": {
            "legal": legal,
            "finance": finance,
            "compliance": compliance,
            "operations": operations
        },
        "report": report
    }

@app.post("/batch-analyze")
async def batch_analyze(
    doc_ids: List[str],
    tone: str = "formal",
    focus: str = "full",
    structure: str = "structured"
):
    tasks = [analyze_contract(doc_id, tone, focus, structure) for doc_id in doc_ids]
    return await asyncio.gather(*tasks)

@app.post("/feedback")
async def submit_feedback(
    doc_id: str,
    rating: int,
    comments: Optional[str] = None
):
    # In production, we'd save this to a Postgres/Mongo instance
    print(f"User feedback for {doc_id}: {rating} stars - {comments}")
    
    add_action("FEEDBACK", {
        "doc_id": doc_id,
        "rating": rating,
        "comments": comments
    })
    
    return {"status": "success"}

@app.get("/history")
async def fetch_history():
    return get_history()
