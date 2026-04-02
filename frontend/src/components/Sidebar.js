import React from "react";
import { deleteConversation } from "../api";

export default function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNewChat,
  onToggleDocs,
  refreshConversations,
}) {
  const handleDelete = async (e, id) => {
    e.stopPropagation();
    await deleteConversation(id);
    refreshConversations();
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Research Assistant</h2>
        <button className="sidebar-btn" onClick={onNewChat}>
          + New Chat
        </button>
        <button className="sidebar-btn secondary" onClick={onToggleDocs}>
          Documents
        </button>
      </div>
      <div className="conv-list">
        {conversations.map((c) => (
          <div
            key={c.conversation_id}
            className={`conv-item ${c.conversation_id === activeId ? "active" : ""}`}
            onClick={() => onSelect(c.conversation_id)}
            title={c.title}
          >
            {c.title || "Untitled"}
          </div>
        ))}
      </div>
    </aside>
  );
}
