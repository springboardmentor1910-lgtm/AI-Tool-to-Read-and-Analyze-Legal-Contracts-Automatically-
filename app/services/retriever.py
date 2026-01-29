from app.services.embeddings import get_pinecone_index, embed_text


_cached_query = None

def retrieve_context(doc_id: str, top_k: int = 5) -> str:
    global _cached_query
    index = get_pinecone_index()
    if index is None:
        return ""

    if _cached_query is None:
        _cached_query = embed_text("contract context")
        
    query_vector = _cached_query
    if not query_vector:
        return ""

    try:
        result = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            filter={
                "doc_id": doc_id,
                "type": {"$ne": "agent_output"}  # IMPORTANT
            }
        )
    except Exception as e:
        print(f"Retrieval error: {e}")
        return ""

    texts = []

    for match in result["matches"]:
        metadata = match.get("metadata", {})
        if "text" in metadata:
            texts.append(metadata["text"])

    return " ".join(texts)
