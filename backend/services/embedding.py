import asyncio
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import tiktoken

from config import settings


class EmbeddingService:
    def __init__(self):
        self.models = {}
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    async def get_model(self, model_name: str) -> SentenceTransformer:
        """Get or load embedding model"""
        if model_name not in self.models:
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            model = await loop.run_in_executor(
                None,
                SentenceTransformer,
                model_name
            )
            self.models[model_name] = model
        return self.models[model_name]
    
    async def embed_text(self, text: str, model_name: str) -> List[float]:
        """Generate embedding for text"""
        try:
            model = await self.get_model(model_name)
            
            # Generate embedding in thread pool
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                model.encode,
                text
            )
            
            return embedding.tolist()
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    async def embed_texts(self, texts: List[str], model_name: str) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            model = await self.get_model(model_name)
            
            # Generate embeddings in thread pool
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                model.encode,
                texts
            )
            
            return [embedding.tolist() for embedding in embeddings]
        except Exception as e:
            raise Exception(f"Failed to generate embeddings: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
        """Chunk text by character count with overlap"""
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            # Count tokens in chunk
            token_count = self._count_tokens(chunk_text)
            
            chunks.append({
                "index": chunk_index,
                "content": chunk_text,
                "start_char": start,
                "end_char": min(end, len(text)),
                "token_count": token_count
            })
            
            chunk_index += 1
            start = end - overlap
            
            # Break if we've reached the end
            if end >= len(text):
                break
        
        return chunks
    
    def chunk_text_auto(self, text: str, model_name: str) -> List[Dict[str, Any]]:
        """Auto-chunk text based on model's max token limit"""
        # Get model max tokens (rough estimates)
        max_tokens_map = {
            "jinaai/jina-embeddings-v3": 8192,
            "qwen3-0.6B": 2048
        }
        
        max_tokens = max_tokens_map.get(model_name, 1000)
        
        # Convert tokens to approximate character count
        # Rough estimate: 1 token = 4 characters
        chunk_size = max_tokens * 4
        overlap = int(chunk_size * 0.1)  # 10% overlap
        
        return self.chunk_text(text, chunk_size, overlap)
    
    def should_vectorize(self, token_count: int) -> bool:
        """Determine if content should be vectorized based on token count"""
        return token_count >= settings.max_tokens_threshold
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except:
            return int(len(text.split()) * 1.3)


class ChunkingService:
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def chunk_by_tokens(self, text: str, max_tokens: int, overlap_tokens: int = 0) -> List[Dict[str, Any]]:
        """Chunk text by token count"""
        try:
            tokens = self.encoding.encode(text)
            chunks = []
            start = 0
            chunk_index = 0
            
            while start < len(tokens):
                end = min(start + max_tokens, len(tokens))
                chunk_tokens = tokens[start:end]
                chunk_text = self.encoding.decode(chunk_tokens)
                
                chunks.append({
                    "index": chunk_index,
                    "content": chunk_text,
                    "token_count": len(chunk_tokens),
                    "start_token": start,
                    "end_token": end
                })
                
                chunk_index += 1
                start = end - overlap_tokens
                
                if end >= len(tokens):
                    break
            
            return chunks
        except Exception as e:
            raise Exception(f"Failed to chunk by tokens: {str(e)}")
    
    def chunk_by_sentences(self, text: str, max_tokens: int) -> List[Dict[str, Any]]:
        """Chunk text by sentences while respecting token limits"""
        import re
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if adding sentence exceeds token limit
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            token_count = self._count_tokens(test_chunk)
            
            if token_count > max_tokens and current_chunk:
                # Save current chunk and start new one
                chunks.append({
                    "index": chunk_index,
                    "content": current_chunk.strip(),
                    "token_count": self._count_tokens(current_chunk)
                })
                chunk_index += 1
                current_chunk = sentence
            else:
                current_chunk = test_chunk
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "index": chunk_index,
                "content": current_chunk.strip(),
                "token_count": self._count_tokens(current_chunk)
            })
        
        return chunks
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except:
            return int(len(text.split()) * 1.3)