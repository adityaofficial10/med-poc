// src/pages/Login.jsx
import { useState } from 'react';
import axios from 'axios';

export default function Login({ setToken }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  async function handleLogin(e) {
    e.preventDefault();
          const formData = new FormData();
          formData.append("username", username);
          formData.append("password", password);

          try {
            const res = await axios.post("http://localhost:8000/login/", formData);
            const { token } = res.data;
            localStorage.setItem("token", token);
            setToken(token);
          } catch (err) {
            console.error(err);
            alert("Login failed");
          }
  }

  return (
    <div>
      <h2>🔐 Login</h2>
      <form onSubmit={handleLogin}>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
        />
        <br />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
        />
        <br />
        <button type="submit">Login</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}
