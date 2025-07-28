import { useState } from 'react';
import api from '../api';
import ChatBox from '../components/ChatBox';
import ReactMarkdown from 'react-markdown';


export default function Chat() {
  const [answer, setAnswer] = useState('');
  const [displayedAnswer, setDisplayedAnswer] = useState('');
  const [lastQuestion, setLastQuestion] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleAsk(question) {
    const token = localStorage.getItem('token');
    if (!token) {
      setAnswer("Login required.");
      setDisplayedAnswer("Login required.");
      setLastQuestion(question);
      return;
    }

    setLoading(true);
    setLastQuestion(question);
    setAnswer('');
    setDisplayedAnswer('');
    const form = new FormData();
    form.append("question", question);
    form.append("user_id", token);

    try {
      const ENDPOINT = "/query/";
      const res = await api.post(ENDPOINT, form);
      setAnswer(res.data.answer);

      // Typewriter effect
      let i = 0;
      function typeWriter() {
        setDisplayedAnswer(res.data.answer.slice(0, i));
        if (i < res.data.answer.length) {
          i++;
          setTimeout(typeWriter, 15); // Adjust speed here
        }
      }
      typeWriter();
    } catch (err) {
      setAnswer("❌ Error processing your query.");
      setDisplayedAnswer("❌ Error processing your query.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ marginTop: 32 }}>
      <h2 style={{ color: "#2b6cb0" }}>💬 Ask a Question</h2>
      <ChatBox onSend={handleAsk} loading={loading} />
      {!loading && (<div style={{
        background: "#f7fafc",
        borderRadius: 8,
        padding: 16,
        marginTop: 16,
        minHeight: 60,
        boxShadow: "0 1px 4px rgba(0,0,0,0.03)"
      }}>
        {lastQuestion && (
          <div style={{ marginBottom: 8, color: "#4a5568" }}>
            <strong>Question:</strong> {lastQuestion}
          </div>
        )}
        <ReactMarkdown>{displayedAnswer}</ReactMarkdown>
      </div>)}
    </div>
  );
}
