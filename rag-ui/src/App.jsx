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
    <div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          width: "100%",
          maxWidth: 800,
          margin: "0 auto",
          marginTop: 32,
          marginBottom: 32,
        }}
      >
        <div style={{ flex: 1 }} />
        <h1 style={{ flex: 2, textAlign: "center", margin: 0 }}>
          🧠 Medical Report Assistant
        </h1>
        <button
          onClick={() => {
            localStorage.clear();
            setToken(null);
          }}
          style={{ flex: 1, textAlign: "right", background: "none", border: "none", fontSize: 18, cursor: "pointer" }}
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
      <hr
        style={{
          width: "100vw",
          margin: "32px 0",
          position: "relative",
          left: "50%",
          right: "50%",
          transform: "translateX(-50%)"
        }}
      />
      <Chat />
    </div>
  );
}
