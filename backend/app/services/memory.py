"""Conversation memory backed by a simple JSON file store."""
import json
import time
from pathlib import Path

from app.config import settings

_MEMORY_DIR = settings.BASE_DIR / "memory"
_MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def _conv_path(conversation_id: str) -> Path:
    safe_id = "".join(c for c in conversation_id if c.isalnum() or c in "-_")
    return _MEMORY_DIR / f"{safe_id}.json"


def _load(conversation_id: str) -> dict:
    p = _conv_path(conversation_id)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {
        "conversation_id": conversation_id,
        "title": "",
        "messages": [],
    }


def _save(data: dict) -> None:
    p = _conv_path(data["conversation_id"])
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def add_message(conversation_id: str, role: str, content: str) -> None:
    data = _load(conversation_id)
    data["messages"].append({"role": role, "content": content, "ts": time.time()})
    # Auto-title from first user message
    if not data["title"] and role == "user":
        data["title"] = content[:80]
    # Trim old messages but keep the system prompt-worthy first few
    if len(data["messages"]) > settings.MAX_MEMORY_MESSAGES:
        data["messages"] = data["messages"][-settings.MAX_MEMORY_MESSAGES:]
    _save(data)


def get_history(conversation_id: str) -> list[dict]:
    data = _load(conversation_id)
    return data["messages"]


def list_conversations() -> list[dict]:
    results = []
    for p in _MEMORY_DIR.glob("*.json"):
        data = json.loads(p.read_text(encoding="utf-8"))
        results.append({
            "conversation_id": data["conversation_id"],
            "title": data.get("title", ""),
            "message_count": len(data.get("messages", [])),
        })
    return sorted(results, key=lambda x: x["message_count"], reverse=True)


def delete_conversation(conversation_id: str) -> bool:
    p = _conv_path(conversation_id)
    if p.exists():
        p.unlink()
        return True
    return False
