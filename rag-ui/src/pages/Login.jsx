// src/pages/Login.jsx
import { useState } from 'react';
import axios from 'axios';

export default function Login({ setToken }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleLogin(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    try {
      const res = await axios.post("http://localhost:8000/login/", formData);
      const { token } = res.data;
      localStorage.setItem("token", token);
      setToken(token);
    } catch (err) {
      setError("Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "linear-gradient(135deg, #f8fafc 0%, #e0e7ef 100%)"
    }}>
      <div style={{
        background: "#fff",
        borderRadius: 16,
        boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
        padding: 32,
        minWidth: 320,
        maxWidth: 350
      }}>
        <h2 style={{ textAlign: "center", color: "#2b6cb0", marginBottom: 24 }}>🔐 Login</h2>
        <form onSubmit={handleLogin}>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
            style={{
              width: "100%",
              padding: "10px",
              marginBottom: "16px",
              borderRadius: 6,
              border: "1px solid #cbd5e1",
              fontSize: 16
            }}
            autoFocus
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            style={{
              width: "100%",
              padding: "10px",
              marginBottom: "16px",
              borderRadius: 6,
              border: "1px solid #cbd5e1",
              fontSize: 16
            }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              background: loading ? "#90cdf4" : "#3182ce",
              color: "#fff",
              border: "none",
              borderRadius: 6,
              padding: "10px",
              fontWeight: 600,
              fontSize: 16,
              cursor: loading ? "not-allowed" : "pointer"
            }}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        {error && <p style={{ color: 'red', marginTop: 16, textAlign: "center" }}>{error}</p>}
      </div>
    </div>
  );
}
