import uuid
import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import (
    GenerationJob, GeneratedQuestion, Document, DocumentContent,
    Question, QuestionRevision, SourceEvidence, DemoUser
)
from app.schemas.generation import (
    GenerationRequest, GenerationJobResponse, GeneratedQuestionResponse,
    GeneratedQuestionUpdate
)
from app.services.gemini_service import (
    generate_questions_with_gemini,
    generate_sample_demo_questions,
    verify_grounding
)
from app.api.deps import require_faculty

router = APIRouter(prefix="/generations", tags=["Question Generation"])

@router.post("", response_model=Dict[str, Any])
def create_generation_job(
    request: GenerationRequest,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """
    Triggers source-grounded question generation via Google GenAI SDK.
    """
    doc = db.query(Document).filter(Document.id == request.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Source document not found.")
        
    content = db.query(DocumentContent).filter(DocumentContent.document_id == doc.id).first()
    if not content or not content.full_text.strip():
        raise HTTPException(status_code=400, detail="Document contains no extracted text for question generation.")
        
    job_id = f"gen_{uuid.uuid4().hex[:12]}"
    job = GenerationJob(
        id=job_id,
        subject_id=request.subject_id or doc.subject_id,
        document_id=doc.id,
        prompt_summary=f"Types: {request.question_types}, Diff: {request.difficulty}, Count: {request.requested_count}",
        question_types=request.question_types,
        difficulty=request.difficulty,
        requested_count=request.requested_count,
        marks_per_question=request.marks_per_question or 2.0,
        status="in_progress"
    )
    db.add(job)
    db.commit()
    
    # Run Gemini generation or Offline Demo generation
    if request.use_offline_demo:
        gen_result = generate_sample_demo_questions(
            request=request,
            source_text=content.full_text,
            document_title=doc.title
        )
    else:
        gen_result = generate_questions_with_gemini(
            request=request,
            source_text=content.full_text,
            document_title=doc.title
        )
    
    if not gen_result["success"]:
        job.status = "failed"
        job.error_message = gen_result["message"]
        db.commit()
        return {
            "success": False,
            "job_id": job.id,
            "error_type": gen_result.get("error_type", "GENERATION_FAILED"),
            "message": gen_result["message"],
            "generated_count": 0
        }
        
    # Persist generated questions
    created_questions = []
    for q_data in gen_result["questions"]:
        gq = GeneratedQuestion(
            id=q_data["id"],
            generation_job_id=job.id,
            document_id=doc.id,
            question_text=q_data["question_text"],
            question_type=q_data["question_type"],
            options_json=q_data["options_json"],
            correct_answer=q_data["correct_answer"],
            model_answer=q_data["model_answer"],
            rubric_json=q_data["rubric_json"],
            explanation=q_data["explanation"],
            difficulty=q_data["difficulty"],
            marks=q_data["marks"],
            topic_name=q_data["topic_name"],
            unit_number=q_data["unit_number"],
            supporting_excerpt=q_data["supporting_excerpt"],
            page_number=q_data["page_number"],
            confidence_flag=q_data["confidence_flag"],
            review_status="draft"
        )
        db.add(gq)
        created_questions.append(gq)
        
    job.status = "completed"
    job.completed_at = datetime.datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "job_id": job.id,
        "message": f"Successfully generated {len(created_questions)} questions from '{doc.title}'.",
        "generated_count": len(created_questions)
    }

@router.get("/{id}", response_model=GenerationJobResponse)
def get_generation_job(id: str, db: Session = Depends(get_db)):
    job = db.query(GenerationJob).filter(GenerationJob.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found.")
    return job

@router.patch("/questions/{question_id}", response_model=GeneratedQuestionResponse)
def update_generated_question(
    question_id: str,
    payload: GeneratedQuestionUpdate,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    gq = db.query(GeneratedQuestion).filter(GeneratedQuestion.id == question_id).first()
    if not gq:
        raise HTTPException(status_code=404, detail="Generated question not found.")
        
    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(gq, field, val)
        
    # Re-verify grounding if excerpt changed
    if payload.supporting_excerpt is not None:
        doc_content = db.query(DocumentContent).filter(DocumentContent.document_id == gq.document_id).first()
        if doc_content:
            flag, _ = verify_grounding(payload.supporting_excerpt, doc_content.full_text)
            gq.confidence_flag = flag
            
    db.commit()
    db.refresh(gq)
    return gq

@router.delete("/questions/{question_id}")
def delete_generated_question(
    question_id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """Discards a draft generated question."""
    gq = db.query(GeneratedQuestion).filter(GeneratedQuestion.id == question_id).first()
    if not gq:
        raise HTTPException(status_code=404, detail="Generated question not found.")
    db.delete(gq)
    db.commit()
    return {"success": True, "message": "Draft question discarded."}

@router.post("/questions/{question_id}/duplicate", response_model=GeneratedQuestionResponse)
def duplicate_generated_question(
    question_id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """Duplicates a generated question in the review workspace."""
    gq = db.query(GeneratedQuestion).filter(GeneratedQuestion.id == question_id).first()
    if not gq:
        raise HTTPException(status_code=404, detail="Generated question not found.")
        
    new_id = f"gq_copy_{uuid.uuid4().hex[:8]}"
    new_gq = GeneratedQuestion(
        id=new_id,
        generation_job_id=gq.generation_job_id,
        document_id=gq.document_id,
        question_text=f"{gq.question_text} (Copy)",
        question_type=gq.question_type,
        options_json=list(gq.options_json) if gq.options_json else None,
        correct_answer=gq.correct_answer,
        model_answer=gq.model_answer,
        rubric_json=list(gq.rubric_json) if gq.rubric_json else None,
        explanation=gq.explanation,
        difficulty=gq.difficulty,
        marks=gq.marks,
        topic_name=gq.topic_name,
        unit_number=gq.unit_number,
        supporting_excerpt=gq.supporting_excerpt,
        page_number=gq.page_number,
        confidence_flag=gq.confidence_flag,
        review_status="draft"
    )
    db.add(new_gq)
    db.commit()
    db.refresh(new_gq)
    return new_gq

@router.post("/questions/{question_id}/regenerate", response_model=GeneratedQuestionResponse)
def regenerate_single_question(
    question_id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """Regenerates a single question with fresh AI generation."""
    gq = db.query(GeneratedQuestion).filter(GeneratedQuestion.id == question_id).first()
    if not gq:
        raise HTTPException(status_code=404, detail="Generated question not found.")
        
    doc = db.query(Document).filter(Document.id == gq.document_id).first()
    content = db.query(DocumentContent).filter(DocumentContent.document_id == gq.document_id).first() if doc else None
    
    if content and doc:
        req = GenerationRequest(
            document_id=doc.id,
            question_types=[gq.question_type],
            difficulty=gq.difficulty,
            requested_count=1,
            marks_per_question=gq.marks
        )
        gen_result = generate_questions_with_gemini(req, content.full_text, doc.title)
        if not gen_result["success"]:
            gen_result = generate_sample_demo_questions(req, content.full_text, doc.title)
            
        if gen_result["success"] and gen_result["questions"]:
            q_data = gen_result["questions"][0]
            gq.question_text = q_data["question_text"]
            gq.options_json = q_data["options_json"]
            gq.correct_answer = q_data["correct_answer"]
            gq.model_answer = q_data["model_answer"]
            gq.rubric_json = q_data["rubric_json"]
            gq.explanation = q_data["explanation"]
            gq.supporting_excerpt = q_data["supporting_excerpt"]
            gq.confidence_flag = q_data["confidence_flag"]
            db.commit()
            db.refresh(gq)
            
    return gq

@router.post("/questions/{question_id}/approve")
def approve_generated_question(
    question_id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """
    Approves a generated question into the central question bank as Revision 1.
    """
    gq = db.query(GeneratedQuestion).filter(GeneratedQuestion.id == question_id).first()
    if not gq:
        raise HTTPException(status_code=404, detail="Generated question not found.")
        
    if gq.review_status == "approved" and gq.approved_question_id:
        return {"success": True, "question_id": gq.approved_question_id, "message": "Already approved."}
        
    # Create Question and Revision
    central_q_id = f"q_{uuid.uuid4().hex[:12]}"
    rev_id = f"{central_q_id}_v1"
    
    question = Question(
        id=central_q_id,
        subject_id="ITS-401", # Default or from job
        current_revision_id=rev_id,
        status="approved",
        is_active=True,
        is_demo_seed=False
    )
    db.add(question)
    db.flush()
    
    doc = db.query(Document).filter(Document.id == gq.document_id).first()
    
    rev = QuestionRevision(
        id=rev_id,
        question_id=central_q_id,
        revision_number=1,
        question_text=gq.question_text,
        question_type=gq.question_type,
        options_json=gq.options_json,
        correct_answer=gq.correct_answer,
        model_answer=gq.model_answer,
        rubric_json=gq.rubric_json,
        explanation=gq.explanation,
        difficulty=gq.difficulty,
        marks=gq.marks,
        topic_name=gq.topic_name,
        unit_number=gq.unit_number,
        source_document_id=gq.document_id,
        source_document_title=doc.title if doc else None,
        supporting_excerpt=gq.supporting_excerpt,
        page_number=gq.page_number,
        verified_grounding=(gq.confidence_flag == "grounded"),
        approved_by=user.id,
        approved_at=datetime.datetime.utcnow(),
        is_current=True
    )
    db.add(rev)
    db.flush()
    
    if gq.supporting_excerpt:
        ev = SourceEvidence(
            revision_id=rev.id,
            document_id=gq.document_id,
            document_title=doc.title if doc else None,
            excerpt=gq.supporting_excerpt,
            page_number=gq.page_number,
            match_confidence=1.0 if gq.confidence_flag == "grounded" else 0.5,
            verified_grounding=(gq.confidence_flag == "grounded")
        )
        db.add(ev)
        
    gq.review_status = "approved"
    gq.approved_question_id = central_q_id
    db.commit()
    
    return {
        "success": True,
        "question_id": central_q_id,
        "revision_id": rev_id,
        "message": "Question approved and added to Question Bank."
    }

@router.post("/batch-approve")
def batch_approve_questions(
    question_ids: List[str] = Body(..., embed=True),
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """Batch approves a list of generated questions."""
    approved_count = 0
    for q_id in question_ids:
        gq = db.query(GeneratedQuestion).filter(GeneratedQuestion.id == q_id).first()
        if gq and gq.review_status != "approved":
            central_q_id = f"q_{uuid.uuid4().hex[:12]}"
            rev_id = f"{central_q_id}_v1"
            
            question = Question(
                id=central_q_id,
                subject_id="ITS-401",
                current_revision_id=rev_id,
                status="approved",
                is_active=True,
                is_demo_seed=False
            )
            db.add(question)
            db.flush()
            
            doc = db.query(Document).filter(Document.id == gq.document_id).first()
            rev = QuestionRevision(
                id=rev_id,
                question_id=central_q_id,
                revision_number=1,
                question_text=gq.question_text,
                question_type=gq.question_type,
                options_json=gq.options_json,
                correct_answer=gq.correct_answer,
                model_answer=gq.model_answer,
                rubric_json=gq.rubric_json,
                explanation=gq.explanation,
                difficulty=gq.difficulty,
                marks=gq.marks,
                topic_name=gq.topic_name,
                unit_number=gq.unit_number,
                source_document_id=gq.document_id,
                source_document_title=doc.title if doc else None,
                supporting_excerpt=gq.supporting_excerpt,
                page_number=gq.page_number,
                verified_grounding=(gq.confidence_flag == "grounded"),
                approved_by=user.id,
                approved_at=datetime.datetime.utcnow(),
                is_current=True
            )
            db.add(rev)
            
            if gq.supporting_excerpt:
                ev = SourceEvidence(
                    revision_id=rev.id,
                    document_id=gq.document_id,
                    document_title=doc.title if doc else None,
                    excerpt=gq.supporting_excerpt,
                    verified_grounding=(gq.confidence_flag == "grounded")
                )
                db.add(ev)
                
            gq.review_status = "approved"
            gq.approved_question_id = central_q_id
            approved_count += 1
            
    db.commit()
    return {"success": True, "approved_count": approved_count}
