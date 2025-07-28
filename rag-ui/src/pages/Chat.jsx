import { useState } from 'react';
import api from '../api';
import ChatBox from '../components/ChatBox';

export default function Chat() {
  const [answer, setAnswer] = useState('');

  async function handleAsk(question) {
    const token = localStorage.getItem('token');
    if (!token) {
      setAnswer("Login required.");
      return;
    }

    const form = new FormData();
    form.append("question", question);
    form.append("user_id", token);

    try {
      const BETA_ENDPOINT = "/beta/query/";
      const ENDPOINT = "/query/";
      const res = await api.post(ENDPOINT, form);
      setAnswer(res.data.answer);
    } catch (err) {
      setAnswer("❌ Error processing your query.");
    }
  }

  return (
    <div>
      <h2>💬 Ask a Question</h2>
      <ChatBox onSend={handleAsk} />
      <p><strong>Answer:</strong> {answer}</p>
    </div>
  );
}
