import logging
from typing import List, Dict, Any, Optional, Tuple
import uuid
import asyncio

from config import settings

# Optional ChromaDB import
try:
    if settings.vector_store_enabled and settings.vector_store_type == "chromadb":
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        CHROMADB_AVAILABLE = True
    else:
        CHROMADB_AVAILABLE = False
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available. Vector operations will be disabled.")


class VectorStore:
    def __init__(self):
        self.client = None
        self.collection = None
        self.enabled = settings.vector_store_enabled and CHROMADB_AVAILABLE
    
    async def initialize(self):
        """Initialize ChromaDB client and collection"""
        if not self.enabled:
            return
            
        try:
            client_settings = settings.get_chroma_client_settings()
            
            if settings.is_chroma_cloud():
                # Cloud configuration
                self.client = chromadb.CloudClient(**client_settings)
            else:
                # Local configuration
                self.client = chromadb.HttpClient(**client_settings)
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=settings.chroma_collection_name
                )
            except:
                self.collection = self.client.create_collection(
                    name=settings.chroma_collection_name,
                    metadata={"description": "Knowledge base documents"}
                )
            
        except Exception as e:
            logging.error(f"Failed to initialize vector store: {str(e)}")
            self.enabled = False
            raise Exception(f"Failed to initialize vector store: {str(e)}")
    
    async def add_vectors(
        self, 
        document_id: int, 
        chunks: List[Dict[str, Any]], 
        embeddings: List[List[float]]
    ) -> List[str]:
        """Add vectors to the collection"""
        if not self.enabled:
            return []
            
        if not self.collection:
            await self.initialize()
        
        try:
            vector_ids = []
            documents = []
            metadatas = []
            ids = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"doc_{document_id}_chunk_{chunk['index']}_{uuid.uuid4().hex[:8]}"
                vector_ids.append(vector_id)
                
                documents.append(chunk['content'])
                metadatas.append({
                    "document_id": document_id,
                    "chunk_index": chunk['index'],
                    "start_char": chunk.get('start_char', 0),
                    "end_char": chunk.get('end_char', 0),
                    "token_count": chunk.get('token_count', 0)
                })
                ids.append(vector_id)
            
            # Add to ChromaDB in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.collection.add,
                embeddings,
                metadatas,
                documents,
                ids
            )
            
            return vector_ids
            
        except Exception as e:
            raise Exception(f"Failed to add vectors: {str(e)}")
    
    async def search_vectors(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        document_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        if not self.enabled:
            return []
            
        if not self.collection:
            await self.initialize()
        
        try:
            # Prepare where clause for filtering by document IDs
            where_clause = None
            if document_ids:
                where_clause = {"document_id": {"$in": document_ids}}
            
            # Search in thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self.collection.query,
                [query_embedding],
                top_k,
                where_clause,
                None,  # where_document
                True,  # include distances
                True,  # include documents
                True   # include metadatas
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "score": 1.0 - results['distances'][0][i]  # Convert distance to similarity
                })
            
            return formatted_results
            
        except Exception as e:
            raise Exception(f"Failed to search vectors: {str(e)}")
    
    async def delete_document_vectors(self, document_id: int):
        """Delete all vectors for a document"""
        if not self.enabled:
            return
            
        if not self.collection:
            await self.initialize()
        
        try:
            # Delete vectors by document_id in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.collection.delete,
                None,  # ids
                {"document_id": document_id}  # where
            )
        except Exception as e:
            raise Exception(f"Failed to delete document vectors: {str(e)}")
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        if not self.enabled:
            return {"total_vectors": 0, "collection_name": "disabled"}
            
        if not self.collection:
            await self.initialize()
        
        try:
            # Get count in thread pool
            loop = asyncio.get_event_loop()
            count = await loop.run_in_executor(
                None,
                self.collection.count
            )
            
            return {
                "total_vectors": count,
                "collection_name": settings.chroma_collection_name,
                "enabled": True
            }
        except Exception as e:
            return {
                "total_vectors": 0,
                "collection_name": settings.chroma_collection_name,
                "enabled": False,
                "error": str(e)
            }
    
    async def health_check(self) -> bool:
        """Check if vector store is healthy"""
        if not self.enabled:
            return False
            
        try:
            if not self.client:
                await self.initialize()
            
            # Simple health check
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.client.heartbeat
            )
            return True
        except:
            return False


class VectorSearchService:
    def __init__(self):
        self.vector_store = VectorStore()
    
    async def index_document(
        self, 
        document_id: int, 
        chunks: List[Dict[str, Any]], 
        embeddings: List[List[float]]
    ) -> List[str]:
        """Index document chunks with embeddings"""
        if not self.vector_store.enabled:
            return []
            
        try:
            # Delete existing vectors for this document
            await self.vector_store.delete_document_vectors(document_id)
            
            # Add new vectors
            vector_ids = await self.vector_store.add_vectors(
                document_id, chunks, embeddings
            )
            
            return vector_ids
        except Exception as e:
            raise Exception(f"Failed to index document: {str(e)}")
    
    async def search_documents(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        document_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """Search documents by embedding similarity"""
        if not self.vector_store.enabled:
            return []
            
        return await self.vector_store.search_vectors(
            query_embedding, top_k, document_ids
        )
    
    async def delete_document(self, document_id: int):
        """Delete all vectors for a document"""
        if self.vector_store.enabled:
            await self.vector_store.delete_document_vectors(document_id)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return await self.vector_store.get_collection_stats()
    
    async def health_check(self) -> bool:
        """Check vector store health"""
        return await self.vector_store.health_check()
    
    def is_enabled(self) -> bool:
        """Check if vector search is enabled"""
        return self.vector_store.enabled