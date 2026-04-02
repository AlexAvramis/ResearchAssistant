import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { askQuestion, getConversationHistory } from "../api";

export default function ChatPanel({ conversationId, onMessageSent }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    getConversationHistory(conversationId)
      .then((r) => setMessages(r.data.messages || []))
      .catch(() => setMessages([]));
  }, [conversationId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const q = input.trim();
    if (!q || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);

    try {
      const res = await askQuestion(conversationId, q);
      const { answer, sources } = res.data;
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: answer, sources },
      ]);
      onMessageSent();
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error: " + (err.response?.data?.detail || err.message) },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  if (messages.length === 0 && !loading) {
    return (
      <div className="chat-panel">
        <div className="empty-state">
          <h3>AI Research Assistant</h3>
          <p>Upload PDFs and ask questions about your documents.</p>
        </div>
        <div className="chat-input-bar">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask a question about your documents..."
          />
          <button onClick={send} disabled={loading}>
            Send
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-panel">
      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            {m.role === "assistant" ? (
              <ReactMarkdown>{m.content}</ReactMarkdown>
            ) : (
              m.content
            )}
            {m.sources && m.sources.length > 0 && (
              <div className="sources">
                Sources:{" "}
                {m.sources.map((s, j) => (
                  <span key={j}>
                    {s.filename} p.{s.page}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <span className="spinner" /> Thinking...
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="chat-input-bar">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask a question about your documents..."
        />
        <button onClick={send} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}
