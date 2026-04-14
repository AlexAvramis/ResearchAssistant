# AI Research Assistant (RAG System with Memory)

Upload PDFs (papers, notes, docs) and interact with an AI that answers questions grounded in your documents, summarizes sections, and remembers previous conversations.

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

## Features

- **PDF Upload & Indexing** — Upload PDF files; they are chunked and embedded into ChromaDB.
- **RAG Q&A** — Ask questions and get answers grounded in your uploaded documents with source citations.
- **Document Summarization** — Summarize entire documents or specific sections.
- **Conversation Memory** — The assistant remembers previous messages within a conversation.
- **Multi-conversation** — Create and switch between multiple chat sessions.

## Tech Stack

| Layer          | Technology                       |
|----------------|----------------------------------|
| Frontend       | React 18                         |
| Backend API    | FastAPI + Uvicorn                |
| LLM            | OpenAI (gpt-4o-mini) via LangChain |
| Embeddings     | OpenAI text-embedding-3-small    |
| Vector DB      | ChromaDB (persistent, local)     |
| PDF Processing | PyPDF + LangChain text splitters |
| Memory         | JSON file-based conversation store |

## Quick Start

> **You need two separate terminals** — one for the backend and one for the frontend.
> Both processes run continuously, so they cannot share a terminal.
> Start the backend first, then the frontend.

### 1. Backend (Terminal 1)

```bash
cd ResearchAssistant/backend

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
# Edit .env and add your OPENAI_API_KEY

# Run the server
python run.py
# Keep this terminal open — wait for "Uvicorn running on http://0.0.0.0:8000"
```

The API will be available at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### 2. Frontend (Terminal 2)

```bash
cd ResearchAssistant/frontend

# Install dependencies (first time only)
npm install

# Start the dev server
npm start
# Keep this terminal open — opens browser automatically
```

Opens at `http://localhost:3000`. The backend must be running before you use the frontend.

## API Endpoints

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
ResearchAssistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Settings (env vars)
│   │   ├── models.py            # Pydantic schemas
│   │   ├── db/
│   │   │   └── vector_store.py  # ChromaDB setup
│   │   ├── routes/
│   │   │   ├── chat.py          # Q&A and summarize endpoints
│   │   │   ├── conversations.py # Conversation management
│   │   │   └── documents.py     # PDF upload & management
│   │   └── services/
│   │       ├── ingestion.py     # PDF loading & chunking
│   │       ├── memory.py        # Conversation memory
│   │       └── rag.py           # RAG pipeline
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/
│   ├── public/index.html
│   ├── src/
│   │   ├── App.js               # Main app layout
│   │   ├── App.css              # Styles
│   │   ├── api.js               # API client
│   │   ├── index.js
│   │   └── components/
│   │       ├── ChatPanel.js     # Chat interface
│   │       ├── DocumentPanel.js # Document management
│   │       └── Sidebar.js       # Navigation sidebar
│   └── package.json
├── .gitignore
└── README.md
```

## Configuration

Edit `backend/.env`:

| Variable         | Default                  | Description          |
|------------------|--------------------------|----------------------|
| `OPENAI_API_KEY` | *(required)*             | Your OpenAI API key  |
| `LLM_MODEL`      | `gpt-4o-mini`            | Chat model to use    |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model      |

You can also tune chunking and retrieval parameters in `backend/app/config.py`.

## Using a Local LLM

To use a local model (e.g., via Ollama), swap `ChatOpenAI` for `ChatOllama` in `services/rag.py` and `OpenAIEmbeddings` for a local embedding model in `db/vector_store.py`. LangChain makes this a one-line change.
