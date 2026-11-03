import uuid
import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Paper, PaperSection, PaperItem, QuestionRevision, Question, DemoUser
from app.schemas.paper import (
    PaperResponse, PaperDetailResponse, PaperCreate, PaperUpdate,
    PaperAssembleRequest, ValidationResult, BlueprintRule
)
from app.services.paper_service import validate_paper_integrity, assemble_paper_automatically
from app.services.pdf_export import generate_question_paper_pdf, generate_answer_key_pdf
from app.api.deps import require_faculty

router = APIRouter(prefix="/papers", tags=["Paper Builder & Library"])

@router.get("", response_model=List[PaperResponse])
def list_papers(
    status: Optional[str] = Query(None),
    subject_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Paper)
    if status:
        query = query.filter(Paper.status == status)
    if subject_id:
        query = query.filter(Paper.subject_id == subject_id)
        
    papers = query.order_by(Paper.created_at.desc()).all()
    results = []
    for p in papers:
        resp = PaperResponse.model_validate(p)
        resp.question_count = len(p.items) if p.items else 0
        results.append(resp)
    return results

@router.post("", response_model=PaperResponse)
def create_paper(
    payload: PaperCreate,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    paper_id = f"paper_{uuid.uuid4().hex[:10]}"
    paper = Paper(
        id=paper_id,
        title=payload.title,
        subject_id=payload.subject_id or "ITS-401",
        status="draft",
        duration_minutes=payload.duration_minutes,
        total_marks=payload.total_marks,
        instructions=payload.instructions or "1. All questions are compulsory.\n2. Figures to the right indicate full marks.",
        blueprint_json=payload.blueprint_json or {
            "target_marks": payload.total_marks,
            "duration_minutes": payload.duration_minutes,
            "difficulty_target": {"easy": 30, "medium": 50, "hard": 20},
            "type_target": {"mcq": 5, "short_answer": 4, "long_answer": 2}
        },
        warnings_acknowledged=False,
        window_start=payload.window_start,
        window_end=payload.window_end,
        is_demo_seed=False
    )
    db.add(paper)
    db.flush()
    
    # Create default sections
    sec_a = PaperSection(
        id=f"sec_{uuid.uuid4().hex[:10]}",
        paper_id=paper.id,
        name="Section A: Multiple Choice Questions",
        description="Select the best alternative.",
        section_order=1,
        total_marks=10.0
    )
    sec_b = PaperSection(
        id=f"sec_{uuid.uuid4().hex[:10]}",
        paper_id=paper.id,
        name="Section B: Short Answer Questions",
        description="Concise technical explanations.",
        section_order=2,
        total_marks=20.0
    )
    sec_c = PaperSection(
        id=f"sec_{uuid.uuid4().hex[:10]}",
        paper_id=paper.id,
        name="Section C: Long Answer / Design Problems",
        description="Comprehensive system design questions.",
        section_order=3,
        total_marks=20.0
    )
    db.add_all([sec_a, sec_b, sec_c])
    db.commit()
    db.refresh(paper)
    
    resp = PaperResponse.model_validate(paper)
    resp.question_count = 0
    return resp

@router.get("/{id}")
def get_paper(id: str, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
        
    sections_data = []
    for sec in paper.sections:
        items_data = []
        for it in sec.items:
            rev = db.query(QuestionRevision).filter(QuestionRevision.id == it.question_revision_id).first()
            items_data.append({
                "id": it.id,
                "paper_id": it.paper_id,
                "section_id": it.section_id,
                "question_revision_id": it.question_revision_id,
                "item_order": it.item_order,
                "marks": it.marks,
                "revision": rev
            })
        sections_data.append({
            "id": sec.id,
            "paper_id": sec.paper_id,
            "name": sec.name,
            "description": sec.description,
            "section_order": sec.section_order,
            "total_marks": sec.total_marks,
            "instructions": sec.instructions,
            "items": items_data
        })
        
    # All items
    all_items = []
    for it in paper.items:
        rev = db.query(QuestionRevision).filter(QuestionRevision.id == it.question_revision_id).first()
        all_items.append({
            "id": it.id,
            "paper_id": it.paper_id,
            "section_id": it.section_id,
            "question_revision_id": it.question_revision_id,
            "item_order": it.item_order,
            "marks": it.marks,
            "revision": rev
        })
        
    return {
        "id": paper.id,
        "title": paper.title,
        "subject_id": paper.subject_id,
        "status": paper.status,
        "duration_minutes": paper.duration_minutes,
        "total_marks": paper.total_marks,
        "instructions": paper.instructions,
        "blueprint_json": paper.blueprint_json,
        "validation_results_json": paper.validation_results_json,
        "warnings_acknowledged": paper.warnings_acknowledged,
        "window_start": paper.window_start,
        "window_end": paper.window_end,
        "is_demo_seed": paper.is_demo_seed,
        "published_at": paper.published_at,
        "created_at": paper.created_at,
        "updated_at": paper.updated_at,
        "sections": sections_data,
        "items": all_items
    }

@router.patch("/{id}")
def update_paper(
    id: str,
    payload: PaperUpdate,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    paper = db.query(Paper).filter(Paper.id == id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
        
    if payload.title is not None:
        paper.title = payload.title
    if payload.duration_minutes is not None:
        paper.duration_minutes = payload.duration_minutes
    if payload.total_marks is not None:
        paper.total_marks = payload.total_marks
    if payload.instructions is not None:
        paper.instructions = payload.instructions
    if payload.blueprint_json is not None:
        paper.blueprint_json = payload.blueprint_json
    if payload.warnings_acknowledged is not None:
        paper.warnings_acknowledged = payload.warnings_acknowledged
    if payload.window_start is not None:
        paper.window_start = payload.window_start
    if payload.window_end is not None:
        paper.window_end = payload.window_end
        
    # If sections & items layout updated
    if payload.sections is not None:
        # Clear existing items and sections
        for it in paper.items:
            db.delete(it)
        for s in paper.sections:
            db.delete(s)
        db.flush()
        
        global_order = 1
        for s_idx, sec_input in enumerate(payload.sections):
            sec_id = sec_input.get("id") or f"sec_{uuid.uuid4().hex[:10]}"
            sec = PaperSection(
                id=sec_id,
                paper_id=paper.id,
                name=sec_input.get("name", f"Section {s_idx+1}"),
                description=sec_input.get("description"),
                section_order=s_idx + 1,
                total_marks=float(sec_input.get("total_marks", 0.0)),
                instructions=sec_input.get("instructions")
            )
            db.add(sec)
            db.flush()
            
            for item_input in sec_input.get("items", []):
                rev_id = item_input.get("question_revision_id")
                marks = float(item_input.get("marks", 2.0))
                item_id = item_input.get("id") or f"pi_{uuid.uuid4().hex[:10]}"
                pi = PaperItem(
                    id=item_id,
                    paper_id=paper.id,
                    section_id=sec.id,
                    question_revision_id=rev_id,
                    item_order=global_order,
                    marks=marks
                )
                db.add(pi)
                global_order += 1
                
    db.commit()
    db.refresh(paper)
    return {"success": True, "message": "Paper layout updated successfully."}

@router.post("/{id}/assemble")
def assemble_paper(
    id: str,
    payload: PaperAssembleRequest,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    paper = db.query(Paper).filter(Paper.id == id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
        
    assemble_paper_automatically(paper, payload.blueprint, db)
    validation = validate_paper_integrity(paper, db)
    paper.validation_results_json = validation.model_dump()
    db.commit()
    
    return {
        "success": True,
        "message": "Paper assembled automatically from eligible approved questions.",
        "validation": validation
    }

@router.post("/{id}/validate", response_model=ValidationResult)
def validate_paper(
    id: str,
    db: Session = Depends(get_db)
):
    paper = db.query(Paper).filter(Paper.id == id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
        
    validation = validate_paper_integrity(paper, db)
    paper.validation_results_json = validation.model_dump()
    db.commit()
    return validation

@router.post("/{id}/publish")
def publish_paper(
    id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """
    Formally publishes examination paper after strict integrity checks.
    """
    paper = db.query(Paper).filter(Paper.id == id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
        
    validation = validate_paper_integrity(paper, db)
    if not validation.can_publish:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot publish paper due to validation errors: {'; '.join(validation.errors)}"
        )
        
    if validation.warnings and not paper.warnings_acknowledged:
        raise HTTPException(
            status_code=400,
            detail=f"Paper has unacknowledged blueprint warnings: {'; '.join(validation.warnings)}. Please acknowledge before publishing."
        )
        
    paper.status = "published"
    paper.published_at = datetime.datetime.utcnow()
    paper.validation_results_json = validation.model_dump()
    db.commit()
    
    return {"success": True, "message": "Paper formally published as official examination."}

@router.post("/{id}/make-practice")
def make_paper_practice(
    id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    paper = db.query(Paper).filter(Paper.id == id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    paper.status = "practice"
    db.commit()
    return {"success": True, "message": "Paper marked available for Student Practice."}

@router.get("/{id}/export")
def export_question_paper(
    id: str,
    db: Session = Depends(get_db)
):
    """
    Exports official examination question paper PDF (without answers).
    """
    paper = db.query(Paper).filter(Paper.id == id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
        
    # Build data dict
    paper_dict = {
        "id": paper.id,
        "title": paper.title,
        "subject_id": paper.subject_id,
        "duration_minutes": paper.duration_minutes,
        "total_marks": paper.total_marks,
        "instructions": paper.instructions
    }
    
    sections_list = []
    for s in paper.sections:
        items = []
        for it in s.items:
            rev = db.query(QuestionRevision).filter(QuestionRevision.id == it.question_revision_id).first()
            items.append({
                "item_order": it.item_order,
                "marks": it.marks,
                "revision": {
                    "question_text": rev.question_text if rev else "",
                    "question_type": rev.question_type if rev else "short_answer",
                    "options_json": rev.options_json if rev else [],
                    "marks": it.marks
                }
            })
        sections_list.append({
            "name": s.name,
            "total_marks": s.total_marks,
            "instructions": s.instructions,
            "items": items
        })
        
    pdf_path = generate_question_paper_pdf(paper_dict, sections_list)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"Question_Paper_{paper.title.replace(' ', '_')}.pdf"
    )

@router.get("/{id}/answer-key")
def export_answer_key(
    id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty) # CRITICAL: Faculty only!
):
    """
    Exports confidential faculty answer key and scoring rubric PDF.
    """
    paper = db.query(Paper).filter(Paper.id == id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
        
    paper_dict = {
        "id": paper.id,
        "title": paper.title,
        "subject_id": paper.subject_id,
        "duration_minutes": paper.duration_minutes,
        "total_marks": paper.total_marks,
    }
    
    sections_list = []
    for s in paper.sections:
        items = []
        for it in s.items:
            rev = db.query(QuestionRevision).filter(QuestionRevision.id == it.question_revision_id).first()
            items.append({
                "item_order": it.item_order,
                "marks": it.marks,
                "revision": {
                    "question_text": rev.question_text if rev else "",
                    "question_type": rev.question_type if rev else "short_answer",
                    "options_json": rev.options_json if rev else [],
                    "correct_answer": rev.correct_answer if rev else "",
                    "model_answer": rev.model_answer if rev else "",
                    "rubric_json": rev.rubric_json if rev else [],
                    "explanation": rev.explanation if rev else "",
                    "supporting_excerpt": rev.supporting_excerpt if rev else "",
                    "marks": it.marks
                }
            })
        sections_list.append({
            "name": s.name,
            "items": items
        })
        
    pdf_path = generate_answer_key_pdf(paper_dict, sections_list)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"Answer_Key_{paper.title.replace(' ', '_')}.pdf"
    )
