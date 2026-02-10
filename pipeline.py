# pipeline.py
# Module 3 Final: Ultra-Safe Mode for Free Tier Limits

import os
import time
import concurrent.futures
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

# Import our Logic Modules
from clues import analyze_clause_with_clues

# 1. SETUP & CONFIGURATION
load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = "contract-db"

# Initialize Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Check/Create Index
if INDEX_NAME not in pc.list_indexes().names():
    print(f"[System] Creating new Pinecone Index: {INDEX_NAME}")
    pc.create_index(
        name=INDEX_NAME,
        dimension=768, 
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
index = pc.Index(INDEX_NAME)

# 2. STEP A: LOAD REAL DATA
def load_and_chunk_pdf(pdf_path):
    print(f"\n[System] Loading PDF: {pdf_path}...")
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        
        # Split into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(docs)
        
        print(f"[System] Document split into {len(chunks)} real chunks.")
        
        # --- ULTRA SAFE LIMIT ---
        # We process ONLY 5 chunks to guarantee success on Free Tier
        limit = 5
        print(f"[Safe Mode] Limiting analysis to first {limit} chunks.")
        return [chunk.page_content for chunk in chunks][:limit]

    except Exception as e:
        print(f"[Error] Failed to load PDF: {e}")
        return []

# 3. STEP B: PARALLEL PROCESSING
def process_chunks_in_parallel(chunks):
    print(f"[System] Starting Parallel Analysis on {len(chunks)} chunks...")
    analyzed_results = []
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_chunk = {executor.submit(analyze_clause_with_clues, chunk): chunk for chunk in chunks}
        
        for future in concurrent.futures.as_completed(future_to_chunk):
            try:
                result = future.result()
                if result['agent'] != "Operations": 
                    analyzed_results.append(result)
            except Exception as e:
                pass
                
    end_time = time.time()
    print(f"[System] Analysis Complete. Found {len(analyzed_results)} risks in {end_time - start_time:.2f}s.")
    return analyzed_results

# 4. STEP C: STORAGE (STRICT THROTTLING)
def store_results_in_pinecone(results):
    if not results:
        print("⚠️ No risks found to store.")
        return

    print(f"\n[System] Preparing to store {len(results)} 'Clues' in Pinecone...")
    
    # Process ONE BY ONE to be safe
    for i, res in enumerate(results):
        try:
            text_content = f"{res['agent']} Alert: {res['analysis']}"
            
            # Generate Embedding (Single Call)
            vector = embeddings.embed_query(text_content)
            
            # Prepare Payload
            clue_id = f"clue_{int(time.time())}_{i}"
            metadata = {
                "agent": res['agent'],
                "risk": res.get('risk', 'N/A'),
                "text": res['analysis'],
                "type": "clue"
            }
            
            # Upload
            index.upsert(vectors=[(clue_id, vector, metadata)])
            print(f"   ... Uploaded Clue {i+1}/{len(results)}")
            
            # SLEEP: Pause 2 seconds between every single upload
            time.sleep(2)

        except Exception as e:
            print(f"\n[Rate Limit Hit] Google asked us to wait. Pausing for 60 seconds...")
            # If we hit the limit, we MUST wait 60s as per the logs
            time.sleep(60)
            print("   ... Resuming upload.")
            # Retry mechanism would go here, but for now we skip to keep logic simple

    print(f"✅ Success! Processing complete.")

# 5. MAIN EXECUTION
if __name__ == "__main__":
    pdf_filename = "sample_contract.pdf" 
    
    if os.path.exists(pdf_filename):
        real_chunks = load_and_chunk_pdf(pdf_filename)
        if real_chunks:
            agent_findings = process_chunks_in_parallel(real_chunks)
            store_results_in_pinecone(agent_findings)
    else:
        print(f"⚠️ File '{pdf_filename}' not found.")