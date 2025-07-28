// src/components/ChatBox.jsx
import { useState } from 'react';

export default function ChatBox({ onSend, loading }) {
  const [question, setQuestion] = useState('');

  function handleSend() {
    if (question.trim()) {
      onSend(question);
      // Do not clear question here to persist it
    }
  }

  return (
    <div style={{ marginTop: '20px', display: "flex", gap: 8 }}>
      <textarea
        rows={3}
        placeholder="Ask something about the report..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        style={{
          width: "100%",
          borderRadius: 6,
          border: "1px solid #cbd5e1",
          padding: 8,
          fontSize: 16,
          resize: "vertical"
        }}
        disabled={loading}
      />
      <button
        onClick={handleSend}
        disabled={loading}
        style={{
          background: "#3182ce",
          color: "#fff",
          border: "none",
          borderRadius: 6,
          padding: "8px 18px",
          fontWeight: 600,
          cursor: loading ? "not-allowed" : "pointer",
          alignSelf: "flex-end",
          minWidth: 70
        }}
      >
        {loading ? (
          <span>
            <span className="spinner" style={{
              display: "inline-block",
              width: 16,
              height: 16,
              border: "2px solid #fff",
              borderTop: "2px solid #3182ce",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
              marginRight: 6,
              verticalAlign: "middle"
            }} />
          </span>
        ) : "Ask"}
      </button>
      {/* Spinner CSS */}
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg);}
            100% { transform: rotate(360deg);}
          }
        `}
      </style>
    </div>
  );
}
