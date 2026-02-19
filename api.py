"""FastAPI endpoints for contract upload and domain classification."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import Optional, Dict, Any
import tempfile
import os
from pathlib import Path
from contract_analyzer import ContractAnalyzer
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Contract Analysis API",
    description="API for contract upload, domain classification, and analysis",
    version="1.0.0"
)

analyzer = ContractAnalyzer(use_free_model=True)


@app.get("/")
async def root():
    return {
        "message": "Contract Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/v1/upload",
            "classify": "/api/v1/classify",
            "analyze": "/api/v1/analyze",
            "health": "/api/v1/health"
        }
    }


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "service": "contract-analysis-api"}


@app.post("/api/v1/upload")
async def upload_contract(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and process a contract document.
    
    Args:
        file: Contract file (PDF, DOCX, or TXT)
    
    Returns:
        Document ID and metadata
    """
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.pdf', '.docx', '.txt']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported: .pdf, .docx, .txt"
        )
    
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / file.filename
    
    counter = 1
    while file_path.exists():
        stem = Path(file.filename).stem
        file_path = upload_dir / f"{stem}_{counter}{file_ext}"
        counter += 1
        
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        document_id = analyzer.upload_document(str(file_path))
        doc_info = analyzer.documents.get(document_id, {})
        
        return {
            "success": True,
            "document_id": document_id,
            "filename": file.filename,
            "metadata": doc_info.get("metadata", {}),
            "message": "Document uploaded and processed successfully"
        }
    except Exception as e:
        if file_path.exists():
            os.unlink(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.post("/api/v1/classify")
async def classify_contract(
    document_id: Optional[str] = None,
    file: Optional[UploadFile] = File(None)
) -> Dict[str, Any]:
    """
    Classify contract domain and generate analysis plan.
    
    Args:
        document_id: ID of previously uploaded document (optional)
        file: Contract file to classify (optional, if document_id not provided)
    
    Returns:
        Domain classification and analysis plan
    """
    if document_id:
        if document_id not in analyzer.documents:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
        classification = analyzer.classify_domain(document_id)
    elif file:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.pdf', '.docx', '.txt']:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(await file.read())
            tmp_path = tmp_file.name
        try:
            doc_id = analyzer.upload_document(tmp_path)
            classification = analyzer.classify_domain(doc_id)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    else:
        raise HTTPException(status_code=400, detail="Either document_id or file must be provided")
    
    return {
        "success": True,
        "domain": classification.get("domain", "Unknown"),
        "domain_confidence": classification.get("domain_confidence", "medium"),
        "analysis_plan": classification.get("analysis_plan", {}),
        "coordination_points": classification.get("coordination_points", [])
    }


@app.post("/api/v1/analyze")
async def analyze_contract(
    document_id: str,
    agent_roles: Optional[str] = None,
    fast: Optional[bool] = False
) -> Dict[str, Any]:
    """
    Analyze a contract using AI agents.
    
    Args:
        document_id: ID of the document to analyze
        agent_roles: Comma-separated list of agent roles (optional, default: all)
    
    Returns:
        Analysis results from all agents
    """
    if document_id not in analyzer.documents:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    roles_list = None
    if agent_roles:
        roles_list = [r.strip() for r in agent_roles.split(",")]
        valid_roles = ["compliance", "finance", "legal", "operations"]
        invalid_roles = [r for r in roles_list if r not in valid_roles]
        if invalid_roles:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid agent roles: {invalid_roles}. Valid: {valid_roles}"
            )
    
    try:
        if fast:
            doc_info = analyzer.documents[document_id]
            parsed = analyzer.parser.parse_document(doc_info["file_path"])
            full_text = parsed["text"]
            roles = roles_list or ["compliance", "finance", "legal", "operations"]
            results = analyzer.orchestrator.analyze_contract_parallel(full_text, roles)
            return {
                "success": True,
                "document_id": document_id,
                "domain": None,
                "analyses": results.get("analyses", {}),
                "coordination_messages": results.get("coordination_messages", []),
                "completed_agents": results.get("completed_agents", []),
                "planning_info": {}
            }
        else:
            results = analyzer.analyze_contract(document_id, roles_list)
            return {
                "success": True,
                "document_id": document_id,
                "domain": results.get("domain", "Unknown"),
                "analyses": results.get("analyses", {}),
                "coordination_messages": results.get("coordination_messages", []),
                "completed_agents": results.get("completed_agents", []),
                "planning_info": results.get("planning_info", {})
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing contract: {str(e)}")


@app.get("/api/v1/documents/{document_id}")
async def get_document_info(document_id: str) -> Dict[str, Any]:
    """
    Get information about an uploaded document.
    
    Args:
        document_id: ID of the document
    
    Returns:
        Document metadata and information
    """
    if document_id not in analyzer.documents:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    doc_info = analyzer.documents[document_id]
    
    return {
        "success": True,
        "document_id": document_id,
        "metadata": doc_info.get("metadata", {}),
        "num_chunks": doc_info.get("num_chunks", 0),
        "text_length": doc_info.get("text_length", 0)
    }


@app.get("/api/v1/documents")
async def list_documents() -> Dict[str, Any]:
    """
    List all uploaded documents.
    
    Returns:
        List of document IDs and metadata
    """
    documents = []
    for doc_id, doc_info in analyzer.documents.items():
        documents.append({
            "document_id": doc_id,
            "filename": doc_info.get("metadata", {}).get("file_name", "Unknown"),
            "file_type": doc_info.get("metadata", {}).get("file_type", "Unknown"),
            "text_length": doc_info.get("text_length", 0)
        })
    
    return {
        "success": True,
        "count": len(documents),
        "documents": documents
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
