from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Header, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
import aiofiles
from datetime import datetime

from database import get_db, Project, Document, Job, VectorChunk
from schemas import *
from auth import verify_x_api_key
from services.parsing import DocumentParser, WebScraper
from services.embedding import EmbeddingService
from services.vector_store import VectorSearchService
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Knowledge Base Service",
    description="A pure knowledge base service with document parsing, embedding, and search",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
parser = DocumentParser()
scraper = WebScraper()
embedding_service = EmbeddingService()
vector_service = VectorSearchService()

# Global job storage (in production, use Redis or database)
jobs = {}


async def create_job(project_id: int, job_type: str) -> str:
    """Create a new background job"""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "id": job_id,
        "project_id": project_id,
        "job_type": job_type,
        "status": "pending",
        "progress": 0.0,
        "result": None,
        "error_message": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    return job_id


async def update_job(job_id: str, status: str, progress: float = None, result: dict = None, error: str = None):
    """Update job status"""
    if job_id in jobs:
        jobs[job_id]["status"] = status
        jobs[job_id]["updated_at"] = datetime.utcnow()
        if progress is not None:
            jobs[job_id]["progress"] = progress
        if result is not None:
            jobs[job_id]["result"] = result
        if error is not None:
            jobs[job_id]["error_message"] = error


# API Endpoints

@app.get("/")
async def root():
    return {"message": "Knowledge Base Service API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    vector_health = await vector_service.health_check()
    return {
        "status": "healthy",
        "database": "connected",
        "vector_store": "connected" if vector_health else "disabled/disconnected",
        "embedding_service": "enabled" if embedding_service.is_enabled() else "disabled",
        "vector_search": "enabled" if vector_service.is_enabled() else "disabled",
        "ocr": "enabled" if settings.ocr_enabled else "disabled",
        "timestamp": datetime.utcnow()
    }


# Projects CRUD
@app.post("/api/v1/projects", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="x-api-key")
):
    """Create a new project"""
    verify_x_api_key(x_api_key)
    
    db_project = Project(
        name=project.name,
        description=project.description
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return db_project


@app.get("/api/v1/projects", response_model=List[ProjectResponse])
async def list_projects(
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="x-api-key")
):
    """List all projects"""
    verify_x_api_key(x_api_key)
    return db.query(Project).all()


@app.get("/api/v1/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="x-api-key")
):
    """Get project by ID"""
    verify_x_api_key(x_api_key)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.get("/api/v1/projects/{project_id}/documents", response_model=List[DocumentResponse])
async def list_project_documents(
    project_id: int,
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="x-api-key")
):
    """List documents in a project"""
    verify_x_api_key(x_api_key)
    
    # Check if project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return db.query(Document).filter(Document.project_id == project_id).all()


# File Upload
@app.post("/api/v1/projects/{project_id}/upload", response_model=UploadResponse)
async def upload_files(
    project_id: int,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="x-api-key")
):
    """Upload and parse documents"""
    verify_x_api_key(x_api_key)
    
    # Check if project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create job
    job_id = await create_job(project_id, "upload_and_parse")
    
    # Process files in background
    background_tasks.add_task(process_uploaded_files, job_id, project_id, files, db)
    
    return UploadResponse(
        job_id=job_id,
        message=f"Processing {len(files)} files"
    )


