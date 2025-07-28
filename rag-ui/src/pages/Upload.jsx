import { useState } from 'react';
import api from '../api';
import FileList from '../components/FileList';

export default function Upload({ files, setFiles, uploadedFiles, setUploadedFiles }) {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleUpload() {
    const token = localStorage.getItem('token');
    if (!token) {
      setMessage("User ID missing from session.");
      return;
    }

    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }
    formData.append('user_id', token);

    setLoading(true);
    try {
      const res = await api.post('/upload/', formData);
      setMessage(`✅ Uploaded ${files.length} file(s)`);
      setUploadedFiles(prev => [...prev, ...(res.data.uploads || [])]);
      setFiles([]);
    } catch (err) {
      setMessage(`❌ Failed to upload files`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ marginBottom: 32 }}>
      <h2 style={{ color: "#2b6cb0" }}>📤 Upload Reports</h2>
      <input
        type="file"
        multiple
        onChange={e => setFiles(Array.from(e.target.files))}
        style={{ margin: "12px 0", padding: 8, borderRadius: 6, border: "1px solid #cbd5e1" }}
        disabled={loading}
      />
      <br />
      <button
        onClick={handleUpload}
        disabled={loading || files.length === 0}
        style={{
          background: loading ? "#90cdf4" : "#3182ce",
          color: "#fff",
          border: "none",
          borderRadius: 6,
          padding: "8px 20px",
          fontWeight: 600,
          cursor: loading ? "not-allowed" : "pointer",
          marginTop: 8,
          minWidth: 120
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
            Uploading...
          </span>
        ) : "Upload & Index"}
      </button>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg);}
            100% { transform: rotate(360deg);}
          }
        `}
      </style>
      <p style={{ color: "#38a169", fontWeight: 500 }}>{message}</p>
      <FileList files={uploadedFiles} setFiles={setUploadedFiles} />
    </div>
  );
}
