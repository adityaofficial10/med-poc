# qdrant_store.py
import os
import hashlib
from datetime import datetime
from typing import List, Dict
from fastapi.responses import JSONResponse
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)

from openai import OpenAI
import tiktoken
import asyncio
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "medical_reports")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
EMBED_DIM = 1536  # text-embedding-3-small

client = QdrantClient(url=QDRANT_URL)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def truncate_to_token_limit(text: str, max_tokens: int = 8192, model: str = "text-embedding-3-small") -> str:
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
        return enc.decode(tokens)
    return text

def ensure_collection():
    cols = [c.name for c in client.get_collections().collections]
    if COLLECTION not in cols:
        client.recreate_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )

# from sentence_transformers import SentenceTransformer
# import numpy as np

# MODEL_NAME = "emilyalsentzer/Bio_ClinicalBERT"

# embedding_model = SentenceTransformer(MODEL_NAME)

# def get_embedding_using_fine_tuned_model(text: str) -> list[float]:
#     """Returns a normalized embedding vector for the given text."""
#     embedding = embedding_model.encode(text, normalize_embeddings=True)
#     return embedding.tolist()  # Qdrant expects a list

async def get_embedding_async(text: str) -> List[float]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://api.openai.com/v1/engines/{EMBED_MODEL}/embeddings",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"input": text},
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]

def get_embedding(text: str) -> List[float]:
    resp = openai_client.embeddings.create(
        model=EMBED_MODEL,
        input=[text],
    )
    return resp.data[0].embedding


MAX_EMBED_CHARS = 8000  # ~4 chars per token, adjust as needed

async def upsert_chunks_async(patient_id: str, filename: str, chunks: List[str], user_id: str):
    ensure_collection()
    timestamp = datetime.utcnow().isoformat()
    points = []
    # Parallel embedding
    embeddings = await asyncio.gather(*[get_embedding_async(chunk) for chunk in chunks])
    for i, vec in enumerate(embeddings):
        uid = int(hashlib.md5(f"{user_id}_{filename}_{i}".encode()).hexdigest(), 16) % (10**12)
        points.append(
            PointStruct(
                id=uid,
                vector=vec,
                payload={
                    "patient_id": patient_id,
                    "filename": filename,
                    "user_id": user_id,
                    "chunk_id": i,
                    "text": chunks[i]
                }
            )
        )
    client.upsert(collection_name=COLLECTION, points=points)

def upsert_chunks(patient_id: str, filename: str, chunks: List[str], user_id: str):
    ensure_collection()
    timestamp = datetime.utcnow().isoformat()
    points = []
    for i, chunk in enumerate(chunks):
        # Truncate chunk if too long for embedding model
        safe_chunk = truncate_to_token_limit(chunk, 8192, EMBED_MODEL)
        vec = get_embedding(safe_chunk)
        uid = int(hashlib.md5(f"{user_id}_{filename}_{i}".encode()).hexdigest(), 16) % (10**12)
        points.append(
            PointStruct(
                id=uid,
                vector=vec,
                payload={
                    "patient_id": patient_id,
                    "filename": filename,
                    "user_id": user_id,
                    "chunk_id": i,
                    "text": safe_chunk
                }
            )
        )
    client.upsert(collection_name=COLLECTION, points=points)


def search_chunks(query: str, top_k: int, user_id: str) -> List[str]:
    ensure_collection()
    qvec = get_embedding(query)
    hits = client.search(
        collection_name=COLLECTION,
        query_vector=qvec,
        query_filter=Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            ]
        ),
        limit=top_k,
    )
    return [h.payload["text"] for h in hits]

def search_across_reports(query, top_k, user_id):
    vector = get_embedding(query)

    # Search across all vectors for this patient
    hits = client.search(
        collection_name="medical_reports",
        query_vector=vector,
        limit=top_k,
        query_filter=Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            ]
        )
    )

    # Optional: group by filename or timestamp
    grouped = {}
    for hit in hits:
        print(hit.payload["filename"])
        filename = hit.payload.get("filename", "unknown")
        if filename not in grouped:
            grouped[filename] = []
        grouped[filename].append(hit.payload["text"])

    return grouped


def list_documents() -> List[Dict]:
    ensure_collection()
    docs = {}
    # Scroll through all points (small POC; fine)
    scroll, next_page = client.scroll(
        collection_name=COLLECTION,
        with_payload=True,
        with_vectors=False,
        limit=1000,
    )
    for pt in scroll:
        p = pt.payload
        pid = p.get("patient_id")
        if pid and pid not in docs:
            docs[pid] = {
                "patient_id": pid,
                "filename": p.get("filename"),
                "timestamp": p.get("timestamp"),
            }
    return list(docs.values())


async def handle_delete_file(user_id: str, filename: str):
    from database import mongo_db
    try:
        # Delete from Qdrant
        client.delete(
            collection_name=COLLECTION,
            points_selector=Filter(
                must=[
                    FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                    FieldCondition(key="filename", match=MatchValue(value=filename)),
                ]
            ),
            wait=True
        )
        # Delete from MongoDB
        await mongo_db.files.delete_many({"user_id": user_id, "filename": filename})

        return {"message": f"Deleted file: {filename} for user {user_id}."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    

def summarize_chunks(chunks: list[str], model="gpt-4"):
    context = "\n\n".join(chunks[:20])  # limit to ~20 chunks (~6-7 pages worth)

    prompt = f"""You are a medical assistant. Read the following medical report data and extract key findings.
Summarize them in bullet points or a table.
Focus on test names, values, and whether they're high/low/normal.

--- Medical Report ---
{context}
----------------------

Summary:"""

    resp = openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return resp.choices[0].message.content.strip()

