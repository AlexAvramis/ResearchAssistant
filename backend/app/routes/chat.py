from fastapi import APIRouter

from app.models import ChatRequest, ChatResponse, SummarizeRequest, SummarizeResponse
from app.services.rag import ask, summarize

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=ChatResponse)
async def chat_ask(req: ChatRequest):
    result = ask(req.conversation_id, req.question)
    return ChatResponse(**result)


@router.post("/summarize", response_model=SummarizeResponse)
async def chat_summarize(req: SummarizeRequest):
    result = summarize(req.document_id, req.section)
    return SummarizeResponse(**result)
