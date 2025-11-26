import pdfplumber
import PyPDF2
import fitz  # PyMuPDF
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text from PDF files using multiple methods for reliability"""
    
    @staticmethod
    def extract_with_pdfplumber(pdf_path: str) -> Optional[str]:
        """Extract text using pdfplumber (best for layout preservation)"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            return text.strip()
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            return None
    
    @staticmethod
    def extract_with_pypdf2(pdf_path: str) -> Optional[str]:
        """Extract text using PyPDF2 (fallback method)"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            return text.strip()
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            return None
    
    @staticmethod
    def extract_with_pymupdf(pdf_path: str) -> Optional[str]:
        """Extract text using PyMuPDF (most robust)"""
        try:
            text = ""
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text() + "\n\n"
            doc.close()
            return text.strip()
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            return None
    
    @classmethod
    def extract_text(cls, pdf_path: str) -> str:
        """
        Extract text from PDF using multiple methods for best results
        Returns the first successful extraction
        """
        # Try methods in order of reliability
        methods = [
            cls.extract_with_pdfplumber,
            cls.extract_with_pymupdf,
            cls.extract_with_pypdf2,
        ]
        
        for method in methods:
            try:
                text = method(pdf_path)
                if text and len(text.strip()) > 50:  # Valid text threshold
                    logger.info(f"Successfully extracted text using {method.__name__}")
                    return text
            except Exception as e:
                logger.warning(f"{method.__name__} failed: {e}")
                continue
        
        raise ValueError("Could not extract text from PDF using any available method")