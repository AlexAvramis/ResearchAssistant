import hashlib
import uuid

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.db.vector_store import get_vectorstore


def _file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def ingest_pdf(file_path: str, original_filename: str) -> dict:
    """Load a PDF, split into chunks, and store in the vector DB."""
    doc_id = _file_hash(file_path)

    loader = PyPDFLoader(file_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(pages)

    ids = []
    for i, chunk in enumerate(chunks):
        chunk.metadata["document_id"] = doc_id
        chunk.metadata["filename"] = original_filename
        chunk.metadata["chunk_index"] = i
        ids.append(f"{doc_id}_{i}")

    vs = get_vectorstore()
    vs.add_documents(chunks, ids=ids)

    return {"document_id": doc_id, "filename": original_filename, "num_chunks": len(chunks)}


def list_documents() -> list[dict]:
    """Return a list of ingested documents with metadata."""
    vs = get_vectorstore()
    collection = vs._collection
    result = collection.get(include=["metadatas"])

    docs: dict[str, dict] = {}
    for meta in result["metadatas"]:
        did = meta.get("document_id", "unknown")
        if did not in docs:
            docs[did] = {
                "document_id": did,
                "filename": meta.get("filename", "unknown"),
                "num_chunks": 0,
            }
        docs[did]["num_chunks"] += 1

    return list(docs.values())


def delete_document(document_id: str) -> bool:
    """Delete all chunks for a given document_id."""
    vs = get_vectorstore()
    collection = vs._collection
    result = collection.get(where={"document_id": document_id}, include=[])
    if not result["ids"]:
        return False
    collection.delete(ids=result["ids"])
    return True
