# Installation Guide

## Requirements

- Python 3.12+ (for backend development)
- Node.js 18+ (for frontend development)
- Docker & Docker Compose (for containerized deployment)

## Installation Options

### 1. Minimal Setup (Recommended for Testing)

This setup includes basic document processing without AI/ML dependencies.

```bash
# Clone repository
git clone <repository>
cd knowledge-base-service

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-minimal.txt

# Frontend setup
cd ../frontend
npm install

# Environment setup
cd ..
cp .env.example .env
# Edit .env and set:
# VECTOR_STORE_ENABLED=false
# EMBEDDING_ENABLED=false
# OCR_ENABLED=false
```

**Start services:**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm start
```

### 2. Full Setup with Local ChromaDB

This setup includes all AI/ML features with local vector database.

```bash
# Clone and basic setup (same as above)
git clone <repository>
cd knowledge-base-service

# Backend with full dependencies
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Environment setup
cd ..
cp .env.example .env
# Keep default settings or customize as needed
```

**Start with Docker:**
```bash
docker-compose up -d
```

### 3. Cloud ChromaDB Setup

Use Chroma Cloud for managed vector storage.

```bash
# Same setup as Full Setup, but configure .env:
VECTOR_STORE_ENABLED=true
CHROMA_AUTH_TOKEN=your-chroma-cloud-token
CHROMA_API_KEY=your-chroma-cloud-api-key
CHROMA_TENANT=your-tenant
CHROMA_DATABASE=your-database

# Start services
docker-compose up -d
```

## Troubleshooting

### Python Dependency Conflicts

**Problem**: Version conflicts with Python 3.12
```
ERROR: torch==2.1.1 has no wheels with a matching Python ABI tag
```

**Solutions**:
1. Use minimal setup: `pip install -r requirements-minimal.txt`
2. Update torch version: `pip install torch>=2.1.2`
3. Use Docker deployment instead

### ChromaDB Connection Issues

**Problem**: ChromaDB fails to connect
```
Failed to initialize vector store: Connection refused
```

**Solutions**:
1. Check if ChromaDB service is running: `docker-compose ps`
2. Verify port availability: `netstat -tulpn | grep 8001`
3. Use minimal setup without vector storage:
   ```
   VECTOR_STORE_ENABLED=false
   EMBEDDING_ENABLED=false
   ```

### Memory Issues with Embeddings

**Problem**: Out of memory when loading embedding models

**Solutions**:
1. Use lightweight models (default in config):
   ```
   DEFAULT_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```
2. Disable embeddings for minimal setup:
   ```
   EMBEDDING_ENABLED=false
   ```
3. Increase Docker memory limits

### Frontend Build Issues

**Problem**: Node.js dependency conflicts

**Solutions**:
1. Clear cache: `npm cache clean --force`
2. Delete node_modules: `rm -rf node_modules && npm install`
3. Use specific Node version: `nvm use 18`

## Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate

# For minimal development
pip install -r requirements-minimal.txt

# For full development
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm start  # Starts on http://localhost:3000
```

### API Testing
```bash
# Test basic functionality
python test_api.py

# Manual API testing
curl -H "x-api-key: dev-api-key" http://localhost:8000/health
```

## Production Deployment

### Environment Configuration
```bash
# Production environment variables
API_KEY=your-production-api-key-here
DEBUG=false
LOG_LEVEL=WARNING

# For cloud deployment
CHROMA_AUTH_TOKEN=your-production-token
```

### Docker Production
```bash
# Build and start
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale backend=2
```

### Security Considerations

1. **Change default API key** in production
2. **Use HTTPS** in production
3. **Configure CORS** appropriately
4. **Secure ChromaDB** with authentication
5. **Regular backups** of SQLite database

## Feature Matrix

| Feature | Minimal Setup | Full Setup | Cloud Setup |
|---------|---------------|------------|-------------|
| Document Upload | ✅ | ✅ | ✅ |
| Basic Parsing | ✅ | ✅ | ✅ |
| OCR Support | ❌ | ✅ | ✅ |
| Vector Search | ❌ | ✅ | ✅ |
| Embeddings | ❌ | ✅ | ✅ |
| Web Scraping | ✅ | ✅ | ✅ |
| Cloud Vector DB | ❌ | ❌ | ✅ |
| Dependencies | Minimal | Full | Full |
| Memory Usage | Low | High | Medium |

## Next Steps

1. Choose your setup based on requirements
2. Follow the appropriate installation steps
3. Test with the validation script: `python validate_deployment.py`
4. Start uploading documents and testing queries
5. Configure for production if needed