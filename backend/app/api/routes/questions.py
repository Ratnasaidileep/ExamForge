import uuid
import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Question, QuestionRevision, SourceEvidence, Document, DemoUser
from app.schemas.question import (
    QuestionResponse, QuestionRevisionResponse, QuestionCreate,
    QuestionUpdate, QuestionApproveRequest
)
from app.schemas.common import PaginatedResponse
from app.api.deps import require_faculty

router = APIRouter(prefix="/questions", tags=["Central Question Bank"])

@router.get("")
def list_questions(
    subject_id: Optional[str] = Query(None),
    question_type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    unit_number: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Searchable, paginated question bank with multidimensional filtering.
    """
    query = db.query(Question).filter(Question.is_active == True)
    
    if subject_id:
        query = query.filter(Question.subject_id == subject_id)
    if status:
        query = query.filter(Question.status == status)
        
    all_questions = query.order_by(Question.created_at.desc()).all()
    
    # In-memory filter on current revision properties
    filtered = []
    for q in all_questions:
        curr_rev = db.query(QuestionRevision).filter(QuestionRevision.id == q.current_revision_id).first()
        if not curr_rev:
            continue
            
        if question_type and curr_rev.question_type != question_type:
            continue
        if difficulty and curr_rev.difficulty != difficulty:
            continue
        if unit_number and curr_rev.unit_number != unit_number:
            continue
        if search:
            s_lower = search.lower()
            if s_lower not in curr_rev.question_text.lower() and (not curr_rev.topic_name or s_lower not in curr_rev.topic_name.lower()):
                continue
                
        # Format response
        filtered.append({
            "id": q.id,
            "subject_id": q.subject_id,
            "current_revision_id": q.current_revision_id,
            "status": q.status,
            "is_active": q.is_active,
            "is_demo_seed": q.is_demo_seed,
            "current_revision": {
                "id": curr_rev.id,
                "question_id": curr_rev.question_id,
                "revision_number": curr_rev.revision_number,
                "question_text": curr_rev.question_text,
                "question_type": curr_rev.question_type,
                "options_json": curr_rev.options_json,
                "correct_answer": curr_rev.correct_answer,
                "model_answer": curr_rev.model_answer,
                "rubric_json": curr_rev.rubric_json,
                "explanation": curr_rev.explanation,
                "difficulty": curr_rev.difficulty,
                "marks": curr_rev.marks,
                "topic_name": curr_rev.topic_name,
                "unit_number": curr_rev.unit_number,
                "source_document_title": curr_rev.source_document_title,
                "supporting_excerpt": curr_rev.supporting_excerpt,
                "verified_grounding": curr_rev.verified_grounding,
                "approved_by": curr_rev.approved_by,
                "approved_at": curr_rev.approved_at.isoformat() if curr_rev.approved_at else None,
                "is_current": curr_rev.is_current,
                "created_at": curr_rev.created_at.isoformat()
            },
            "created_at": q.created_at.isoformat(),
            "updated_at": q.updated_at.isoformat()
        })
        
    total = len(filtered)
    start = (page - 1) * page_size
    items = filtered[start:start + page_size]
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size)
    }

@router.get("/{id}")
def get_question_detail(id: str, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")
        
    revs = (
        db.query(QuestionRevision)
        .filter(QuestionRevision.question_id == q.id)
        .order_by(QuestionRevision.revision_number.desc())
        .all()
    )
    
    curr_rev = next((r for r in revs if r.id == q.current_revision_id), revs[0] if revs else None)
    
    return {
        "id": q.id,
        "subject_id": q.subject_id,
        "current_revision_id": q.current_revision_id,
        "status": q.status,
        "is_active": q.is_active,
        "is_demo_seed": q.is_demo_seed,
        "current_revision": curr_rev,
        "revisions": revs,
        "created_at": q.created_at,
        "updated_at": q.updated_at
    }

@router.post("")
def create_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """Creates a new question manually with revision 1."""
    q_id = f"q_{uuid.uuid4().hex[:12]}"
    rev_id = f"{q_id}_v1"
    
    q = Question(
        id=q_id,
        subject_id=payload.subject_id or "ITS-401",
        current_revision_id=rev_id,
        status=payload.status,
        is_active=True,
        is_demo_seed=False
    )
    db.add(q)
    db.flush()
    
    rev = QuestionRevision(
        id=rev_id,
        question_id=q_id,
        revision_number=1,
        question_text=payload.question_text,
        question_type=payload.question_type,
        options_json=payload.options_json,
        correct_answer=payload.correct_answer,
        model_answer=payload.model_answer,
        rubric_json=payload.rubric_json,
        explanation=payload.explanation,
        difficulty=payload.difficulty,
        marks=payload.marks,
        topic_id=payload.topic_id,
        topic_name=payload.topic_name,
        unit_number=payload.unit_number,
        source_document_id=payload.source_document_id,
        source_document_title=payload.source_document_title,
        supporting_excerpt=payload.supporting_excerpt,
        page_number=payload.page_number,
        verified_grounding=True,
        approved_by=user.id if payload.status == "approved" else None,
        approved_at=datetime.datetime.utcnow() if payload.status == "approved" else None,
        is_current=True
    )
    db.add(rev)
    db.commit()
    return {"success": True, "question_id": q.id, "revision_id": rev.id}

@router.patch("/{id}")
def update_question(
    id: str,
    payload: QuestionUpdate,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """
    Edits a question by creating a NEW immutable revision.
    If the question was previously approved, marks status as 'draft' requiring re-approval.
    """
    q = db.query(Question).filter(Question.id == id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")
        
    curr_rev = db.query(QuestionRevision).filter(QuestionRevision.id == q.current_revision_id).first()
    if not curr_rev:
        raise HTTPException(status_code=500, detail="Missing current question revision.")
        
    # Mark old revision as not current
    curr_rev.is_current = False
    
    new_rev_number = curr_rev.revision_number + 1
    new_rev_id = f"{q.id}_v{new_rev_number}"
    
    # Inherit existing values unless updated
    new_rev = QuestionRevision(
        id=new_rev_id,
        question_id=q.id,
        revision_number=new_rev_number,
        question_text=payload.question_text if payload.question_text is not None else curr_rev.question_text,
        question_type=payload.question_type if payload.question_type is not None else curr_rev.question_type,
        options_json=payload.options_json if payload.options_json is not None else curr_rev.options_json,
        correct_answer=payload.correct_answer if payload.correct_answer is not None else curr_rev.correct_answer,
        model_answer=payload.model_answer if payload.model_answer is not None else curr_rev.model_answer,
        rubric_json=payload.rubric_json if payload.rubric_json is not None else curr_rev.rubric_json,
        explanation=payload.explanation if payload.explanation is not None else curr_rev.explanation,
        difficulty=payload.difficulty if payload.difficulty is not None else curr_rev.difficulty,
        marks=payload.marks if payload.marks is not None else curr_rev.marks,
        topic_id=curr_rev.topic_id,
        topic_name=payload.topic_name if payload.topic_name is not None else curr_rev.topic_name,
        unit_number=payload.unit_number if payload.unit_number is not None else curr_rev.unit_number,
        source_document_id=curr_rev.source_document_id,
        source_document_title=curr_rev.source_document_title,
        supporting_excerpt=payload.supporting_excerpt if payload.supporting_excerpt is not None else curr_rev.supporting_excerpt,
        page_number=curr_rev.page_number,
        verified_grounding=curr_rev.verified_grounding,
        approved_by=None,
        approved_at=None,
        is_current=True
    )
    db.add(new_rev)
    db.flush()
    
    q.current_revision_id = new_rev.id
    if payload.requires_reapproval:
        q.status = "draft" # Requires re-approval
        
    db.commit()
    
    return {
        "success": True,
        "question_id": q.id,
        "new_revision_id": new_rev.id,
        "status": q.status,
        "message": f"Created Revision {new_rev_number}. Requires re-approval before inclusion in new published exams."
    }

@router.post("/{id}/approve")
def approve_question(
    id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """Explicitly approves the current revision of a question."""
    q = db.query(Question).filter(Question.id == id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")
        
    curr_rev = db.query(QuestionRevision).filter(QuestionRevision.id == q.current_revision_id).first()
    if not curr_rev:
        raise HTTPException(status_code=500, detail="Missing question revision.")
        
    curr_rev.approved_by = user.id
    curr_rev.approved_at = datetime.datetime.utcnow()
    q.status = "approved"
    
    db.commit()
    return {"success": True, "message": f"Question {q.id} (Revision {curr_rev.revision_number}) approved."}

@router.post("/{id}/archive")
def archive_question(
    id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """Archives a question from active question bank."""
    q = db.query(Question).filter(Question.id == id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")
    q.status = "archived"
    q.is_active = False
    db.commit()
    return {"success": True, "message": "Question archived."}

@router.post("/{id}/duplicate")
def duplicate_question(
    id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """Duplicates an existing question into a new draft question with revision 1."""
    q = db.query(Question).filter(Question.id == id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")
        
    curr_rev = db.query(QuestionRevision).filter(QuestionRevision.id == q.current_revision_id).first()
    if not curr_rev:
        raise HTTPException(status_code=500, detail="Missing question revision.")
        
    new_q_id = f"q_{uuid.uuid4().hex[:12]}"
    new_rev_id = f"{new_q_id}_v1"
    
    new_q = Question(
        id=new_q_id,
        subject_id=q.subject_id,
        current_revision_id=new_rev_id,
        status="draft",
        is_active=True,
        is_demo_seed=False
    )
    db.add(new_q)
    db.flush()
    
    new_rev = QuestionRevision(
        id=new_rev_id,
        question_id=new_q_id,
        revision_number=1,
        question_text=f"{curr_rev.question_text} (Copy)",
        question_type=curr_rev.question_type,
        options_json=list(curr_rev.options_json) if curr_rev.options_json else None,
        correct_answer=curr_rev.correct_answer,
        model_answer=curr_rev.model_answer,
        rubric_json=list(curr_rev.rubric_json) if curr_rev.rubric_json else None,
        explanation=curr_rev.explanation,
        difficulty=curr_rev.difficulty,
        marks=curr_rev.marks,
        topic_id=curr_rev.topic_id,
        topic_name=curr_rev.topic_name,
        unit_number=curr_rev.unit_number,
        source_document_id=curr_rev.source_document_id,
        source_document_title=curr_rev.source_document_title,
        supporting_excerpt=curr_rev.supporting_excerpt,
        page_number=curr_rev.page_number,
        verified_grounding=curr_rev.verified_grounding,
        approved_by=None,
        approved_at=None,
        is_current=True
    )
    db.add(new_rev)
    db.commit()
    return {"success": True, "question_id": new_q.id, "revision_id": new_rev.id, "message": "Question duplicated as draft."}
