from fastapi import APIRouter, HTTPException

from app.models import ConversationInfo
from app.services.memory import list_conversations, get_history, delete_conversation

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/", response_model=list[ConversationInfo])
async def get_conversations():
    return [ConversationInfo(**c) for c in list_conversations()]


@router.get("/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    history = get_history(conversation_id)
    return {"conversation_id": conversation_id, "messages": history}


@router.delete("/{conversation_id}")
async def remove_conversation(conversation_id: str):
    if not delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"status": "deleted", "conversation_id": conversation_id}
