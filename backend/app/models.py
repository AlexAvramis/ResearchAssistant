from pydantic import BaseModel


class ChatRequest(BaseModel):
    conversation_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]
    conversation_id: str


class SummarizeRequest(BaseModel):
    document_id: str
    section: str | None = None


class SummarizeResponse(BaseModel):
    summary: str
    document_id: str


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    num_chunks: int


class ConversationInfo(BaseModel):
    conversation_id: str
    title: str
    message_count: int
