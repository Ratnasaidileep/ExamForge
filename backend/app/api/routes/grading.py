import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Attempt, Response, AttemptItem, DemoUser
from app.schemas.grading import (
    GradingQueueItemResponse, GradingAttemptDetailResponse,
    DescriptiveResponseToGrade, GradeResponseRequest, FinalizeGradingRequest
)
from app.services.grading_service import update_response_grade, finalize_attempt_grading
from app.api.deps import require_faculty

router = APIRouter(prefix="/grading", tags=["Faculty Grading Queue & Workspace"])

@router.get("/queue", response_model=List[GradingQueueItemResponse])
def get_grading_queue(
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """
    Displays submitted student attempts containing descriptive answers awaiting evaluation.
    """
    attempts = (
        db.query(Attempt)
        .filter(Attempt.status.in_(["awaiting_grading", "partially_graded", "submitted"]))
        .order_by(Attempt.submitted_at.asc())
        .all()
    )
    
    queue = []
    for att in attempts:
        student = db.query(DemoUser).filter(DemoUser.id == att.student_id).first()
        
        # Count pending vs graded descriptive responses
        total_descriptive = 0
        pending_count = 0
        graded_count = 0
        
        for r in att.responses:
            item = db.query(AttemptItem).filter(
                AttemptItem.attempt_id == att.id,
                AttemptItem.question_revision_id == r.question_revision_id
            ).first()
            if item and item.question_snapshot_json.get("question_type") != "mcq":
                total_descriptive += 1
                if r.grading_status == "pending":
                    pending_count += 1
                elif r.grading_status == "manually_graded":
                    graded_count += 1
                    
        queue.append(GradingQueueItemResponse(
            attempt_id=att.id,
            student_id=att.student_id,
            student_name=student.name if student else "Student",
            title=att.title,
            submitted_at=att.submitted_at or att.started_at,
            pending_count=pending_count,
            graded_count=graded_count,
            total_descriptive=total_descriptive,
            objective_score=att.objective_score,
            total_possible_marks=att.total_possible_marks,
            status=att.status
        ))
        
    return queue

@router.get("/attempts/{id}", response_model=GradingAttemptDetailResponse)
def get_attempt_grading_workspace(
    id: str,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """
    Returns grading workspace for an attempt:
    Includes student answer, model answer, rubric, marks allocator.
    """
    attempt = db.query(Attempt).filter(Attempt.id == id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found.")
        
    student = db.query(DemoUser).filter(DemoUser.id == attempt.student_id).first()
    
    descriptive_list: List[DescriptiveResponseToGrade] = []
    all_graded = True
    
    for it in attempt.items:
        snap = it.question_snapshot_json
        q_type = snap.get("question_type", "short_answer")
        if q_type == "mcq":
            continue
            
        resp = db.query(Response).filter(
            Response.attempt_id == attempt.id,
            Response.question_revision_id == it.question_revision_id
        ).first()
        
        status = resp.grading_status if resp else "pending"
        if status == "pending":
            all_graded = False
            
        descriptive_list.append(DescriptiveResponseToGrade(
            response_id=resp.id if resp else "",
            question_revision_id=it.question_revision_id,
            question_text=snap.get("question_text", ""),
            question_type=q_type,
            marks_allocated=it.marks_allocated,
            submitted_answer=resp.submitted_answer if resp else "",
            model_answer=snap.get("model_answer"),
            rubric_json=snap.get("rubric_json"),
            marks_awarded=resp.marks_awarded if resp else None,
            grading_status=status,
            faculty_feedback=resp.faculty_feedback if resp else None,
            graded_at=resp.graded_at if resp else None
        ))
        
    return GradingAttemptDetailResponse(
        attempt_id=attempt.id,
        student_id=attempt.student_id,
        student_name=student.name if student else "Student",
        student_email=student.email if student else "student@college.edu",
        title=attempt.title,
        status=attempt.status,
        submitted_at=attempt.submitted_at or attempt.started_at,
        objective_score=attempt.objective_score,
        provisional_score=attempt.provisional_score,
        final_score=attempt.final_score,
        total_possible_marks=attempt.total_possible_marks,
        responses_to_grade=descriptive_list,
        can_finalize=all_graded and (len(descriptive_list) > 0)
    )

@router.patch("/responses/{response_id}")
def grade_descriptive_response(
    response_id: str,
    payload: GradeResponseRequest,
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """
    Awards marks and feedback for a student's descriptive response.
    Enforces that awarded marks are between 0 and maximum possible marks.
    """
    resp = db.query(Response).filter(Response.id == response_id).first()
    if not resp:
        raise HTTPException(status_code=404, detail="Response record not found.")
        
    update_response_grade(
        response=resp,
        marks_awarded=payload.marks_awarded,
        feedback=payload.faculty_feedback or "",
        grader_id=user.id,
        db=db
    )
    
    return {
        "success": True,
        "message": f"Awarded {payload.marks_awarded} marks.",
        "response_id": resp.id,
        "attempt_status": resp.attempt.status,
        "provisional_score": resp.attempt.provisional_score
    }

@router.post("/attempts/{id}/finalize")
def finalize_grading(
    id: str,
    payload: FinalizeGradingRequest = Body(default=FinalizeGradingRequest()),
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """
    Finalizes attempt grading:
    Blocks finalization if any required descriptive response is still pending.
    """
    attempt = db.query(Attempt).filter(Attempt.id == id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found.")
        
    finalize_attempt_grading(attempt, db)
    
    return {
        "success": True,
        "message": "Attempt grading finalized successfully. Results released to student.",
        "final_score": attempt.final_score,
        "status": attempt.status
    }
