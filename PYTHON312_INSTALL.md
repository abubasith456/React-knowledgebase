# Python 3.12 Installation Guide

## The Problem

PyTorch and some ML libraries don't have pre-built wheels for Python 3.12 yet, causing installation failures.

## Solutions (Choose One)

### Option 1: Minimal Setup (Recommended)
**Best for**: Testing, development, high-quality document processing

```bash
cd backend
pip install -r requirements-minimal.txt
```

**Features included**:
- ✅ Document upload & parsing (PDF, DOCX, PPTX, TXT, MD, HTML)
- ✅ High-quality Docling parsing
- ✅ Web scraping with Docling
- ✅ Token counting
- ✅ Raw content search
- ❌ Vector embeddings
- ❌ Semantic search

### Option 2: Lite Setup (ChromaDB without ML)
**Best for**: Vector storage without heavy ML dependencies

```bash
cd backend
pip install -r requirements-lite.txt
```

**Features included**:
- ✅ All minimal features
- ✅ ChromaDB vector storage
- ✅ Basic vector operations
- ❌ Automatic embeddings (you can add pre-computed ones)

### Option 3: Use Python 3.11
**Best for**: Full ML/AI features

```bash
# Install Python 3.11 (using pyenv)
pyenv install 3.11.7
pyenv local 3.11.7

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install full requirements
pip install -r requirements.txt
```

### Option 4: Force PyTorch Installation
**Best for**: Advanced users willing to compile from source

```bash
cd backend

# Install without PyTorch first
pip install -r requirements-minimal.txt

# Install PyTorch nightly (has Python 3.12 support)
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu

# Install sentence transformers
pip install sentence-transformers

# Install ChromaDB
pip install chromadb
```

### Option 5: Docker Deployment
**Best for**: Production, avoiding local dependency issues

```bash
# Use Docker to avoid Python version issues
docker-compose up -d

# Or minimal Docker setup
docker-compose -f docker-compose.minimal.yml up -d
```

## Configuration for Each Option

### Minimal Setup (.env)
```env
VECTOR_STORE_ENABLED=false
EMBEDDING_ENABLED=false
OCR_ENABLED=false
USE_SIMPLE_PARSING=true
```

### Lite Setup (.env)
```env
VECTOR_STORE_ENABLED=true
EMBEDDING_ENABLED=false  # No automatic embeddings
OCR_ENABLED=false
USE_SIMPLE_PARSING=true
```

### Full Setup (.env)
```env
VECTOR_STORE_ENABLED=true
EMBEDDING_ENABLED=true
OCR_ENABLED=true
USE_SIMPLE_PARSING=false
DEFAULT_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Testing Your Installation

```bash
# Test API functionality
python test_api.py

# Validate installation
python validate_deployment.py

# Start development server
uvicorn main:app --reload
```

## Feature Comparison

| Feature | Minimal | Lite | Full |
|---------|---------|------|------|
| Python 3.12 | ✅ | ✅ | ❌ |
| Document Parsing | ✅ | ✅ | ✅ |
| Vector Storage | ❌ | ✅ | ✅ |
| Auto Embeddings | ❌ | ❌ | ✅ |
| Semantic Search | ❌ | ❌ | ✅ |
| OCR Support | ❌ | ❌ | ✅ |
| Install Time | 30s | 2min | 10min |
| Dependencies | 20 | 30 | 50+ |

## Troubleshooting

### Error: "No wheels for torch"
**Solution**: Use Option 1 (Minimal) or Option 5 (Docker)

### Error: "sentence-transformers not found"
**Solution**: Either disable embeddings or use Python 3.11

### Error: "chromadb connection failed"
**Solution**: Set `VECTOR_STORE_ENABLED=false` for basic operation

### Error: "numpy version conflict"
**Solution**: Use `pip install numpy>=1.24.0` (flexible version)

## Recommended Approach

1. **Start with Minimal**: Get basic functionality working first
2. **Test Core Features**: Upload documents, test parsing
3. **Upgrade as Needed**: Add vector search when PyTorch supports Python 3.12
4. **Use Docker for Production**: Avoids all compatibility issues

## When PyTorch Supports Python 3.12

Check PyTorch website for Python 3.12 wheel availability:
- https://pytorch.org/get-started/locally/
- When available, update `requirements.txt` with the new version
- Run `pip install -r requirements.txt` to upgrade

## Quick Commands

```bash
# Minimal (always works)
pip install -r requirements-minimal.txt
VECTOR_STORE_ENABLED=false uvicorn main:app --reload

# Docker (always works)
docker-compose -f docker-compose.minimal.yml up -d

# Check what's working
curl -H "x-api-key: dev-api-key" http://localhost:8000/health
```