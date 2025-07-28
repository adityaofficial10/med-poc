// src/components/ChatBox.jsx
import { useState } from 'react';

export default function ChatBox({ onSend }) {
  const [question, setQuestion] = useState('');

  function handleSend() {
    if (question.trim()) {
      onSend(question.trim());
      setQuestion('');
    }
  }

  return (
    <div style={{ marginTop: '20px' }}>
      <textarea
        rows={3}
        placeholder="Ask something about the report..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        style={{ width: '100%' }}
      />
      <button onClick={handleSend}>Ask</button>
    </div>
  );
}
