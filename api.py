# ---------------------------------------------------------
# FILE: api.py (FINAL PRODUCTION - ASYNC COMPATIBLE)
# ---------------------------------------------------------
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import uvicorn
import os
import shutil

# Import the graph and ingestion tool
from agent_graph import app as contract_agent_graph
from ingest_service import process_and_store_document

app = FastAPI(title="AI Legal Contract Agent API")

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def home():
    return {"status": "Online", "message": "AI Legal Agent is ready."}

# --- UPLOAD ENDPOINT ---
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    print(f"📥 RECEIVING FILE: {file.filename}")
    temp_file_path = f"temp_{file.filename}"
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        success = process_and_store_document(temp_file_path)
        
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        if success:
            return {"status": "success", "filename": file.filename}
        else:
            raise HTTPException(status_code=500, detail="Ingestion Failed")
            
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))

# --- ANALYZE ENDPOINT (ASYNC UPGRADE) ---
@app.post("/analyze")
async def analyze_contract(request: QueryRequest):
    print(f"📥 Received Query: {request.query}")
    try:
        # Initialize State
        inputs = {
            "user_query": request.query,
            "revision_number": 1,
            "messages": [],
            "plan": [],       
            "documents": [],
            "risk_score": 0,
            "risk_summary": "Pending...",
            "confidence_score": 0.0,
            "agent_reports": {},     
            "executive_summary": ""  
        }
        
        # --- THE FIX IS HERE ---
        # OLD WAY (Synchronous - Causes Error 500):
        # result = contract_agent_graph.invoke(inputs, config={"recursion_limit": 15})
        
        # NEW WAY (Asynchronous - Supports Parallelism):
        result = await contract_agent_graph.ainvoke(inputs, config={"recursion_limit": 15})
        
        # Response Construction
        return {
            "executive_summary": result.get("executive_summary", "Analysis complete."),
            "agent_reports": result.get("agent_reports", {}),
            "risk_score": result.get("risk_score", 0),
            "risk_summary": result.get("risk_summary", ""),
            "confidence_score": result.get("confidence_score", 0.0),
            "result": result.get("final_report", "") # Fallback for old UI
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 STARTING BACKEND SERVER...")
    uvicorn.run(app, host="127.0.0.1", port=8000)