import asyncio
import logging
import hashlib
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
import openai
import google.generativeai as genai
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

class VectorStore:
    """Simple vector store implementation"""
    
    def __init__(self, config):
        self.config = config
        self.client = QdrantClient(
            host=config.qdrant_host,
            port=config.qdrant_port
        )
        self.collection_name = config.collection_name
        
        # Initialize embeddings
        if config.embedding_provider == "openai":
            openai.api_key = config.openai_api_key
        else:
            genai.configure(api_key=config.gemini_api_key)
        
        # TF-IDF for keyword search
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        self.tfidf_matrix = None
        self.document_ids = []
        
        # Create collection
        self._init_collection()
    
    def _init_collection(self):
        """Initialize Qdrant collection"""
        try:
            # Check if collection exists
            existing_collections = []
            try:
                collections_response = self.client.get_collections()
                if hasattr(collections_response, 'collections'):
                    existing_collections = [c.name for c in collections_response.collections]
            except Exception as e:
                logger.warning(f"Error checking collections: {e}")
            
            if self.collection_name not in existing_collections:
                # Create collection with basic settings
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={
                        "size": self.config.embedding_dimensions,
                        "distance": "Cosine"
                    }
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            # Continue anyway - collection might already exist
    
    async def embed_text(self, text):
        """Generate embeddings for text"""
        if self.config.embedding_provider == "openai":
            response = await asyncio.to_thread(
                openai.embeddings.create,
                model=self.config.openai_embedding_model,
                input=text
            )
            embedding = response.data[0].embedding
        else:
            model_name = self.config.gemini_model
            if not (model_name.startswith("models/") or model_name.startswith("tunedModels/")):
                model_name = "models/embedding-001"
            result = await asyncio.to_thread(
                genai.embed_content,
                model=model_name,
                content=text,
                task_type="retrieval_document"
            )
            embedding = result['embedding']
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = (np.array(embedding) / norm).tolist()
        return embedding
    
    async def add_documents(self, documents):
        """Add documents to vector store"""
        logger.info(f"Adding {len(documents)} documents")
        
        points = []
        for i, doc in enumerate(documents):
            # Generate embedding
            embedding = await self.embed_text(doc["content"])
            
            # Create point
            point_id = hashlib.md5(f"{doc['metadata']['file_hash']}_{i}".encode()).hexdigest()
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    **doc["metadata"],
                    "content": doc["content"],
                    "indexed_at": datetime.utcnow().isoformat()
                }
            )
            points.append(point)
            
            # Batch upload
            if len(points) >= 100:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                points = []
        
        # Upload remaining points
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        
        # Update TF-IDF
        await self._update_tfidf()
        
        logger.info("Documents added successfully")
    
    async def hybrid_search(self, query, filter_conditions=None, top_k=5):
        """Perform hybrid search"""
        # Vector search
        query_embedding = await self.embed_text(query)
        
        search_filter = None
        if filter_conditions:
            conditions = []
            for key, value in filter_conditions.items():
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            search_filter = Filter(must=conditions)
        
        vector_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=top_k * 2
        )
        
        # Keyword search
        keyword_results = self._keyword_search(query, top_k * 2)
        
        # Combine results
        combined = self._combine_results(vector_results, keyword_results)
        
        return combined[:top_k]
    
    def _keyword_search(self, query, limit):
        """Perform keyword search using TF-IDF"""
        if self.tfidf_matrix is None:
            return []
        
        query_vector = self.tfidf_vectorizer.transform([query])
        similarities = (self.tfidf_matrix * query_vector.T).toarray().flatten()
        
        top_indices = np.argsort(similarities)[::-1][:limit]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                point_id = self.document_ids[idx]
                points = self.client.retrieve(
                    collection_name=self.collection_name,
                    ids=[point_id]
                )
                if points:
                    results.append({
                        "id": str(points[0].id),
                        "score": float(similarities[idx]),
                        "payload": points[0].payload
                    })
        
        return results
    
    def _combine_results(self, vector_results, keyword_results):
        """Combine vector and keyword search results"""
        combined = {}
        value_pattern = re.compile(r'\b\d+\.?\d*\s*(mg/dL|g/dL|mmol/L|IU/L|%|/μL|mmHg|bpm|°[CF])\b', re.IGNORECASE)
        # Add vector results
        for hit in vector_results:
            content = hit.payload.get("content", "")
            boost = 0.1 if value_pattern.search(content) else 0
            combined[str(hit.id)] = {
                "id": str(hit.id),
                "content": content,
                "metadata": hit.payload,
                "vector_score": hit.score,
                "keyword_score": 0,
                "combined_score": hit.score * self.config.vector_weight + boost
            }
        
        # Add keyword results
        for result in keyword_results:
            doc_id = result["id"]
            if doc_id in combined:
                combined[doc_id]["keyword_score"] = result["score"]
                combined[doc_id]["combined_score"] += result["score"] * self.config.keyword_weight
            else:
                combined[doc_id] = {
                    "id": doc_id,
                    "content": result["payload"].get("content", ""),
                    "metadata": result["payload"],
                    "vector_score": 0,
                    "keyword_score": result["score"],
                    "combined_score": result["score"] * self.config.keyword_weight
                }
        
        # Sort by combined score
        results = list(combined.values())
        results.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return results
    
    async def _update_tfidf(self):
        """Update TF-IDF matrix"""
        all_points = self.client.scroll(
            collection_name=self.collection_name,
            limit=10000
        )[0]
        
        if all_points:
            texts = [p.payload.get("content", "") for p in all_points]
            self.document_ids = [p.id for p in all_points]
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
    
    async def get_document_by_filename(self, filename):
        """Get all chunks for a document"""
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(key="filename", match=MatchValue(value=filename))]
            ),
            limit=1000
        )[0]
        
        return [{
            "id": str(p.id),
            "content": p.payload.get("content", ""),
            "metadata": p.payload
        } for p in results]
    
    async def delete_document(self, filename):
        """Delete document by filename"""
        chunks = await self.get_document_by_filename(filename)
        if chunks:
            point_ids = [c["id"] for c in chunks]
            self.client.delete(
                collection_name=self.collection_name,
                points_selector={"points": point_ids}
            )
            logger.info(f"Deleted {len(point_ids)} chunks for {filename}")
            await self._update_tfidf()
    
    async def get_collection_stats(self):
        """Get collection statistics"""
        try:
            # Simple approach without triggering Pydantic issues
            collections = self.client.get_collections()
            collection_exists = any(c.name == self.collection_name for c in collections.collections)
            
            if not collection_exists:
                return {
                    "total_chunks": 0,
                    "total_documents": 0,
                    "documents": []
                }
            
            # Get points count using search with limit 0
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=[0.0] * self.config.embedding_dimensions,
                limit=0
            )
            
            # Get unique documents by scrolling
            unique_files = set()
            try:
                offset = None
                while True:
                    batch = self.client.scroll(
                        collection_name=self.collection_name,
                        limit=100,
                        offset=offset
                    )
                    
                    if not batch or not batch[0]:
                        break
                        
                    for point in batch[0]:
                        if hasattr(point, 'payload') and point.payload:
                            unique_files.add(point.payload.get("filename", ""))
                    
                    offset = batch[1]
                    if not offset:
                        break
                        
            except Exception as e:
                logger.warning(f"Error scrolling points: {e}")
            
            return {
                "total_chunks": len(unique_files) * 10,  # Estimate
                "total_documents": len(unique_files),
                "documents": list(unique_files)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "total_chunks": 0,
                "total_documents": 0,
                "documents": [],
                "error": str(e)
            }