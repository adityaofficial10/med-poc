import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Simple configuration class without Pydantic"""
    
    def __init__(self):
        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Validate API keys
        if not self.openai_api_key or not self.gemini_api_key:
            raise ValueError("Missing API keys in .env file")
        
        # Qdrant settings
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = "medical_reports"
        
        # LLM settings
        self.primary_llm = os.getenv("PRIMARY_LLM", "gemini")
        self.openai_model = "gpt-3.5-turbo"  # Using 3.5 for faster responses
        self.gemini_model = "gemini-pro"
        
        # Embedding settings
        self.embedding_provider = os.getenv("EMBEDDING_PROVIDER", "openai")
        self.openai_embedding_model = "text-embedding-ada-002"
        self.embedding_dimensions = 1536  # For OpenAI ada-002
        
        # RAG settings
        self.chunk_size = 256
        self.chunk_overlap = 100
        self.k_retrieval = 5
        
        # Search weights
        self.vector_weight = 0.7
        self.keyword_weight = 0.3
        
        # File settings
        self.upload_dir = "data/uploads"
        self.max_file_size_mb = 50
        
        # Performance
        self.cache_ttl = 3600
        
    @property
    def max_file_size_bytes(self):
        return self.max_file_size_mb * 1024 * 1024