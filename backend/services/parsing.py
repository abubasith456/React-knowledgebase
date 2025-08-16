import os
import uuid
from typing import Optional, Dict, Any
from pathlib import Path
import asyncio
import aiofiles
import mimetypes

# Document processing imports
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
import easyocr
from PIL import Image
import PyPDF2
from docx import Document as DocxDocument
from pptx import Presentation
import tiktoken

from config import settings


class DocumentParser:
    def __init__(self):
        self.converter = DocumentConverter()
        self.ocr_reader = easyocr.Reader(['en']) if settings.ocr_enabled else None
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
    
    async def parse_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Parse document and extract text content"""
        try:
            file_ext = Path(filename).suffix.lower()
            
            if file_ext == '.pdf':
                content = await self._parse_pdf(file_path)
            elif file_ext == '.docx':
                content = await self._parse_docx(file_path)
            elif file_ext in ['.pptx', '.ppt']:
                content = await self._parse_pptx(file_path)
            elif file_ext in ['.txt', '.md']:
                content = await self._parse_text(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                content = await self._parse_image(file_path)
            else:
                # Try Docling for other formats
                content = await self._parse_with_docling(file_path)
            
            # Count tokens
            token_count = self._count_tokens(content)
            
            return {
                "raw_content": content,
                "parsed_content": content,
                "token_count": token_count,
                "file_type": file_ext,
                "metadata": {
                    "parsing_method": self._get_parsing_method(file_ext),
                    "original_filename": filename
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse document: {str(e)}")
    
    async def _parse_pdf(self, file_path: str) -> str:
        """Parse PDF using PyPDF2 and fallback to Docling"""
        try:
            content = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
            
            # If PyPDF2 extraction is poor, try Docling
            if len(content.strip()) < 100:
                content = await self._parse_with_docling(file_path)
            
            return content.strip()
        except:
            return await self._parse_with_docling(file_path)
    
    async def _parse_docx(self, file_path: str) -> str:
        """Parse DOCX using python-docx"""
        try:
            doc = DocxDocument(file_path)
            content = ""
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            return content.strip()
        except:
            return await self._parse_with_docling(file_path)
    
    async def _parse_pptx(self, file_path: str) -> str:
        """Parse PPTX using python-pptx"""
        try:
            prs = Presentation(file_path)
            content = ""
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        content += shape.text + "\n"
            return content.strip()
        except:
            return await self._parse_with_docling(file_path)
    
    async def _parse_text(self, file_path: str) -> str:
        """Parse text files"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            content = await file.read()
        return content
    
    async def _parse_image(self, file_path: str) -> str:
        """Parse images using OCR"""
        if not self.ocr_reader:
            raise Exception("OCR is disabled")
        
        try:
            # Run OCR in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.ocr_reader.readtext, 
                file_path
            )
            
            # Extract text from OCR results
            content = ""
            for detection in result:
                content += detection[1] + " "
            
            return content.strip()
        except Exception as e:
            raise Exception(f"OCR failed: {str(e)}")
    
    async def _parse_with_docling(self, file_path: str) -> str:
        """Parse document using Docling converter"""
        try:
            # Run Docling in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.converter.convert,
                file_path
            )
            
            # Extract text content
            if result.document and result.document.main_text:
                return result.document.main_text
            else:
                return ""
        except Exception as e:
            raise Exception(f"Docling parsing failed: {str(e)}")
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except:
            # Fallback to word count * 1.3 (rough token approximation)
            return int(len(text.split()) * 1.3)
    
    def _get_parsing_method(self, file_ext: str) -> str:
        """Get the parsing method used for the file type"""
        method_map = {
            '.pdf': 'PyPDF2 + Docling fallback',
            '.docx': 'python-docx + Docling fallback',
            '.pptx': 'python-pptx + Docling fallback',
            '.ppt': 'python-pptx + Docling fallback',
            '.txt': 'direct text',
            '.md': 'direct text',
            '.png': 'EasyOCR',
            '.jpg': 'EasyOCR',
            '.jpeg': 'EasyOCR'
        }
        return method_map.get(file_ext, 'Docling')


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
            if result.document and result.document.main_text:
                content = result.document.main_text
            
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