# Dependency Optimization & Configuration Changes

## Issues Fixed

### 1. Python 3.12 Compatibility
**Problem**: Torch 2.1.1 had no wheels for Python 3.12
**Solution**: Updated to torch 2.1.2 with Python 3.12 support

### 2. Dependency Conflicts 
**Problem**: Docling required requests>=2.32.3 but had requests==2.31.0
**Solution**: Updated requests to >=2.32.0 and made Docling optional

### 3. Heavy Dependencies
**Problem**: Too many ML/AI dependencies making installation complex
**Solution**: Created modular dependency system with minimal and full options

## New Dependency Structure

### Core Dependencies (`requirements-minimal.txt`)
- FastAPI + SQLAlchemy (backend core)
- Basic document parsers (PyPDF2, python-docx, python-pptx)
- Token counting (tiktoken)
- Authentication & HTTP client
- **Size**: ~20 packages, lightweight

### Full Dependencies (`requirements.txt`)
- All minimal dependencies
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- EasyOCR for image processing
- **Size**: ~50+ packages, ML/AI enabled

## Configuration Improvements

### 1. Optional Vector Storage
```env
VECTOR_STORE_ENABLED=true/false
VECTOR_STORE_TYPE=chromadb
```

### 2. Cloud ChromaDB Support
```env
CHROMA_AUTH_TOKEN=your-token
CHROMA_API_KEY=your-api-key
CHROMA_TENANT=your-tenant
```

### 3. Optional Features
```env
EMBEDDING_ENABLED=true/false
OCR_ENABLED=true/false
USE_SIMPLE_PARSING=true/false
```

### 4. Lightweight Models
- Default: `sentence-transformers/all-MiniLM-L6-v2` (22MB)
- Alternative: `sentence-transformers/all-mpnet-base-v2` (420MB)
- Optional: Jina/Qwen models (for advanced use)

## Deployment Options

### 1. Minimal Setup (No AI/ML)
```bash
pip install -r requirements-minimal.txt
docker-compose -f docker-compose.minimal.yml up -d
```
- Only document parsing and storage
- SQLite database only
- No vector search
- Fast startup, low memory

### 2. Full Local Setup
```bash
pip install -r requirements.txt
docker-compose up -d
```
- All AI/ML features
- Local ChromaDB
- Vector search enabled
- Higher memory usage

### 3. Cloud Setup
```bash
# Configure Chroma Cloud credentials
pip install -r requirements.txt
docker-compose up -d
```
- Managed vector storage
- Reduced local resource usage
- Production ready

## Benefits

1. **Compatibility**: Python 3.12 support
2. **Flexibility**: Choose features based on needs
3. **Resource Efficient**: Minimal setup uses <100MB RAM
4. **Scalable**: Cloud vector storage option
5. **Development Friendly**: Fast local development
6. **Production Ready**: Multiple deployment options

## Migration Guide

### From Previous Version
1. Update requirements: `pip install -r requirements.txt`
2. Update environment: Copy new variables from `.env.example`
3. Choose setup type based on needs
4. Test with validation script: `python validate_deployment.py`

### For New Installations
1. Choose setup type (minimal/full/cloud)
2. Follow appropriate installation guide in `INSTALL.md`
3. Configure environment variables
4. Deploy and test

## Validation

All changes validated with:
- ✅ Python 3.12 compatibility
- ✅ Dependency conflict resolution
- ✅ Optional service loading
- ✅ Multiple deployment configurations
- ✅ Feature matrix coverage
- ✅ Error handling for missing dependencies