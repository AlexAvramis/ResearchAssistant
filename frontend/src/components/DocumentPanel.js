import React, { useState, useEffect, useRef } from "react";
import {
  uploadDocument,
  getDocuments,
  deleteDocument,
  summarizeDocument,
} from "../api";

export default function DocumentPanel() {
  const [docs, setDocs] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [summary, setSummary] = useState(null);
  const [summarizing, setSummarizing] = useState(false);
  const fileRef = useRef();

  const refresh = () =>
    getDocuments()
      .then((r) => setDocs(r.data))
      .catch(() => {});

  useEffect(() => {
    refresh();
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      await uploadDocument(file);
      refresh();
    } catch (err) {
      alert("Upload failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
      fileRef.current.value = "";
    }
  };

  const handleDelete = async (id) => {
    await deleteDocument(id);
    refresh();
    if (summary?.document_id === id) setSummary(null);
  };

  const handleSummarize = async (id) => {
    setSummarizing(true);
    setSummary(null);
    try {
      const res = await summarizeDocument(id);
      setSummary(res.data);
    } catch (err) {
      alert("Summarize failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setSummarizing(false);
    }
  };

  return (
    <div className="doc-panel">
      <h2>Documents</h2>

      <div className="upload-area" onClick={() => fileRef.current.click()}>
        <input
          ref={fileRef}
          type="file"
          accept="application/pdf"
          onChange={handleUpload}
        />
        {uploading ? (
          <p>
            <span className="spinner" /> Uploading &amp; processing…
          </p>
        ) : (
          <p>Click or drag a PDF here to upload</p>
        )}
      </div>

      <div className="doc-list">
        {docs.length === 0 && <p style={{ color: "#64748b" }}>No documents uploaded yet.</p>}
        {docs.map((d) => (
          <div key={d.document_id} className="doc-card">
            <div className="info">
              <span className="name">{d.filename}</span>
              <span className="meta">{d.num_chunks} chunks indexed</span>
            </div>
            <div className="doc-actions">
              <button
                className="btn-summarize"
                onClick={() => handleSummarize(d.document_id)}
                disabled={summarizing}
              >
                Summarize
              </button>
              <button
                className="btn-delete"
                onClick={() => handleDelete(d.document_id)}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {summarizing && (
        <div className="summary-box">
          <span className="spinner" /> Generating summary…
        </div>
      )}
      {summary && (
        <div className="summary-box">
          <strong>Summary:</strong>
          <br />
          {summary.summary}
        </div>
      )}
    </div>
  );
}