async def process_uploaded_files(job_id: str, project_id: int, files: List[UploadFile], db: Session):
    """Background task to process uploaded files"""
    try:
        await update_job(job_id, "running", 0.0)
        
        os.makedirs(settings.upload_dir, exist_ok=True)
        total_files = len(files)
        processed_documents = []
        
        for i, file in enumerate(files):
            try:
                # Save file
                file_path = os.path.join(settings.upload_dir, f"{uuid.uuid4().hex}_{file.filename}")
                async with aiofiles.open(file_path, 'wb') as f:
                    content = await file.read()
                    await f.write(content)
                
                # Parse document
                parse_result = await parser.parse_document(file_path, file.filename)
                
                # Save to database
                document = Document(
                    project_id=project_id,
                    filename=file.filename,
                    file_path=file_path,
                    file_type=parse_result["file_type"],
                    file_size=len(content),
                    raw_content=parse_result["raw_content"],
                    parsed_content=parse_result["parsed_content"],
                    token_count=parse_result["token_count"],
                    metadata=parse_result["metadata"]
                )
                db.add(document)
                db.commit()
                db.refresh(document)
                
                processed_documents.append({
                    "id": document.id,
                    "filename": document.filename,
                    "token_count": document.token_count
                })
                
                # Update progress
                progress = (i + 1) / total_files
                await update_job(job_id, "running", progress)
                
            except Exception as e:
                print(f"Error processing file {file.filename}: {str(e)}")
                continue
        
        await update_job(
            job_id, 
            "completed", 
            1.0, 
            {"processed_documents": processed_documents}
        )
        
    except Exception as e:
        await update_job(job_id, "failed", error=str(e))


# URL Scraping
@app.post("/api/v1/projects/{project_id}/scrape", response_model=UploadResponse)
async def scrape_url(
    project_id: int,
    scrape_request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="x-api-key")
):
    """Scrape content from URL"""
    verify_x_api_key(x_api_key)
    
    # Check if project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create job
    job_id = await create_job(project_id, "scrape_url")
    
    # Process in background
    background_tasks.add_task(process_url_scrape, job_id, project_id, scrape_request, db)
    
    return UploadResponse(
        job_id=job_id,
        message=f"Scraping URL: {scrape_request.url}"
    )


async def process_url_scrape(job_id: str, project_id: int, scrape_request: ScrapeRequest, db: Session):
    """Background task to scrape URL"""
    try:
        await update_job(job_id, "running", 0.5)
        
        # Scrape content
        scrape_result = await scraper.scrape_url(
            scrape_request.url, 
            scrape_request.include_links
        )
        
        # Save to database
        document = Document(
            project_id=project_id,
            filename=f"scraped_{scrape_request.url.replace('/', '_')}",
            file_path="",  # No file path for scraped content
            file_type="web",
            file_size=len(scrape_result["raw_content"]),
            raw_content=scrape_result["raw_content"],
            parsed_content=scrape_result["parsed_content"],
            token_count=scrape_result["token_count"],
            metadata=scrape_result["metadata"]
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        await update_job(
            job_id, 
            "completed", 
            1.0, 
            {"document_id": document.id, "token_count": document.token_count}
        )
        
    except Exception as e:
        await update_job(job_id, "failed", error=str(e))


# Indexing
@app.post("/api/v1/projects/{project_id}/index", response_model=UploadResponse)
async def index_project(
    project_id: int,
    index_request: IndexRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="x-api-key")
):
    """Index project documents"""
    verify_x_api_key(x_api_key)
    
    # Check if project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create job
    job_id = await create_job(project_id, "indexing")
    
    # Process in background
    background_tasks.add_task(process_indexing, job_id, project_id, index_request, db)
    
    return UploadResponse(
        job_id=job_id,
        message="Starting indexing process"
    )


