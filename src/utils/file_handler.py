import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts raw text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def save_text_to_file(text: str, file_path: str):
    """Saves text to a file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text) 