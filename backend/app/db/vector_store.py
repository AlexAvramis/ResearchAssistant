import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.config import settings

_embedding_fn = None
_vectorstore = None


def get_embedding_fn() -> OpenAIEmbeddings:
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
        )
    return _embedding_fn


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        client = chromadb.PersistentClient(path=str(settings.CHROMA_DIR))
        _vectorstore = Chroma(
            client=client,
            collection_name="research_docs",
            embedding_function=get_embedding_fn(),
        )
    return _vectorstore
