// src/components/FileList.jsx
import { useEffect, useState } from 'react';
import api from '../api';

export default function FileList({ files, setFiles }) {

  return (
    <div style={{ marginTop: '20px' }}>
      <h4>📄 Uploaded Reports:</h4>
      {files.length === 0 && <p>No files yet.</p>}
      <ul>
        {files.map((file, i) => (
          <li key={i}>
            🗂 <strong>{file.filename}</strong> – uploaded at {new Date(file.timestamp).toLocaleString()}
          </li>
        ))}
      </ul>
    </div>
  );
}
