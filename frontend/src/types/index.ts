export interface Project {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: number;
  project_id: number;
  filename: string;
  file_type: string;
  file_size: number;
  token_count?: number;
  is_vectorized: boolean;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: string;
  project_id: number;
  job_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  result?: Record<string, any>;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface QueryRequest {
  query: string;
  top_k?: number;
  include_metadata?: boolean;
}

export interface QueryResult {
  content: string;
  metadata?: Record<string, any>;
  score?: number;
}

export interface QueryResponse {
  query: string;
  results: QueryResult[];
  is_vectorized: boolean;
  total_results: number;
}

export interface IndexRequest {
  mode: 'auto' | 'manual';
  embedding_model: 'jinaai/jina-embeddings-v3' | 'qwen3-0.6B';
  chunk_size?: number;
  chunk_overlap?: number;
}

export interface ScrapeRequest {
  url: string;
  include_links?: boolean;
}

export interface UploadResponse {
  job_id: string;
  message: string;
}

export interface ApiError {
  detail: string;
}