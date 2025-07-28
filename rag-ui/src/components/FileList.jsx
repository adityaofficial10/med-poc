// src/components/FileList.jsx
import { useEffect, useState } from 'react';
import api from '../api';

export default function FileList({ files, setFiles }) {

  const [deleting, setDeleting] = useState(null);

  async function handleDelete(filename) {
    setDeleting(filename);
    try {
      const token = localStorage.getItem('token');
      const form = new FormData();
      form.append("filename", filename);
      form.append("user_id", token);
      await api.post('/delete_file/', form);
      setFiles(files.filter(f => f.filename !== filename));
    } catch (err) {
      alert('Failed to delete file.');
    } finally {
      setDeleting(null);
    }
  }

  return (
    <div style={{ marginTop: '20px' }}>
      <h4 style={{ color: "#2b6cb0" }}>📄 Uploaded Reports:</h4>
      {files.length === 0 && <p style={{ color: "#718096" }}>No files yet.</p>}
      <ul style={{ listStyle: "none", padding: 0 }}>
        {files.map((file, i) => (
          <li
            key={i}
            style={{
              background: "#f7fafc",
              borderRadius: 8,
              marginBottom: 10,
              padding: "10px 16px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              boxShadow: "0 1px 4px rgba(0,0,0,0.03)"
            }}
          >
            <span>
              🗂 <strong>{file.filename}</strong>
              <span style={{ color: "#718096", fontSize: 13, marginLeft: 8 }}>
                {file.timestamp && `uploaded at ${new Date(file.timestamp).toLocaleString()}`}
              </span>
            </span>
            <button
              style={{
                background: "none",
                border: "none",
                cursor: "pointer",
                color: "#e53e3e",
                fontSize: 20,
                marginLeft: 12
              }}
              title="Delete"
              disabled={deleting === file.filename}
              onClick={() => handleDelete(file.filename)}
            >
              🗑️
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
