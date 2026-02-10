# ingest_service.py
# This is a TOOL that api.py can use to update the database automatically.

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

load_dotenv()

def process_and_store_document(file_path):
    """
    1. Wipes the database (Removes old ghosts like Khoros).
    2. Reads the new PDF.
    3. Uploads it to Pinecone.
    """
    try:
        print(f"🔄 STARTING INGESTION for: {file_path}")
        
        # A. WIPE OLD DATA (The Fix for 'Khoros')
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = os.getenv("PINECONE_INDEX_NAME")
        index = pc.Index(index_name)
        
        # Check if index contains data before deleting
        stats = index.describe_index_stats()
        if stats.total_vector_count > 0:
            index.delete(delete_all=True)
            print("   🗑️  Old memory wiped clean.")
        
        # B. LOAD & SPLIT NEW PDF
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)
        print(f"   📄 Processed {len(splits)} chunks from PDF.")

        # C. EMBED & STORE
        embeddings = HuggingFaceEndpointEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2",
            task="feature-extraction",
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        )
        
        PineconeVectorStore.from_documents(
            splits, 
            embeddings, 
            index_name=index_name
        )
        print("   ✅ SUCCESS: New document is live in memory.")
        return True

    except Exception as e:
        print(f"   ❌ INGESTION ERROR: {e}")
        return False