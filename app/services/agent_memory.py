from app.services.embeddings import embed_text, get_pinecone_index

def store_agent_result(doc_id: str, agent_name: str, result: dict):
    """
    Persist intermediate agent analysis to the vector store.
    Useful for multi-agent context retrieval and auditing.
    """
    content_text = str(result)
    embedding = embed_text(content_text)

    index = get_pinecone_index()
    if index is None:
        return

    try:
        index.upsert([
            {
                "id": f"{doc_id}_{agent_name}",
                "values": embedding,
                "metadata": {
                    "doc_id": doc_id,
                    "agent": agent_name,
                    "type": "agent_output",
                    "text": content_text
                }
            }
        ])
    except Exception as e:
        print(f"Error persisting agent result ({agent_name}): {e}")

def store_final_report(doc_id: str, report: dict):
    """
    Persist the final consolidated report.
    """
    content_text = str(report)
    embedding = embed_text(content_text)

    index = get_pinecone_index()
    if index is None:
        return

    try:
        index.upsert([
            {
                "id": f"{doc_id}_final_report",
                "values": embedding,
                "metadata": {
                    "doc_id": doc_id,
                    "type": "final_report",
                    "text": content_text
                }
            }
        ])
    except Exception as e:
        print(f"Error persisting final report: {e}")
