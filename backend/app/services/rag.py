"""Core RAG pipeline: retrieval-augmented generation with conversation memory."""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.db.vector_store import get_vectorstore
from app.services import memory as mem


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
        temperature=0.2,
    )


_QA_SYSTEM = """\
You are an AI Research Assistant. Answer the user's question using ONLY the \
provided context from uploaded documents. If the context does not contain \
enough information, say so honestly. Cite the source filename and page when possible.

Context:
{context}
"""

_SUMMARIZE_SYSTEM = """\
You are an AI Research Assistant. Summarize the following document content \
clearly and concisely. Preserve key findings, methods, and conclusions.

Content:
{context}
"""


def _history_to_messages(history: list[dict]):
    msgs = []
    for m in history:
        if m["role"] == "user":
            msgs.append(HumanMessage(content=m["content"]))
        else:
            msgs.append(AIMessage(content=m["content"]))
    return msgs


def ask(conversation_id: str, question: str) -> dict:
    """Answer a question using RAG + conversation memory."""
    vs = get_vectorstore()
    retriever = vs.as_retriever(search_kwargs={"k": settings.TOP_K})

    # Retrieve relevant chunks
    docs = retriever.invoke(question)
    context = "\n\n---\n\n".join(
        f"[{d.metadata.get('filename', '?')} p.{d.metadata.get('page', '?')}]\n{d.page_content}"
        for d in docs
    )

    sources = [
        {
            "filename": d.metadata.get("filename", ""),
            "page": d.metadata.get("page", ""),
            "snippet": d.page_content[:200],
        }
        for d in docs
    ]

    # Build prompt with history
    history = mem.get_history(conversation_id)
    prompt = ChatPromptTemplate.from_messages([
        ("system", _QA_SYSTEM),
        MessagesPlaceholder("history"),
        ("human", "{question}"),
    ])

    chain = prompt | _get_llm() | StrOutputParser()
    answer = chain.invoke({
        "context": context,
        "history": _history_to_messages(history),
        "question": question,
    })

    # Persist to memory
    mem.add_message(conversation_id, "user", question)
    mem.add_message(conversation_id, "assistant", answer)

    return {"answer": answer, "sources": sources, "conversation_id": conversation_id}


def summarize(document_id: str, section: str | None = None) -> dict:
    """Summarize a document (or a section of it)."""
    vs = get_vectorstore()
    collection = vs._collection

    where_filter = {"document_id": document_id}
    result = collection.get(where=where_filter, include=["documents", "metadatas"])

    if not result["documents"]:
        return {"summary": "No document found with that ID.", "document_id": document_id}

    # Sort by chunk index
    pairs = list(zip(result["documents"], result["metadatas"]))
    pairs.sort(key=lambda x: x[1].get("chunk_index", 0))

    if section:
        # Filter chunks that mention the section keyword
        section_lower = section.lower()
        pairs = [(doc, meta) for doc, meta in pairs if section_lower in doc.lower()]

    context = "\n\n".join(doc for doc, _ in pairs[:20])  # cap to avoid token overflow

    prompt = ChatPromptTemplate.from_messages([
        ("system", _SUMMARIZE_SYSTEM),
        ("human", "Please provide a comprehensive summary."),
    ])

    chain = prompt | _get_llm() | StrOutputParser()
    summary = chain.invoke({"context": context})

    return {"summary": summary, "document_id": document_id}
