"""Document parsing utilities."""
from typing import List, Dict
from pathlib import Path
import pypdf
from docx import Document


class DocumentParser:
    """Handles parsing of various document formats."""
    
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.txt']
    
    @staticmethod
    def parse_document(file_path: str) -> Dict[str, any]:
        """
        Parse a document and extract text content.
        
        Args:
            file_path: Path to the document file
        
        Returns:
            Dictionary with 'text' and 'metadata' keys
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = file_path.suffix.lower()
        
        if not file_ext:
            raise ValueError(
                f"File has no extension: {file_path}\n"
                f"Supported formats: {', '.join(DocumentParser.SUPPORTED_FORMATS)}\n"
                f"Please ensure your file has a valid extension (.pdf, .docx, or .txt)"
            )
        
        if file_ext == '.pdf':
            return DocumentParser._parse_pdf(file_path)
        elif file_ext == '.docx':
            return DocumentParser._parse_docx(file_path)
        elif file_ext == '.txt':
            return DocumentParser._parse_txt(file_path)
        else:
            raise ValueError(
                f"Unsupported file format: {file_ext}\n"
                f"Supported formats: {', '.join(DocumentParser.SUPPORTED_FORMATS)}\n"
                f"File provided: {file_path}"
            )
    
    @staticmethod
    def _parse_pdf(file_path: Path) -> Dict[str, any]:
        """Parse PDF file."""
        text_parts = []
        metadata = {
            "file_name": file_path.name,
            "file_type": "pdf",
            "file_size": file_path.stat().st_size
        }
        
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            metadata["num_pages"] = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text_parts.append(page_text)
        
        return {
            "text": "\n\n".join(text_parts),
            "metadata": metadata
        }
    
    @staticmethod
    def _parse_docx(file_path: Path) -> Dict[str, any]:
        """Parse DOCX file."""
        doc = Document(file_path)
        text_parts = []
        
        for paragraph in doc.paragraphs:
            text_parts.append(paragraph.text)
        
        metadata = {
            "file_name": file_path.name,
            "file_type": "docx",
            "file_size": file_path.stat().st_size
        }
        
        return {
            "text": "\n\n".join(text_parts),
            "metadata": metadata
        }
    
    @staticmethod
    def _parse_txt(file_path: Path) -> Dict[str, any]:
        """Parse TXT file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        metadata = {
            "file_name": file_path.name,
            "file_type": "txt",
            "file_size": file_path.stat().st_size
        }
        
        return {
            "text": text,
            "metadata": metadata
        }
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict[str, any]]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
        
        Returns:
            List of chunk dictionaries with 'text' and 'chunk_index'
        """
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        chunk_index = 0
        
        for word in words:
            word_length = len(word) + 1
            
            if current_length + word_length > chunk_size and current_chunk:
                chunks.append({
                    "text": " ".join(current_chunk),
                    "chunk_index": chunk_index
                })
                chunk_index += 1
                
                overlap_words = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else current_chunk
                current_chunk = overlap_words + [word]
                current_length = sum(len(w) + 1 for w in current_chunk)
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append({
                "text": " ".join(current_chunk),
                "chunk_index": chunk_index
            })
        
        return chunks


