import axios, { AxiosResponse } from 'axios';
import {
  Project,
  Document,
  Job,
  QueryRequest,
  QueryResponse,
  IndexRequest,
  ScrapeRequest,
  UploadResponse
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
const API_KEY = 'dev-api-key'; // In production, this should come from env vars

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': API_KEY,
  },
});

// Projects API
export const projectsApi = {
  list: (): Promise<AxiosResponse<Project[]>> =>
    api.get('/projects'),

  create: (project: { name: string; description?: string }): Promise<AxiosResponse<Project>> =>
    api.post('/projects', project),

  get: (id: number): Promise<AxiosResponse<Project>> =>
    api.get(`/projects/${id}`),

  getDocuments: (id: number): Promise<AxiosResponse<Document[]>> =>
    api.get(`/projects/${id}/documents`),

  upload: (id: number, files: File[]): Promise<AxiosResponse<UploadResponse>> => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    return api.post(`/projects/${id}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'x-api-key': API_KEY,
      },
    });
  },

  scrape: (id: number, scrapeRequest: ScrapeRequest): Promise<AxiosResponse<UploadResponse>> =>
    api.post(`/projects/${id}/scrape`, scrapeRequest),

  index: (id: number, indexRequest: IndexRequest): Promise<AxiosResponse<UploadResponse>> =>
    api.post(`/projects/${id}/index`, indexRequest),

  query: (id: number, queryRequest: QueryRequest): Promise<AxiosResponse<QueryResponse>> =>
    api.post(`/projects/${id}/query`, queryRequest),
};

// Jobs API
export const jobsApi = {
  get: (id: string): Promise<AxiosResponse<Job>> =>
    api.get(`/jobs/${id}`),
};

// Health check
export const healthApi = {
  check: (): Promise<AxiosResponse<{ status: string; database: string; vector_store: string; timestamp: string }>> =>
    api.get('/health', { baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000' }),
};

export default api;