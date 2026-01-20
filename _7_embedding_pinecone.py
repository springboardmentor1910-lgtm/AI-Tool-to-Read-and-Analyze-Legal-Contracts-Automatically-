from _1_env_auth import PINECONE_KEY
from _6_langgraph import db_clause

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import uuid

embedder = SentenceTransformer("intfloat/multilingual-e5-large")
pc = Pinecone(api_key=PINECONE_KEY)
index = pc.Index("legal-contracts-db5")

def embed(text):
    return embedder.encode(f"passage: {text}", normalize_embeddings=True).tolist()

def upsert_db():
    vectors = []
    for item in db_clause:
        vectors.append({
            "id": str(uuid.uuid4()),
            "values": embed(item["clause"]),
            "metadata": item,
        })
    if vectors:
        index.upsert(vectors=vectors)

def query_db(q, k=5):
    vec = embedder.encode(f"query: {q}", normalize_embeddings=True).tolist()
    return index.query(vector=vec, top_k=k, include_metadata=True)