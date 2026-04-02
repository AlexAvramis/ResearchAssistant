import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";
import DocumentPanel from "./components/DocumentPanel";
import { getConversations } from "./api";

function generateId() {
  return Math.random().toString(36).substring(2, 10);
}

export default function App() {
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(generateId());
  const [showDocs, setShowDocs] = useState(false);

  const refreshConversations = () =>
    getConversations().then((r) => setConversations(r.data));

  useEffect(() => {
    refreshConversations();
  }, []);

  const handleNewChat = () => setActiveConv(generateId());

  return (
    <div className="app">
      <Sidebar
        conversations={conversations}
        activeId={activeConv}
        onSelect={setActiveConv}
        onNewChat={handleNewChat}
        onToggleDocs={() => setShowDocs((v) => !v)}
        refreshConversations={refreshConversations}
      />
      <main className="main">
        {showDocs ? (
          <DocumentPanel />
        ) : (
          <ChatPanel
            conversationId={activeConv}
            onMessageSent={refreshConversations}
          />
        )}
      </main>
    </div>
  );
}
