import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Authentication
    api_key: str = "dev-api-key"
    
    # Database
    database_url: str = "sqlite:///./data/kb_service.db"
    
    # Vector Storage Configuration
    vector_store_enabled: bool = True
    vector_store_type: str = "chromadb"  # chromadb, none
    
    # ChromaDB Configuration
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection_name: str = "knowledge_base"
    chroma_auth_token: Optional[str] = None  # For Chroma Cloud
    chroma_api_key: Optional[str] = None     # For Chroma Cloud
    chroma_tenant: Optional[str] = None      # For Chroma Cloud
    chroma_database: Optional[str] = None    # For Chroma Cloud
    
    # Embedding Configuration
    embedding_enabled: bool = True
    default_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"  # Lightweight model
    alternative_embedding_model: str = "sentence-transformers/all-mpnet-base-v2"
    max_tokens_threshold: int = 7000
    
    # Chunking
    default_chunk_size: int = 1000
    default_chunk_overlap: int = 200
    
    # File Upload
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    upload_dir: str = "./data/uploads"
    
    # OCR
    ocr_enabled: bool = False  # Disabled by default for minimal setup
    
    # Document Processing
    use_simple_parsing: bool = True  # Use simple parsers instead of Docling
    
    # Development
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
    
    def is_chroma_cloud(self) -> bool:
        """Check if using Chroma Cloud"""
        return bool(self.chroma_auth_token or self.chroma_api_key)
    
    def get_chroma_client_settings(self) -> dict:
        """Get ChromaDB client settings"""
        if self.is_chroma_cloud():
            # Cloud configuration
            settings = {}
            if self.chroma_auth_token:
                settings["auth_token"] = self.chroma_auth_token
            if self.chroma_api_key:
                settings["api_key"] = self.chroma_api_key
            if self.chroma_tenant:
                settings["tenant"] = self.chroma_tenant
            if self.chroma_database:
                settings["database"] = self.chroma_database
            return settings
        else:
            # Local configuration
            return {
                "host": self.chroma_host,
                "port": self.chroma_port
            }


settings = Settings()