<<<<<<< HEAD
# Contract Analysis System

AI-powered contract analysis with 4 specialized agents: Compliance, Finance, Legal, and Operations.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` with API keys:**
   ```
   GROQ_API_KEY=your_groq_key_here
   PINECONE_API_KEY=your_pinecone_key_here
   PINECONE_INDEX_NAME=contract-analysis-free
   HUGGINGFACE_API_TOKEN=your_hf_token_here
   ```

   - Get Groq key (free): https://console.groq.com/
   - Get Pinecone key (free): https://app.pinecone.io/
   - Get Hugging Face token (free): https://huggingface.co/settings/tokens

3. **Verify Setup:**
   Run the verification script to check your environment:
   ```bash
   python verify_setup.py
   ```

4. **Run Experiment:**
   Run the analysis on a sample contract:
   ```bash
   python run_experiment.py
   ```
   This will analyze `experiments/sample_contract.txt` and save the results to `experiments/analysis_result.json`.

5. **Run the app:**
   ```bash
   streamlit run app.py
   ```
   
   Or: `python -m streamlit run app.py`

6. **Upload and analyze:**
   - Upload PDF, DOCX, or TXT file
   - Click "Analyze Contract"
   - View results from all 4 agents

## Features

### Milestone 1 (Completed)
- ✅ 4 AI Agents: Compliance, Finance, Legal, Operations
- ✅ Free AI models (Groq default, Hugging Face fallback)
- ✅ Supports PDF, DOCX, TXT
- ✅ Clean web UI with history and semantic search (Pinecone integration)

### Milestone 2 (Completed)
- ✅ **Planning Module**: Generates and coordinates specialized agents based on contract domain
- ✅ **API Integration**: RESTful API endpoints for contract upload and domain classification
- ✅ **Prompt Templates**: Structured prompt templates for agent communication
- ✅ **LangGraph Coordination**: Inter-agent coordination using LangGraph workflow
- ✅ **Vector Search**: Pinecone integration for efficient contract chunk retrieval

## API Endpoints

The system includes a FastAPI server for programmatic access:

### Start API Server
```bash
python api.py
# Or: uvicorn api:app --reload
```

### Available Endpoints

- `GET /` - API information
- `GET /api/v1/health` - Health check
- `POST /api/v1/upload` - Upload contract document
- `POST /api/v1/classify` - Classify contract domain and generate analysis plan
- `POST /api/v1/analyze` - Analyze contract with AI agents
- `GET /api/v1/documents` - List all uploaded documents
- `GET /api/v1/documents/{document_id}` - Get document information



## Validation

Run the validation script to test LangGraph coordination:

```bash
python validate_langgraph.py
```

This will validate:
- Planning Module functionality
- Prompt template generation
- LangGraph graph structure
- Full integration (upload, classify, analyze)
- Inter-agent communication

## Project Structure

```
.
├── app.py                 # Streamlit UI
├── api.py                 # FastAPI REST endpoints
├── contract_analyzer.py   # Main analyzer with planning integration
├── agents.py              # AI agents with LangGraph coordination
├── planning_module.py     # Planning module for agent coordination
├── prompt_templates.py    # Structured prompt templates
├── document_parser.py     # Document parsing
├── free_llm_provider.py   # Free model support (Groq/HF/Ollama)
├── validate_langgraph.py  # Validation script for Milestone 2
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Architecture

### Planning Module
The `PlanningModule` classifies contracts by domain and generates analysis plans:
- Domain classification (Technology, Healthcare, Financial, etc.)
- Agent priority determination
- Analysis sequence planning
- Coordination strategy definition

### LangGraph Coordination
The `AgentOrchestrator` uses LangGraph to coordinate agents:
- Sequential workflow: Compliance → Finance → Legal → Operations → Coordinate
- State management with shared context
- Inter-agent message passing
- Result synthesis

### Prompt Templates
Structured templates for:
- System prompts for each agent role
- Analysis prompts with role-specific instructions
- Planning prompts for domain classification
- Coordination prompts for result synthesis
- Inter-agent communication messages
