import os
import socket
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

# Global state for connection reusing
_model = None
_index = None
_pc = None

def get_model():
    global _model
    if _model is None:
        try:
            print("Loading embedding model (all-MiniLM-L6-v2)...")
            
            # Set a request timeout for model download
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(60) 
            
            try:
                _model = SentenceTransformer("all-MiniLM-L6-v2")
                print("Embedding model loaded.")
            finally:
                socket.setdefaulttimeout(original_timeout)
                
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            return None
    return _model

def get_pinecone_index():
    global _index, _pc
    if _index is None:
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX")
        
        if not api_key or not index_name:
            print("Pinecone configuration missing in .env")
            return None

        try:
            print(f"Connecting to Pinecone index: {index_name}")
            
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(30)
            
            try:
                if _pc is None:
                    _pc = Pinecone(api_key=api_key)
                
                # Verify index exists
                indexes = [i.name for i in _pc.list_indexes()]
                if index_name not in indexes:
                    print(f"Index {index_name} not found. Creating...")
                    _pc.create_index(
                        name=index_name,
                        dimension=384,
                        metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1")
                    )
                
                _index = _pc.Index(index_name)
                print("Pinecone connection established.")
            finally:
                socket.setdefaulttimeout(original_timeout)
                
        except Exception as e:
            print(f"Failed to connect to Pinecone: {e}")
            return None
    return _index

def embed_text(text: str):
    model = get_model()
    if model is None:
        return []
    return model.encode(text).tolist()

def store_embeddings(text: str, doc_id: str):
    """
    Chunks text and stores embeddings in Pinecone.
    """
    index = get_pinecone_index()
    model = get_model()
    
    if index is None or model is None:
        return

    # Chunking logic
    chunk_size = 800 
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    if not chunks:
        return

    print(f"Storing {len(chunks)} chunks for {doc_id}...")

    try:
        # Batch encode for performance
        embeddings = model.encode(chunks, batch_size=64, show_progress_bar=False)
        
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vectors.append({
                "id": f"{doc_id}_{i}",
                "values": embedding.tolist(),
                "metadata": {
                    "doc_id": doc_id,
                    "type": "contract_chunk",
                    "text": chunk
                }
            })

        # Batch upsert (Pinecone limit is usually ~100-200 vectors per request)
        for j in range(0, len(vectors), 100):
            batch = vectors[j:j+100]
            index.upsert(batch)
            
        print(f"Successfully indexed {doc_id}")
    except Exception as e:
        print(f"Indexing error for {doc_id}: {e}")
