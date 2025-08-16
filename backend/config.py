import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Authentication
    api_key: str = "dev-api-key"
    
    # Database
    database_url: str = "sqlite:///./data/kb_service.db"
    
    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection_name: str = "knowledge_base"
    
    # Embedding
    default_embedding_model: str = "jinaai/jina-embeddings-v3"
    alternative_embedding_model: str = "qwen3-0.6B"
    max_tokens_threshold: int = 7000
    
    # Chunking
    default_chunk_size: int = 1000
    default_chunk_overlap: int = 200
    
    # File Upload
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    upload_dir: str = "./data/uploads"
    
    # OCR
    ocr_enabled: bool = True
    
    # Development
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"


settings = Settings()