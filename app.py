# query_server.py
from datetime import datetime
from http.client import HTTPException
import json
import os
import shutil
import traceback
from typing import List
from uuid import uuid4

from chat_memory import add_to_history, get_user_history
from database import create_token, hash_password, verify_password, mongo_db, get_user_id_from_token
from fastapi import FastAPI, UploadFile, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import UploadFile, File, Form, Depends


from file_store import store_metadata
from openai import OpenAI

from extract_chunks import extract_chunks_from_pdf
from qdrant_store import summarize_chunks, upsert_chunks, search_chunks, list_documents, handle_delete_file, upsert_chunks_async
from llm_prompter import build_prompt

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")  # or gpt-4 / gpt-4o
META_DIR = "storage/metadata"

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(title="Medical RAG POC", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register/")
async def register(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if await mongo_db.users.find_one({"username": username}):
        raise HTTPException(400, "User already exists")

    hashed = hash_password(password)
    await mongo_db.users.insert_one({
        "username": username,
        "email": email,
        "hashed_password": hashed
    })

    return {"message": "User registered successfully"}

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    user = await mongo_db.users.find_one({"username": username})
    print(user)
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(401, "Invalid credentials")

    token = create_token({"sub": username})
    return {"token": token}



@app.post("/upload/")
async def upload_multiple(
    files: List[UploadFile] = File(...),
    user_id: str = Depends(get_user_id_from_token)
):
    results = []
    mongo_file_docs = []
    for file in files:
        try:
            patient_id = file.filename

            tmp_path = f"/tmp/{uuid4().hex}_{file.filename}"
            with open(tmp_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            chunks, _ = extract_chunks_from_pdf(tmp_path)
            os.remove(tmp_path)

            if not chunks:
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": "No text chunks extracted."
                })
                continue

            upsert_chunks(
                patient_id=patient_id,
                filename=file.filename,
                chunks=chunks,
                user_id=user_id
            )
            # summary = summarize_chunks(chunks)
            store_metadata(user_id=user_id, filename=file.filename, num_chunks=len(chunks), summary="")
            results.append({
                "filename": file.filename,
                "status": "indexed",
                "num_chunks": len(chunks),
                "timestamp": datetime.utcnow(),
            })
            # Collect metadata for batch insert
            mongo_file_docs.append({
                "filename": file.filename,
                "user_id": user_id,
                "timestamp": datetime.utcnow(),
                "num_chunks": len(chunks)
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })

    # Batch insert all file metadata at once (if any)
    if mongo_file_docs:
        await mongo_db.files.insert_many(mongo_file_docs)

    return {"uploads": results}


@app.post("/query/")
async def query(question: str = Form(...), user_id: str = Depends(get_user_id_from_token)):
    try:
        chunks = search_chunks(question, 5, user_id)

        if not chunks:
            return {"answer": "No relevant context found for your question in this report."}

        prompt = build_prompt(question, chunks)
        full_messages = get_user_history(user_id).copy()
        full_messages.append({"role": "user", "content": prompt})


        resp = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=full_messages,
            temperature=0.0,
        )

        answer = resp.choices[0].message.content
        add_to_history(user_id, "user", prompt)
        add_to_history(user_id, "assistant", answer)

        return {"answer": answer}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/list_documents/")
async def list_reports(user_id: str = Depends(get_user_id_from_token)):
    try:
        # Fetch all files for the user from MongoDB
        files_cursor = mongo_db.files.find({"user_id": user_id})
        files = []
        async for file in files_cursor:
            file["_id"] = str(file["_id"])  # Convert ObjectId to string if needed
            files.append(file)
        return {"files": files}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

from structured_parser import extract_structured_tests
from summary_store import save_structured_summary, load_structured_summary

@app.post("/summary/")
async def get_summary(session_id: str = Form(...), user_id: str = Form(...)):
    try:
        chunks = search_chunks(query="summary", top_k = 10, user_id=user_id)

        full_text = "\n".join(chunks)
        summary = extract_structured_tests(full_text)
        save_structured_summary(user_id, session_id, summary)
        return {"summary": summary}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/delete_file/")
async def delete_file(user_id: str = Form(...), filename: str = Form(...)):
    handle_delete_file(user_id=user_id, filename=filename)

