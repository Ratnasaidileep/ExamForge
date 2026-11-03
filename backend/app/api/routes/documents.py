import os
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Document, DocumentContent, Subject, DemoUser
from app.schemas.document import DocumentResponse, DocumentContentResponse, DocumentUpdate
from app.services.extractor import (
    generate_safe_filename, validate_uploaded_file,
    extract_from_pdf, extract_from_docx, extract_from_txt
)
from app.core.config import settings
from app.api.deps import require_faculty

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    subject_id: Optional[str] = Form("ITS-401"),
    unit_number: Optional[str] = Form("1"),
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """
    Uploads notes in PDF, DOCX, or TXT format, extracts textual content, and detects structure/headings.
    """
    content = await file.read()
    file_type = validate_uploaded_file(file, content)
    
    safe_name = generate_safe_filename(file.filename or "notes.pdf")
    destination_path = settings.STORAGE_UPLOADS_DIR / safe_name
    
    with open(destination_path, "wb") as f:
        f.write(content)
        
    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    
    # Safely parse unit_number
    parsed_unit = 1
    if unit_number:
        try:
            parsed_unit = int(unit_number)
        except (ValueError, TypeError):
            parsed_unit = 1

    # Extract text based on file format
    if file_type == "pdf":
        ext_result = extract_from_pdf(destination_path)
    elif file_type == "docx":
        ext_result = extract_from_docx(destination_path)
    else:
        ext_result = extract_from_txt(destination_path)
        
    doc = Document(
        id=doc_id,
        title=title,
        subject_id=subject_id or "ITS-401",
        unit_number=parsed_unit,
        original_filename=file.filename or safe_name,
        safe_filename=safe_name,
        file_type=file_type,
        file_size=len(content),
        extraction_status=ext_result["status"],
        error_message=ext_result.get("error_message"),
        detected_headings=ext_result.get("headings", []),
        is_demo_seed=False
    )
    db.add(doc)
    db.flush()
    
    doc_content = DocumentContent(
        document_id=doc.id,
        full_text=ext_result.get("full_text", ""),
        page_count=ext_result.get("page_count", 1),
        cleaned_text=ext_result.get("full_text", ""),
        topics_json=ext_result.get("topics", [])
    )
    db.add(doc_content)
    db.commit()
    db.refresh(doc)
    
    return doc

@router.post("/sample", response_model=DocumentResponse)
def create_sample_document(
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """
    Creates and loads a rich sample course document (ITS-401 lecture notes)
    directly into the Document Library for rapid demonstration.
    """
    from app.services.seed_service import ITS_DOCUMENT_TEXT
    
    doc_id = f"doc_sample_{uuid.uuid4().hex[:8]}"
    safe_name = f"its_lecture_notes_sample_{uuid.uuid4().hex[:6]}.txt"
    destination_path = settings.STORAGE_UPLOADS_DIR / safe_name
    
    with open(destination_path, "w", encoding="utf-8") as f:
        f.write(ITS_DOCUMENT_TEXT)
        
    ext_result = extract_from_txt(destination_path)
    
    doc = Document(
        id=doc_id,
        title="ITS Comprehensive Lecture Notes (Units 1-4) [Sample Notes]",
        subject_id="ITS-401",
        unit_number=1,
        original_filename="its_401_sample_lecture_notes.pdf",
        safe_filename=safe_name,
        file_type="pdf",
        file_size=len(ITS_DOCUMENT_TEXT.encode("utf-8")),
        extraction_status="completed",
        error_message=None,
        detected_headings=ext_result.get("headings", []),
        is_demo_seed=True
    )
    db.add(doc)
    db.flush()
    
    doc_content = DocumentContent(
        document_id=doc.id,
        full_text=ITS_DOCUMENT_TEXT,
        page_count=6,
        cleaned_text=ITS_DOCUMENT_TEXT,
        topics_json=ext_result.get("topics", [])
    )
    db.add(doc_content)
    db.commit()
    db.refresh(doc)
    return doc

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    subject_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Returns uploaded documents with optional search and subject filtering."""
    query = db.query(Document)
    if subject_id:
        query = query.filter(Document.subject_id == subject_id)
    if search:
        query = query.filter(Document.title.ilike(f"%{search}%"))
    return query.order_by(Document.created_at.desc()).all()

@router.get("/{id}", response_model=DocumentResponse)
def get_document(id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc

@router.get("/{id}/content", response_model=DocumentContentResponse)
def get_document_content(id: str, db: Session = Depends(get_db)):
    content = db.query(DocumentContent).filter(DocumentContent.document_id == id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Document content not found.")
    return content

@router.patch("/{id}", response_model=DocumentResponse)
def update_document(
    id: str,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if payload.title is not None:
        doc.title = payload.title
    if payload.subject_id is not None:
        doc.subject_id = payload.subject_id
    if payload.unit_number is not None:
        doc.unit_number = payload.unit_number
    db.commit()
    db.refresh(doc)
    return doc

@router.delete("/{id}")
def delete_document(
    id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    # Delete uploaded physical file if it exists
    file_path = settings.STORAGE_UPLOADS_DIR / doc.safe_filename
    if file_path.exists() and not doc.is_demo_seed:
        try:
            os.remove(file_path)
        except Exception:
            pass
            
    db.delete(doc)
    db.commit()
    return {"success": True, "message": "Document deleted successfully."}
