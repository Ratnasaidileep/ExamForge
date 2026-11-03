import re
import uuid
from pathlib import Path
from typing import Dict, Any, List
from pypdf import PdfReader
from docx import Document as DocxDocument
from fastapi import HTTPException, UploadFile
from app.core.config import settings

def generate_safe_filename(original_filename: str) -> str:
    ext = Path(original_filename).suffix.lower()
    clean_stem = re.sub(r'[^a-zA-Z0-9_-]', '_', Path(original_filename).stem)[:50]
    unique_suffix = uuid.uuid4().hex[:8]
    return f"{clean_stem}_{unique_suffix}{ext}"

def validate_uploaded_file(file: UploadFile, content: bytes) -> str:
    # 1. Size check
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    # 2. Extension check
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Only PDF and DOCX files are supported."
        )
    
    # 3. Magic bytes / header validation
    if ext == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="Invalid PDF file: Missing %PDF header.")
        return "pdf"
    elif ext == ".docx":
        # DOCX is a zip file starting with PK\x03\x04
        if not content.startswith(b"PK\x03\x04"):
            raise HTTPException(status_code=400, detail="Invalid DOCX file: Corrupted or invalid archive.")
        return "docx"
    
    return ext.replace(".", "")

def extract_from_pdf(file_path: Path) -> Dict[str, Any]:
    try:
        reader = PdfReader(str(file_path))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                return {
                    "status": "failed",
                    "error_message": "PDF is password protected and cannot be extracted.",
                    "full_text": "",
                    "page_count": 0,
                    "headings": [],
                    "topics": []
                }
        
        page_count = len(reader.pages)
        pages_text: List[str] = []
        headings: List[str] = []
        
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages_text.append(text)
            
            # Simple heading heuristic: lines that look like headings
            for line in text.split("\n"):
                line_str = line.strip()
                if (
                    line_str
                    and len(line_str) < 80
                    and (re.match(r'^(Unit|Chapter|Section|\d+\.|\b[A-Z0-9\s]{4,}\b)', line_str) or line_str.isupper())
                ):
                    headings.append(line_str)
        
        full_text = "\n\n".join(pages_text).strip()
        
        # Check for scanned PDF with zero extractable text
        if not full_text:
            return {
                "status": "scanned_ocr_unsupported",
                "error_message": "This PDF appears to be a scanned image with no selectable text. Optical Character Recognition (OCR) is not supported.",
                "full_text": "",
                "page_count": page_count,
                "headings": [],
                "topics": []
            }
        
        # Extract basic topics / keywords
        words = re.findall(r'\b[A-Z][a-z]{3,}\b', full_text)
        from collections import Counter
        top_words = [w for w, _ in Counter(words).most_common(12) if len(w) > 3]
        
        return {
            "status": "completed",
            "error_message": None,
            "full_text": full_text,
            "page_count": page_count,
            "headings": list(dict.fromkeys(headings))[:20],
            "topics": top_words
        }
    except Exception as e:
        return {
            "status": "failed",
            "error_message": f"PDF extraction failed: {str(e)}",
            "full_text": "",
            "page_count": 0,
            "headings": [],
            "topics": []
        }

def extract_from_docx(file_path: Path) -> Dict[str, Any]:
    try:
        doc = DocxDocument(str(file_path))
        full_paragraphs = []
        headings = []
        
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                full_paragraphs.append(text)
                if p.style and 'Heading' in p.style.name:
                    headings.append(text)
                elif len(text) < 70 and (text.isupper() or re.match(r'^(Unit|Chapter|\d+\.)', text)):
                    headings.append(text)
                    
        full_text = "\n\n".join(full_paragraphs).strip()
        
        if not full_text:
            return {
                "status": "failed",
                "error_message": "DOCX file contains no extractable paragraphs.",
                "full_text": "",
                "page_count": 1,
                "headings": [],
                "topics": []
            }
            
        words = re.findall(r'\b[A-Z][a-z]{3,}\b', full_text)
        from collections import Counter
        top_words = [w for w, _ in Counter(words).most_common(12) if len(w) > 3]
        
        return {
            "status": "completed",
            "error_message": None,
            "full_text": full_text,
            "page_count": max(1, len(full_paragraphs) // 10),
            "headings": list(dict.fromkeys(headings))[:20],
            "topics": top_words
        }
    except Exception as e:
        return {
            "status": "failed",
            "error_message": f"DOCX extraction failed: {str(e)}",
            "full_text": "",
            "page_count": 0,
            "headings": [],
            "topics": []
        }
