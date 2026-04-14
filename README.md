# AI Research Assistant

RAG-based research assistant that lets you upload PDFs and ask questions about them. It retrieves relevant chunks from your documents, passes them as context to an LLM, and gives grounded answers with source citations. Conversations are persisted so you can pick up where you left off.

## Architecture

```
┌─────────────┐      HTTP       ┌──────────────────────────────────┐
│  React UI   │  ◄────────────► │  FastAPI Backend                 │
│  port 3000  │                 │  port 8000                       │
└─────────────┘                 │                                  │
                                │  ┌────────────┐  ┌────────────┐  │
                                │  │ LangChain  │  │ ChromaDB   │  │
                                │  │ + OpenAI   │  │ VectorStore│  │
                                │  └────────────┘  └────────────┘  │
                                │  ┌────────────┐                  │
                                │  │ Conv.      │                  │
                                │  │ Memory     │                  │
                                │  └────────────┘                  │
                                └──────────────────────────────────┘
```

## What it does

- Upload PDFs → chunks them and indexes embeddings into ChromaDB
- Ask questions → retrieves relevant chunks, feeds them to the LLM, returns answer + source citations
- Summarize documents or specific sections
- Conversation history is stored per session (JSON-backed)
- Multiple conversations, switchable from the sidebar

## Stack

| Layer          | Technology                       |
|----------------|----------------------------------|
| Frontend       | React 18                         |
| Backend        | FastAPI + Uvicorn                |
| LLM            | OpenAI (`gpt-4o-mini`) via LangChain |
| Embeddings     | `text-embedding-3-small`         |
| Vector DB      | ChromaDB (persistent, local)     |
| PDF parsing    | PyPDF + LangChain text splitters |
| Memory         | JSON file store                  |

## Setup

**Requirements:** Python 3.10+, Node.js 18+, OpenAI API key with billing

Two terminals are needed — backend and frontend run as separate processes.

### Backend (Terminal 1)

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

copy .env.example .env       # then edit .env and add your OPENAI_API_KEY
python run.py                # runs on :8000
```

### Frontend (Terminal 2)

```bash
cd frontend
npm install      # first time only
npm start        # runs on :3000
```

Start the backend first. Swagger docs are at `http://localhost:8000/docs`.

## API

| Method | Endpoint                              | Description               |
|--------|---------------------------------------|---------------------------|
| GET    | `/api/health`                         | Health check              |
| POST   | `/api/documents/upload`               | Upload a PDF              |
| GET    | `/api/documents/`                     | List all documents        |
| DELETE | `/api/documents/{document_id}`        | Delete a document         |
| POST   | `/api/chat/ask`                       | Ask a question (RAG)      |
| POST   | `/api/chat/summarize`                 | Summarize a document      |
| GET    | `/api/conversations/`                 | List conversations        |
| GET    | `/api/conversations/{id}/history`     | Get conversation history  |
| DELETE | `/api/conversations/{id}`             | Delete a conversation     |

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, router setup
│   ├── config.py            # env-based settings
│   ├── models.py            # Pydantic request/response schemas
│   ├── db/
│   │   └── vector_store.py  # ChromaDB client + embeddings
│   ├── routes/
│   │   ├── chat.py          # /ask and /summarize
│   │   ├── conversations.py # CRUD for conversation history
│   │   └── documents.py     # PDF upload, list, delete
│   └── services/
│       ├── ingestion.py     # PDF → chunks → vector store
│       ├── memory.py        # JSON-backed conversation memory
│       └── rag.py           # retrieval chain + LLM calls
├── requirements.txt
├── .env.example
└── run.py

frontend/
├── src/
│   ├── App.js / App.css
│   ├── api.js               # axios wrapper for all endpoints
│   └── components/
│       ├── ChatPanel.js     # chat UI with markdown rendering
│       ├── DocumentPanel.js # upload, list, summarize, delete
│       └── Sidebar.js       # conversations list + nav
└── package.json
```

## Config

`backend/.env`:

| Variable         | Default                  |
|------------------|--------------------------|
| `OPENAI_API_KEY` | *(required)*             |
| `LLM_MODEL`      | `gpt-4o-mini`            |
| `EMBEDDING_MODEL` | `text-embedding-3-small` |

Chunking params (`CHUNK_SIZE`, `CHUNK_OVERLAP`, `TOP_K`) can be changed in `backend/app/config.py`.

## Local LLM

To swap in a local model (e.g. Ollama), replace `ChatOpenAI` with `ChatOllama` in `services/rag.py` and use a local embedding model in `db/vector_store.py`.
