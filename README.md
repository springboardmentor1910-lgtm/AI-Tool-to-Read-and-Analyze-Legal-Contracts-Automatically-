# AI-Tool-to-Read-and-Analyze-Legal-Contracts-Automatically-
# ClauseSense AI

ClauseSense AI is a contract analysis platform that uses multi-agent orchestration to review legal agreements. The system breaks down documents and analyzes them across four domains: Legal, Finance, Compliance, and Operations.

## Features

- **Multi-Agent Architecture**: Uses specialized agents to perform deep-dive analysis on different aspects of a contract.
- **Context-Aware Retrieval**: Powered by Pinecone and Sentence Transformers for accurate semantic search across large documents.
- **Customizable Reports**: Support for different tones (Formal, Concise, Executive) and structures based on stakeholder needs.
- **Asynchronous Processing**: Handles heavy lifting (embeddings, LLM calls) in background tasks to maintain UI responsiveness.

## Tech Stack

- **Backend**: Python (FastAPI), LangChain, LangGraph, SentenceTransformers (HuggingFace), Pinecone.
- **Frontend**: React, Vite, Framer Motion, Lucide Icons.
- **Database**: Pinecone (Vector Store), Local JSON (Action History).

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- [Pinecone](https://www.pinecone.io/) API Key

### Backend
1. Clone the repository.
2. Create environment: `python -m venv venv` and activate it.
3. Install dependencies: `pip install -r requirements.txt`.
4. Setup `.env`:
   ```env
   PINECONE_API_KEY=your_key
   PINECONE_INDEX=clausesense
   ```
5. Run server: `uvicorn app.main:app --reload --port 8001`

### Frontend
1. Navigate to `/frontend`.
2. Install dependencies: `npm install`.
3. Run dev server: `npm run dev -- --port 5174`.

## API Endpoints

- `POST /upload`: Upload PDF and generate embeddings.
- `POST /analyze`: Run multi-agent analysis on a document.
- `POST /batch-analyze`: Concurrent analysis for multiple docs.
- `GET /history`: Fetch activity logs.
- `POST /feedback`: Submit user ratings for analysis quality.
