import axios from "axios";

const api = axios.create({ baseURL: "http://localhost:8000/api" });

/* ── Documents ── */
export const uploadDocument = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/documents/upload", form);
};

export const getDocuments = () => api.get("/documents/");

export const deleteDocument = (id) => api.delete(`/documents/${id}`);

/* ── Chat ── */
export const askQuestion = (conversationId, question) =>
  api.post("/chat/ask", { conversation_id: conversationId, question });

export const summarizeDocument = (documentId, section = null) =>
  api.post("/chat/summarize", { document_id: documentId, section });

/* ── Conversations ── */
export const getConversations = () => api.get("/conversations/");

export const getConversationHistory = (id) =>
  api.get(`/conversations/${id}/history`);

export const deleteConversation = (id) => api.delete(`/conversations/${id}`);
