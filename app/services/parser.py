from pypdf import PdfReader
from concurrent.futures import ThreadPoolExecutor

def extract_page_text(page):
    """
    Helper function to extract text from a single PDF page.
    """
    try:
        return page.extract_text() or ""
    except Exception:
        return ""

def parse_pdf(file):
    """
    Main entry point for PDF parsing. Uses a ThreadPoolExecutor 
    to speed up text extraction for large documents.
    """
    reader = PdfReader(file.file)
    pages = reader.pages
    
    # Check if we should parallelize
    num_threads = min(8, len(pages))
    
    if num_threads <= 1:
        text = "".join([page.extract_text() or "" for page in pages])
    else:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            text_parts = list(executor.map(extract_page_text, pages))
        text = "".join(text_parts)
        
    return text
