# Knowledge Base Service

A pure knowledge base service built with FastAPI (backend) and React + TypeScript (frontend) for document parsing, embedding, and intelligent search.

## Features

### 📄 Document Processing
- **Multi-format support**: PDF, DOCX, PPTX, TXT, MD, PNG, JPG
- **Advanced parsing**: Docling converter with OCR fallback
- **Web scraping**: URL content extraction
- **Token counting**: Automatic text analysis

### 🔍 Intelligent Indexing
- **Auto mode**: Automatic chunk size detection based on embedding model limits
- **Manual mode**: Custom chunk size and overlap configuration
- **Smart strategy**: <7K tokens stored as raw, ≥7K tokens vectorized
- **Multiple models**: Jina Embeddings v3 (8K) or Qwen3 0.6B (2K)

### 🔎 Hybrid Search
- **Vector search**: Semantic similarity for large documents
- **Raw content**: Direct text matching for small documents
- **ChromaDB**: High-performance vector storage
- **Metadata support**: Rich document context

### 🎨 Modern UI
- **Responsive design**: Mobile and desktop optimized
- **Real-time updates**: Live job progress tracking
- **Tab interface**: Parser, Indexing, Query Test
- **Beautiful design**: Tailwind CSS styling

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │────│  FastAPI Backend │────│   ChromaDB      │
│   (TypeScript)   │    │    (Python)     │    │  Vector Store   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                        ┌─────────────────┐
                        │     SQLite      │
                        │   Metadata DB   │
                        └─────────────────┘
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### 1. Clone Repository
```bash
git clone <repository-url>
cd knowledge-base-service
```

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### 3. Start Services
```bash
docker-compose up -d
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ChromaDB**: http://localhost:8001

## Configuration

### Environment Variables (.env)

```bash
# Authentication
API_KEY=your-secret-api-key-here

# Database
DATABASE_URL=sqlite:///./data/kb_service.db

# ChromaDB Configuration
CHROMA_HOST=chroma
CHROMA_PORT=8000
CHROMA_COLLECTION_NAME=knowledge_base

# Embedding Configuration
DEFAULT_EMBEDDING_MODEL=jinaai/jina-embeddings-v3
ALTERNATIVE_EMBEDDING_MODEL=qwen3-0.6B
MAX_TOKENS_THRESHOLD=7000

# Chunking Configuration
DEFAULT_CHUNK_SIZE=1000
DEFAULT_CHUNK_OVERLAP=200
```

## API Endpoints

### Projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects` - List projects
- `GET /api/v1/projects/{id}` - Get project
- `GET /api/v1/projects/{id}/documents` - List documents

### Document Processing
- `POST /api/v1/projects/{id}/upload` - Upload files
- `POST /api/v1/projects/{id}/scrape` - Scrape URL
- `POST /api/v1/projects/{id}/index` - Index documents
- `POST /api/v1/projects/{id}/query` - Query documents

### Jobs
- `GET /api/v1/jobs/{id}` - Get job status

### Health
- `GET /health` - Service health check

## Usage Guide

### 1. Create Project
Navigate to the frontend and create a new knowledge base project.

### 2. Upload Documents
Use the **Parser** tab to:
- Drag & drop files (PDF, DOCX, PPTX, TXT, MD, PNG, JPG)
- Scrape web content from URLs
- Preview parsed text content

### 3. Index Documents
Use the **Indexing** tab to:
- Choose Auto or Manual mode
- Select embedding model (Jina v3 or Qwen3)
- Configure chunk size and overlap (Manual mode)
- Start the indexing process

### 4. Query Documents
Use the **Query Test** tab to:
- Enter natural language queries
- Adjust result count and metadata inclusion
- View semantic search results with similarity scores
- Browse query history

## Indexing Strategy

### Automatic Decision Making
- **Small documents** (<7,000 tokens): Stored as raw content for direct retrieval
- **Large documents** (≥7,000 tokens): Chunked and vectorized for semantic search

### Auto vs Manual Mode
- **Auto Mode**: Automatically detects embedding model token limits and chunks accordingly
- **Manual Mode**: Allows fine-tuning of chunk size and overlap parameters

### Embedding Models
- **Jina Embeddings v3**: 8,192 token limit, high-quality embeddings
- **Qwen3 0.6B**: 2,048 token limit, efficient processing

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### API Testing
Access the interactive API documentation at http://localhost:8000/docs

## Testing Acceptance Criteria

### Test Case 1: Small Document (<7K tokens)
1. Upload a small PDF/text file
2. Index the project (should skip embedding)
3. Query the project (should return raw content directly)

### Test Case 2: Large Document (>7K tokens)
1. Upload a large document
2. Index the project (should chunk and embed)
3. Query the project (should perform semantic search)

## Dependencies

### Backend
- **FastAPI**: Modern web framework
- **SQLAlchemy**: Database ORM
- **ChromaDB**: Vector database
- **Docling**: Document conversion
- **EasyOCR**: Optical character recognition
- **Sentence Transformers**: Embedding models
- **Tiktoken**: Token counting

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **React Router**: Navigation
- **Axios**: HTTP client
- **React Dropzone**: File uploads
- **Lucide React**: Icons

## Security

- API key authentication via `x-api-key` header
- CORS configuration for cross-origin requests
- Input validation and sanitization
- Error handling and logging

## Performance

- **Async processing**: Background jobs for file processing and indexing
- **Vector optimization**: ChromaDB for fast similarity search
- **Efficient chunking**: Smart token-based text splitting
- **Caching**: Model loading optimization

## Troubleshooting

### Common Issues

1. **ChromaDB Connection Failed**
   - Ensure ChromaDB service is running
   - Check network connectivity between services

2. **File Upload Errors**
   - Verify file format is supported
   - Check file size limits

3. **Embedding Failures**
   - Ensure sufficient memory for model loading
   - Check internet connectivity for model downloads

4. **Search Returns No Results**
   - Verify documents are indexed
   - Try different query phrasings

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Create an issue on GitHub