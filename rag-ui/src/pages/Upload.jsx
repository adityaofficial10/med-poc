import { useState } from 'react';
import api from '../api';
import FileList from '../components/FileList';

export default function Upload({ files, setFiles, uploadedFiles, setUploadedFiles }) {
  const [message, setMessage] = useState('');

  async function handleUpload() {
    const token = localStorage.getItem('token');
    const user_id = localStorage.getItem('user_id');

    if (!token) {
      setMessage("User ID missing from session.");
      return;
    }

    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file); // 'files' matches FastAPI's parameter
    }
    formData.append('user_id', token);

    try {
      const res = await api.post('/upload/', formData);
      setMessage(`✅ Uploaded ${files.length} file(s)`);
      let newFiles = [...uploadedFiles];
      newFiles.concat(res.data.uploads);
      setUploadedFiles(newFiles);
    } catch (err) {
      setMessage(`❌ Failed to upload files`);
    }
  }

  return (
    <div>
      <h2>📤 Upload Reports</h2>
      <input type="file" multiple onChange={(e) => setFiles(e.target.files)} />
      <br />
      <button onClick={handleUpload}>Upload & Index</button>
      <p>{message}</p>
      <FileList files={uploadedFiles} setFiles={setUploadedFiles} />
    </div>
  );
}
