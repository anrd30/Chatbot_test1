from PyPDF2 import PdfReader
import os

def is_text_pdf(pdf_path):
    """Check if the PDF contains extractable text."""
    reader = PdfReader(pdf_path)
    return any(page.extract_text() for page in reader.pages)

def extract_text(pdf_path, cache=True):
    """Extract text from PDF (text-based only, no OCR)."""
    txt_file = pdf_path.replace(".pdf", ".txt")
    
    # ✅ Use cached version if available
    if cache and os.path.exists(txt_file):
        with open(txt_file, "r", encoding="utf-8") as f:
            return f.read()
    
    text = ""
    if is_text_pdf(pdf_path):
        reader = PdfReader(pdf_path)
        text = "\n".join(
            [page.extract_text() for page in reader.pages if page.extract_text()]
        )
        
        # ✅ Save to cache
        if cache:
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(text)
    else:
        print(f"⚠️ Skipping {pdf_path}: No extractable text (image-based PDF).")
    
    return text
