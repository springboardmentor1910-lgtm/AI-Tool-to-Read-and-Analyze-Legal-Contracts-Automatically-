# ingest.py
# Module 3: Serverless Ingestion (HuggingFace -> Pinecone)

import os
import time
from dotenv import load_dotenv
from tqdm import tqdm

# Loaders
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# The NEW Serverless Embeddings
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

# 1. Load Keys
load_dotenv()

def ingest_data():
    print("\n STARTING SERVERLESS INGESTION...")

    # 2. Check PDF
    pdf_path = "sample_contract.pdf"
    if not os.path.exists(pdf_path):
        print(f" Error: File '{pdf_path}' not found. Please add a PDF file.")
        return

    # 3. Load & Split
    print(f" Loading {pdf_path}...")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    all_docs = text_splitter.split_documents(documents)
    print(f"   - Created {len(all_docs)} text chunks.")

    # 4. Initialize Hugging Face Embeddings
    print("🧠 Connecting to Hugging Face Cloud (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        task="feature-extraction",
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    )

    # 5. Check Index Dimensions (CRITICAL STEP)
    # Hugging Face uses 384 dimensions. If your index is 768 (Google), we must reset it.
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME", "contract-db")

    existing_indexes = pc.list_indexes().names()
    
    if index_name in existing_indexes:
        index_info = pc.describe_index(index_name)
        if index_info.dimension != 384:
            print(f"⚠️ Index dimension mismatch ({index_info.dimension} vs 384). Recreating index...")
            pc.delete_index(index_name)
            time.sleep(10) # Wait for deletion
            pc.create_index(
                name=index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print("   - New Index Created.")
    else:
        print("   - Creating new Index...")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

    # 6. Upload to Pinecone
    print(f"☁️  Uploading {len(all_docs)} chunks to Pinecone...")
    
    batch_size = 32
    for i in tqdm(range(0, len(all_docs), batch_size), desc="   Processing Batches"):
        batch = all_docs[i : i + batch_size]
        try:
            PineconeVectorStore.from_documents(
                batch,
                index_name=index_name,
                embedding=embeddings
            )
        except Exception as e:
            print(f"   ⚠️ Batch failed: {e}")

    print("\n✅ SUCCESS! The Knowledge Base is ready.")

if __name__ == "__main__":
    ingest_data()