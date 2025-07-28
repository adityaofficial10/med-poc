// src/App.jsx
import { useEffect, useState } from 'react';
import Login from './pages/Login';
import Upload from './pages/Upload';
import Chat from './pages/Chat';
import api from "./api";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [files, setFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  useEffect(() => {
    async function fetchFiles() {
      const token = localStorage.getItem('token');
      if (!token) return;

      try {
        const res = await api.get(`/list_documents/?user_id=${token}`);
        setUploadedFiles(res.data.files || []);
      } catch (err) {
        console.error('Error fetching files:', err);
      }
    }
    if(token) {
      fetchFiles();
    }
    
  }, [token]);

  if (!token) {
    return <Login setToken={setToken} />;
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #f8fafc 0%, #e0e7ef 100%)",
      padding: 0,
      margin: 0
    }}>
      <div
        style={{
          background: "#fff",
          borderRadius: 16,
          boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
          maxWidth: 800,
          margin: "40px auto",
          padding: 32,
          minHeight: 600
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: 32,
          }}
        >
          <div style={{ flex: 1 }} />
          <h1 style={{ flex: 2, textAlign: "center", margin: 0, fontWeight: 700, fontSize: 32, color: "#2d3748" }}>
            🧠 Medical Report Assistant
          </h1>
          <button
            onClick={() => {
              localStorage.clear();
              setToken(null);
            }}
            style={{
              flex: 1,
              textAlign: "right",
              background: "none",
              border: "none",
              fontSize: 20,
              cursor: "pointer",
              color: "#e53e3e"
            }}
          >
            🚪 Logout
          </button>
        </div>
        <Upload
          files={files}
          setFiles={setFiles}
          uploadedFiles={uploadedFiles}
          setUploadedFiles={setUploadedFiles}
        />
        <hr style={{ width: "100%", margin: "32px 0", border: "none", borderTop: "1px solid #e2e8f0" }} />
        <Chat />
      </div>
    </div>
  );
}
