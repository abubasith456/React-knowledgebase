import os
import uuid
from typing import Optional, Dict, Any
from pathlib import Path
import asyncio
import aiofiles

# Document processing imports - Docling is primary
from docling.document_converter import DocumentConverter
import tiktoken

from config import settings


class DocumentParser:
    def __init__(self):
        self.converter = DocumentConverter()
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
    
    async def parse_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Parse document and extract text content using Docling"""
        try:
            file_ext = Path(filename).suffix.lower()
            
            # Use Docling for all supported formats
            if file_ext in ['.pdf', '.docx', '.pptx', '.ppt', '.html', '.md', '.txt']:
                content = await self._parse_with_docling(file_path)
            elif file_ext in ['.txt', '.md']:
                # Direct text parsing for simple formats
                content = await self._parse_text(file_path)
            else:
                # Try Docling for any other format
                content = await self._parse_with_docling(file_path)
            
            # Count tokens
            token_count = self._count_tokens(content)
            
            return {
                "raw_content": content,
                "parsed_content": content,
                "token_count": token_count,
                "file_type": file_ext,
                "metadata": {
                    "parsing_method": "Docling" if file_ext != '.txt' and file_ext != '.md' else "Direct text",
                    "original_filename": filename,
                    "file_extension": file_ext
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse document: {str(e)}")
    
    async def _parse_with_docling(self, file_path: str) -> str:
        """Parse document using Docling converter"""
        try:
            # Run Docling in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.converter.convert,
                file_path
            )
            
            # Extract text content
            if result.document and hasattr(result.document, 'main_text'):
                return result.document.main_text
            elif result.document and hasattr(result.document, 'text'):
                return result.document.text
            else:
                # Try to extract any text content from the document
                return str(result.document) if result.document else ""
                
        except Exception as e:
            raise Exception(f"Docling parsing failed: {str(e)}")
    
    async def _parse_text(self, file_path: str) -> str:
        """Parse plain text files directly"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
            return content
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                async with aiofiles.open(file_path, 'r', encoding='latin-1') as file:
                    content = await file.read()
                return content
            except Exception as e:
                raise Exception(f"Text parsing failed: {str(e)}")
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except:
            # Fallback to word count * 1.3 (rough token approximation)
            return int(len(text.split()) * 1.3)


class WebScraper:
    def __init__(self):
        self.converter = DocumentConverter()
    
    async def scrape_url(self, url: str, include_links: bool = False) -> Dict[str, Any]:
        """Scrape web content using Docling"""
        try:
            # Use Docling to convert web content
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.converter.convert,
                url
            )
            
            content = ""
            if result.document and hasattr(result.document, 'main_text'):
                content = result.document.main_text
            elif result.document and hasattr(result.document, 'text'):
                content = result.document.text
            else:
                content = str(result.document) if result.document else ""
            
            # Count tokens
            encoding = tiktoken.get_encoding("cl100k_base")
            token_count = len(encoding.encode(content))
            
            return {
                "raw_content": content,
                "parsed_content": content,
                "token_count": token_count,
                "file_type": "web",
                "metadata": {
                    "source_url": url,
                    "parsing_method": "Docling web scraper",
                    "include_links": include_links
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to scrape URL: {str(e)}")