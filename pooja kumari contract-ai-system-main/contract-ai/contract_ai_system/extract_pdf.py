from pypdf import PdfReader

def extract_pdf(file_path: str) -> str:
    """Extract all text from a PDF file and return as string."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text
