import uuid
import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import (
    Attempt, AttemptItem, Response, Paper, PaperItem,
    QuestionRevision, DemoUser
)
from app.schemas.attempt import (
    AttemptCreate, ActiveAttemptResponse, ActiveAttemptQuestionResponse,
    SavedResponseItem, ResponseSaveRequest, AttemptSubmissionResponse,
    AttemptResultResponse, QuestionReviewItem
)
from app.services.grading_service import grade_attempt_submission
from app.api.deps import get_current_user_and_role

router = APIRouter(prefix="/attempts", tags=["Student Assessments & Attempts"])

@router.post("", response_model=Dict[str, Any])
def start_attempt(
    payload: AttemptCreate,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(get_current_user_and_role)
):
    """
    Starts an assessment or practice attempt and creates immutable question snapshots.
    """
    paper = db.query(Paper).filter(Paper.id == payload.paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
        
    if paper.status not in ["published", "practice"]:
        raise HTTPException(status_code=400, detail="This paper is in draft status and not open for assessment.")
        
    now = datetime.datetime.utcnow()
    deadline = now + datetime.timedelta(minutes=paper.duration_minutes) if paper.duration_minutes else None
    
    attempt_id = f"att_{uuid.uuid4().hex[:12]}"
    attempt = Attempt(
        id=attempt_id,
        student_id=user.id,
        paper_id=paper.id,
        title=paper.title,
        subject_id=paper.subject_id,
        mode=payload.mode,
        status="in_progress",
        started_at=now,
        deadline_at=deadline,
        total_possible_marks=paper.total_marks,
        is_demo_seed=False
    )
    db.add(attempt)
    db.flush()
    
    # Create immutable snapshots of paper items
    paper_items = db.query(PaperItem).filter(PaperItem.paper_id == paper.id).order_by(PaperItem.item_order).all()
    if not paper_items:
        raise HTTPException(status_code=400, detail="Cannot take an assessment with no questions.")
        
    for item in paper_items:
        rev = db.query(QuestionRevision).filter(QuestionRevision.id == item.question_revision_id).first()
        if not rev:
            continue
            
        snapshot = {
            "question_revision_id": rev.id,
            "question_text": rev.question_text,
            "question_type": rev.question_type,
            "options": rev.options_json,
            "marks": item.marks,
            "difficulty": rev.difficulty,
            "topic_name": rev.topic_name,
            "unit_number": rev.unit_number,
            "correct_answer": rev.correct_answer,
            "model_answer": rev.model_answer,
            "rubric_json": rev.rubric_json,
            "explanation": rev.explanation
        }
        
        att_item = AttemptItem(
            attempt_id=attempt.id,
            question_revision_id=rev.id,
            order_index=item.item_order,
            marks_allocated=item.marks,
            question_snapshot_json=snapshot
        )
        db.add(att_item)
        
        # Pre-seed empty response
        resp = Response(
            id=f"resp_{uuid.uuid4().hex[:12]}",
            attempt_id=attempt.id,
            question_revision_id=rev.id,
            submitted_answer="",
            is_marked_for_review=False,
            grading_status="pending"
        )
        db.add(resp)
        
    db.commit()
    db.refresh(attempt)
    
    return {
        "attempt_id": attempt.id,
        "title": attempt.title,
        "status": attempt.status,
        "duration_minutes": paper.duration_minutes,
        "deadline_at": attempt.deadline_at.isoformat() if attempt.deadline_at else None
    }

@router.get("/{id}", response_model=ActiveAttemptResponse)
def get_active_attempt(
    id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(get_current_user_and_role)
):
    """
    Retrieves active attempt interface.
    CRITICAL SECURITY RULE: Active-attempt APIs must NEVER return correct answers or model answers!
    """
    attempt = db.query(Attempt).filter(Attempt.id == id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found.")
        
    now = datetime.datetime.utcnow()
    remaining = None
    if attempt.deadline_at:
        remaining = max(0, int((attempt.deadline_at - now).total_seconds()))
        
    # Build sanitized questions list
    sanitized_questions: List[ActiveAttemptQuestionResponse] = []
    for it in attempt.items:
        snap = it.question_snapshot_json
        sanitized_questions.append(ActiveAttemptQuestionResponse(
            question_revision_id=it.question_revision_id,
            order_index=it.order_index,
            question_text=snap.get("question_text", ""),
            question_type=snap.get("question_type", "short_answer"),
            options=snap.get("options"), # Options list for MCQ
            marks_allocated=it.marks_allocated,
            difficulty=snap.get("difficulty"),
            topic_name=snap.get("topic_name"),
            unit_number=snap.get("unit_number")
            # ABSOLUTELY NO correct_answer or model_answer or rubric!
        ))
        
    # Saved responses
    saved_resps: Dict[str, SavedResponseItem] = {}
    for r in attempt.responses:
        saved_resps[r.question_revision_id] = SavedResponseItem(
            question_revision_id=r.question_revision_id,
            submitted_answer=r.submitted_answer,
            is_marked_for_review=r.is_marked_for_review
        )
        
    return ActiveAttemptResponse(
        id=attempt.id,
        student_id=attempt.student_id,
        paper_id=attempt.paper_id,
        question_set_id=attempt.question_set_id,
        title=attempt.title,
        subject_id=attempt.subject_id,
        mode=attempt.mode,
        status=attempt.status,
        started_at=attempt.started_at,
        deadline_at=attempt.deadline_at,
        remaining_seconds=remaining,
        total_questions=len(sanitized_questions),
        total_possible_marks=attempt.total_possible_marks,
        questions=sanitized_questions,
        saved_responses=saved_resps
    )

@router.put("/{id}/responses/{question_revision_id}")
def save_response(
    id: str,
    question_revision_id: str,
    payload: ResponseSaveRequest,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(get_current_user_and_role)
):
    """
    Saves or updates a student's answer as they navigate.
    Enforces server-side deadline.
    """
    attempt = db.query(Attempt).filter(Attempt.id == id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found.")
        
    if attempt.status != "in_progress":
        raise HTTPException(status_code=400, detail="Cannot save answer: Assessment has already been submitted.")
        
    # Deadline enforcement on server
    if attempt.deadline_at and datetime.datetime.utcnow() > (attempt.deadline_at + datetime.timedelta(seconds=15)):
        attempt.status = "expired"
        db.commit()
        raise HTTPException(status_code=400, detail="Assessment time has expired.")
        
    resp = db.query(Response).filter(
        Response.attempt_id == attempt.id,
        Response.question_revision_id == question_revision_id
    ).first()
    
    if not resp:
        resp = Response(
            id=f"resp_{uuid.uuid4().hex[:12]}",
            attempt_id=attempt.id,
            question_revision_id=question_revision_id
        )
        db.add(resp)
        
    if payload.submitted_answer is not None:
        resp.submitted_answer = payload.submitted_answer
    if payload.is_marked_for_review is not None:
        resp.is_marked_for_review = payload.is_marked_for_review
        
    resp.updated_at = datetime.datetime.utcnow()
    db.commit()
    
    return {"success": True, "saved_at": resp.updated_at.isoformat()}

@router.post("/{id}/submit", response_model=AttemptSubmissionResponse)
def submit_attempt(
    id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(get_current_user_and_role)
):
    """
    Submits student assessment:
    - Auto-grades MCQs.
    - Routes descriptive answers to faculty grading queue.
    - Idempotent: multiple submissions return existing submission state.
    """
    attempt = db.query(Attempt).filter(Attempt.id == id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found.")
        
    # Idempotent check
    if attempt.status in ["submitted", "awaiting_grading", "partially_graded", "graded"]:
        pending = sum(1 for r in attempt.responses if r.grading_status == "pending")
        return AttemptSubmissionResponse(
            attempt_id=attempt.id,
            status=attempt.status,
            submitted_at=attempt.submitted_at or attempt.started_at,
            objective_score=attempt.objective_score,
            provisional_score=attempt.provisional_score,
            final_score=attempt.final_score,
            total_possible_marks=attempt.total_possible_marks,
            requires_manual_grading=(pending > 0),
            pending_descriptive_count=pending,
            message="Attempt was already submitted."
        )
        
    result = grade_attempt_submission(attempt, db)
    return AttemptSubmissionResponse(**result)

@router.get("/{id}/results", response_model=AttemptResultResponse)
def get_attempt_results(
    id: str,
    db: Session = Depends(get_db)
):
    """
    Displays assessment results AFTER submission:
    - Objective score (auto-graded MCQs)
    - Provisional score
    - Final score (only if fully graded)
    - Question-by-question review with model answers & explanations
    """
    attempt = db.query(Attempt).filter(Attempt.id == id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found.")
        
    if attempt.status == "in_progress":
        raise HTTPException(status_code=400, detail="Assessment results are not available until the test is submitted.")
        
    correct_count = 0
    incorrect_count = 0
    pending_count = 0
    
    questions_review: List[QuestionReviewItem] = []
    topic_summary: Dict[str, Dict[str, Any]] = {}
    
    for it in attempt.items:
        snap = it.question_snapshot_json
        resp = db.query(Response).filter(
            Response.attempt_id == attempt.id,
            Response.question_revision_id == it.question_revision_id
        ).first()
        
        q_type = snap.get("question_type", "short_answer")
        t_name = snap.get("topic_name") or "General"
        
        if t_name not in topic_summary:
            topic_summary[t_name] = {"total_marks": 0.0, "earned_marks": 0.0, "total_q": 0}
        topic_summary[t_name]["total_marks"] += it.marks_allocated
        topic_summary[t_name]["total_q"] += 1
        
        marks_aw = resp.marks_awarded if resp else None
        is_corr = resp.is_correct if resp else None
        status = resp.grading_status if resp else "pending"
        
        if status == "auto_graded":
            if is_corr:
                correct_count += 1
                topic_summary[t_name]["earned_marks"] += (marks_aw or 0.0)
            else:
                incorrect_count += 1
        elif status == "manually_graded":
            if marks_aw is not None:
                topic_summary[t_name]["earned_marks"] += marks_aw
                if marks_aw >= (it.marks_allocated * 0.5):
                    correct_count += 1
                else:
                    incorrect_count += 1
        elif status == "pending":
            pending_count += 1
            
        questions_review.append(QuestionReviewItem(
            question_revision_id=it.question_revision_id,
            order_index=it.order_index,
            question_text=snap.get("question_text", ""),
            question_type=q_type,
            options=snap.get("options"),
            submitted_answer=resp.submitted_answer if resp else "",
            correct_answer=snap.get("correct_answer"),
            model_answer=snap.get("model_answer"),
            rubric_json=snap.get("rubric_json"),
            explanation=snap.get("explanation"),
            marks_allocated=it.marks_allocated,
            marks_awarded=marks_aw, # Remains null if pending!
            grading_status=status,
            is_correct=is_corr,
            faculty_feedback=resp.faculty_feedback if resp else None,
            topic_name=t_name,
            unit_number=snap.get("unit_number")
        ))
        
    topic_perf = []
    for t_k, t_v in topic_summary.items():
        pct = (t_v["earned_marks"] / t_v["total_marks"] * 100) if t_v["total_marks"] > 0 else 0
        topic_perf.append({
            "topic_name": t_k,
            "total_marks": t_v["total_marks"],
            "earned_marks": t_v["earned_marks"],
            "accuracy_percentage": round(pct, 1),
            "questions_count": t_v["total_q"]
        })
        
    return AttemptResultResponse(
        id=attempt.id,
        student_id=attempt.student_id,
        title=attempt.title,
        mode=attempt.mode,
        status=attempt.status,
        started_at=attempt.started_at,
        submitted_at=attempt.submitted_at,
        total_possible_marks=attempt.total_possible_marks,
        objective_score=attempt.objective_score,
        provisional_score=attempt.provisional_score,
        final_score=attempt.final_score,
        is_fully_graded=(attempt.status == "graded"),
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        pending_grading_count=pending_count,
        topic_performance=topic_perf,
        questions=questions_review
    )