async def process_indexing(job_id: str, project_id: int, index_request: IndexRequest, db: Session):
    """Background task to index documents"""
    try:
        await update_job(job_id, "running", 0.0)
        
        # Get all documents for the project
        documents = db.query(Document).filter(Document.project_id == project_id).all()
        
        if not documents:
            await update_job(job_id, "completed", 1.0, {"message": "No documents to index"})
            return
        
        total_docs = len(documents)
        indexed_docs = []
        
        for i, document in enumerate(documents):
            try:
                # Check if document should be vectorized
                should_vectorize = embedding_service.should_vectorize(document.token_count)
                
                if not should_vectorize:
                    # Skip vectorization for small documents
                    document.is_vectorized = False
                    indexed_docs.append({
                        "id": document.id,
                        "filename": document.filename,
                        "vectorized": False,
                        "reason": f"Token count ({document.token_count}) below threshold"
                    })
                else:
                    # Vectorize document
                    if index_request.mode == IndexingMode.auto:
                        chunks = embedding_service.chunk_text_auto(
                            document.parsed_content, 
                            index_request.embedding_model.value
                        )
                    else:
                        # Manual chunking
                        chunk_size = index_request.chunk_size or settings.default_chunk_size
                        chunk_overlap = index_request.chunk_overlap or settings.default_chunk_overlap
                        chunks = embedding_service.chunk_text(
                            document.parsed_content, 
                            chunk_size, 
                            chunk_overlap
                        )
                    
                    # Generate embeddings
                    chunk_texts = [chunk["content"] for chunk in chunks]
                    embeddings = await embedding_service.embed_texts(
                        chunk_texts, 
                        index_request.embedding_model.value
                    )
                    
                    # Store in vector database
                    vector_ids = await vector_service.index_document(
                        document.id, 
                        chunks, 
                        embeddings
                    )
                    
                    # Save chunks to database
                    for chunk, vector_id in zip(chunks, vector_ids):
                        vector_chunk = VectorChunk(
                            document_id=document.id,
                            chunk_index=chunk["index"],
                            content=chunk["content"],
                            vector_id=vector_id,
                            metadata=chunk
                        )
                        db.add(vector_chunk)
                    
                    document.is_vectorized = True
                    indexed_docs.append({
                        "id": document.id,
                        "filename": document.filename,
                        "vectorized": True,
                        "chunks": len(chunks)
                    })
                
                db.commit()
                
                # Update progress
                progress = (i + 1) / total_docs
                await update_job(job_id, "running", progress)
                
            except Exception as e:
                print(f"Error indexing document {document.id}: {str(e)}")
                indexed_docs.append({
                    "id": document.id,
                    "filename": document.filename,
                    "vectorized": False,
                    "error": str(e)
                })
                continue
        
        await update_job(
            job_id, 
            "completed", 
            1.0, 
            {"indexed_documents": indexed_docs}
        )
        
    except Exception as e:
        await update_job(job_id, "failed", error=str(e))


# Query
@app.post("/api/v1/projects/{project_id}/query", response_model=QueryResponse)
async def query_project(
    project_id: int,
    query_request: QueryRequest,
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="x-api-key")
):
    """Query project documents"""
    verify_x_api_key(x_api_key)
    
    # Check if project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get project documents
    documents = db.query(Document).filter(Document.project_id == project_id).all()
    
    if not documents:
        return QueryResponse(
            query=query_request.query,
            results=[],
            is_vectorized=False,
            total_results=0
        )
    
    # Check if any documents are vectorized
    vectorized_docs = [doc for doc in documents if doc.is_vectorized]
    
    if not vectorized_docs:
        # Return raw content for non-vectorized documents
        results = []
        for doc in documents[:query_request.top_k]:
            results.append(QueryResult(
                content=doc.raw_content[:1000] + "..." if len(doc.raw_content) > 1000 else doc.raw_content,
                metadata={
                    "document_id": doc.id,
                    "filename": doc.filename,
                    "token_count": doc.token_count
                } if query_request.include_metadata else None
            ))
        
        return QueryResponse(
            query=query_request.query,
            results=results,
            is_vectorized=False,
            total_results=len(documents)
        )
    
    else:
        # Perform vector search
        try:
            # Generate query embedding
            query_embedding = await embedding_service.embed_text(
                query_request.query,
                settings.default_embedding_model
            )
            
            # Search vectors
            vector_results = await vector_service.search_documents(
                query_embedding,
                query_request.top_k,
                [doc.id for doc in vectorized_docs]
            )
            
            # Format results
            results = []
            for result in vector_results:
                results.append(QueryResult(
                    content=result["content"],
                    metadata=result["metadata"] if query_request.include_metadata else None,
                    score=result["score"]
                ))
            
            return QueryResponse(
                query=query_request.query,
                results=results,
                is_vectorized=True,
                total_results=len(vector_results)
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# Job Status
@app.get("/api/v1/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    x_api_key: str = Header(..., alias="x-api-key")
):
    """Get job status"""
    verify_x_api_key(x_api_key)
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return JobResponse(**job)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)