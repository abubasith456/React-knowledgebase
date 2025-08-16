from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IndexingMode(str, Enum):
    auto = "auto"
    manual = "manual"


class EmbeddingModel(str, Enum):
    jina = "jinaai/jina-embeddings-v3"
    qwen = "qwen3-0.6B"


class IndexRequest(BaseModel):
    mode: IndexingMode = IndexingMode.auto
    embedding_model: EmbeddingModel = EmbeddingModel.jina
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class JobResponse(BaseModel):
    id: str
    project_id: int
    job_type: str
    status: JobStatus
    progress: float
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    file_type: str
    file_size: int
    token_count: Optional[int]
    is_vectorized: bool
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    include_metadata: bool = True


class QueryResult(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None
    score: Optional[float] = None


class QueryResponse(BaseModel):
    query: str
    results: List[QueryResult]
    is_vectorized: bool
    total_results: int


class ScrapeRequest(BaseModel):
    url: str
    include_links: bool = False


class UploadResponse(BaseModel):
    job_id: str
    message: str