# Medical Report Assistant

A full-stack application for uploading, indexing, searching, and chatting with medical reports using LLMs and vector search.

---

## Features

- **User Authentication**: Register and login with secure password hashing and JWT-based authentication.
- **File Upload**: Upload one or more medical report PDFs. Files are chunked, embedded, and indexed for semantic search.
- **OCR Fallback**: If a PDF has no extractable text, OCR is used to extract content.
- **Vector Search**: Uses Qdrant as a vector database to store and search report chunks using OpenAI embeddings.
- **Chat with Reports**: Ask questions about your uploaded reports. The system retrieves relevant chunks and queries an LLM (OpenAI GPT) for answers.
- **Summarization**: Summarize key findings from reports using GPT-4.
- **File Management**: List and delete uploaded reports. Deletion removes data from both Qdrant and MongoDB.
- **Modern UI**: React-based frontend with file upload, chat, and file management. Typewriter effect and loading indicators for chat and uploads.
- **Role-based Security**: All endpoints require authentication via JWT.

---

## Tech Stack

- **Backend**: FastAPI, MongoDB, Qdrant, OpenAI API, tiktoken, httpx
- **Frontend**: React (with hooks), react-markdown
- **Vector DB**: Qdrant
- **Embeddings**: OpenAI `text-embedding-3-small` (or configurable)
- **LLM**: OpenAI GPT-4 (or configurable)

---

## Key Endpoints

### Authentication
- `POST /register/` — Register a new user
- `POST /login/` — Login and receive a JWT token

### File Operations
- `POST /upload/` — Upload one or more PDF files (multipart/form-data)
- `GET /list_documents/` — List all uploaded files for the authenticated user
- `POST /delete_file/` — Delete a file (removes from Qdrant and MongoDB)

### Chat & Summarization
- `POST /query/` — Ask a question about your reports; gets a GPT answer based on semantic search
- `POST /summary/` — Get a structured summary of your reports
- `POST /beta/query/` - Ask a question about your reports over a period of time, query trends based on semantic search

---

## How It Works

1. **Upload**: User uploads PDF(s). Each file is chunked, embedded (with token limit), and stored in Qdrant. Metadata is stored in MongoDB.
2. **Search/Chat**: User asks a question. The backend retrieves the most relevant chunks using vector search, builds a prompt, and queries GPT-4. The answer is streamed back with a typewriter effect in the UI.
3. **Summarize**: User can request a summary, which uses GPT-4 to extract and summarize key findings.
4. **Delete**: User can delete any uploaded file, which removes all associated data from both Qdrant and MongoDB.

---

## Running Locally

1. **Backend**
   - Install dependencies:  
     `pip install -r requirements.txt`
   - Set environment variables for MongoDB, Qdrant, and OpenAI API keys.
   - Run FastAPI:  
     `uvicorn app:app --reload`

2. **Frontend**
   - `cd rag-ui`
   - `npm install`
   - `npm start`

---

## Environment Variables

- `OPENAI_API_KEY` — Your OpenAI API key
- `QDRANT_URL` — Qdrant instance URL (default: `http://localhost:6333`)
- `QDRANT_COLLECTION` — Qdrant collection name (default: `medical_reports`)
- `EMBED_MODEL` — Embedding model (default: `text-embedding-3-small`)
- `MONGODB_URI` — MongoDB connection string

---

## Notes

- All API endpoints require a valid JWT token in the `Authorization` header (`Bearer <token>`).
- The UI is responsive and provides feedback for uploads, deletions, and chat queries.
- Embedding and LLM calls are token-limited for performance and cost control.
- The backend supports async batch embedding for faster uploads.

---

## Folder Structure

```
/poc
  /rag-ui         # React frontend
  /                # FastAPI backend, vector store, chunking, etc.
```

---

## License

MIT License

---

**Built with ❤️ for medical data exploration and patient empowerment.**