import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models import Attempt, Response, AttemptItem, QuestionRevision, Notification

def grade_attempt_submission(attempt: Attempt, db: Session) -> Dict[str, Any]:
    """
    Grades an attempt upon student submission:
    - Automatically grades all MCQs.
    - Leaves short and long descriptive answers as pending with null marks.
    - Calculates objective and provisional scores.
    """
    now = datetime.datetime.utcnow()
    attempt.submitted_at = now
    
    total_descriptive_pending = 0
    objective_score = 0.0
    
    for resp in attempt.responses:
        # Find item snapshot
        item = db.query(AttemptItem).filter(
            AttemptItem.attempt_id == attempt.id,
            AttemptItem.question_revision_id == resp.question_revision_id
        ).first()
        
        snapshot = item.question_snapshot_json if item else {}
        q_type = snapshot.get("question_type", "short_answer")
        max_marks = float(snapshot.get("marks", item.marks_allocated if item else 2.0))
        
        if q_type == "mcq":
            correct_ans = str(snapshot.get("correct_answer", "")).strip().lower()
            submitted = str(resp.submitted_answer or "").strip().lower()
            
            # Match either exact text, or single letter prefix
            is_match = False
            if submitted and correct_ans:
                if submitted == correct_ans:
                    is_match = True
                elif len(submitted) == 1 and correct_ans.startswith(submitted):
                    is_match = True
                elif len(correct_ans) == 1 and submitted.startswith(correct_ans):
                    is_match = True
                elif submitted in correct_ans or correct_ans in submitted:
                    is_match = True
                    
            resp.is_correct = is_match
            resp.marks_awarded = max_marks if is_match else 0.0
            resp.grading_status = "auto_graded"
            resp.graded_at = now
            if is_match:
                objective_score += max_marks
        else:
            # Descriptive answer
            resp.is_correct = None
            resp.marks_awarded = None # Keep null!
            resp.grading_status = "pending"
            total_descriptive_pending += 1
            
    attempt.objective_score = objective_score
    attempt.provisional_score = objective_score
    
    if total_descriptive_pending > 0:
        attempt.status = "awaiting_grading"
        attempt.final_score = None
        
        # Add faculty notification
        notif = Notification(
            role="faculty",
            title="New Submission Awaiting Grading",
            message=f"Student submitted '{attempt.title}' with {total_descriptive_pending} descriptive questions awaiting evaluation.",
            link=f"/faculty/grading/{attempt.id}"
        )
        db.add(notif)
    else:
        attempt.status = "graded"
        attempt.final_score = objective_score
        attempt.graded_at = now
        
        # Add student notification
        notif = Notification(
            user_id=attempt.student_id,
            role="student",
            title="Assessment Graded",
            message=f"Your assessment '{attempt.title}' has been scored: {objective_score:g} / {attempt.total_possible_marks:g}.",
            link=f"/student/attempt/{attempt.id}/results"
        )
        db.add(notif)
        
    db.commit()
    db.refresh(attempt)
    
    return {
        "attempt_id": attempt.id,
        "status": attempt.status,
        "submitted_at": attempt.submitted_at or now,
        "objective_score": attempt.objective_score,
        "provisional_score": attempt.provisional_score,
        "final_score": attempt.final_score,
        "total_possible_marks": attempt.total_possible_marks,
        "requires_manual_grading": total_descriptive_pending > 0,
        "pending_descriptive_count": total_descriptive_pending,
        "message": "Submission recorded successfully."
    }

def update_response_grade(
    response: Response,
    marks_awarded: float,
    feedback: str,
    grader_id: str,
    db: Session
):
    """
    Updates the marks and feedback awarded by faculty for a single descriptive response.
    """
    # Fetch item to validate max marks
    item = db.query(AttemptItem).filter(
        AttemptItem.attempt_id == response.attempt_id,
        AttemptItem.question_revision_id == response.question_revision_id
    ).first()
    
    max_marks = item.marks_allocated if item else 10.0
    
    if marks_awarded < 0 or marks_awarded > max_marks:
        raise HTTPException(
            status_code=400,
            detail=f"Awarded marks ({marks_awarded}) must be between 0 and maximum marks ({max_marks:g})."
        )
        
    response.marks_awarded = marks_awarded
    response.faculty_feedback = feedback
    response.grader_id = grader_id
    response.grading_status = "manually_graded"
    response.graded_at = datetime.datetime.utcnow()
    
    # Recalculate provisional score for attempt
    attempt = response.attempt
    provisional = 0.0
    pending_count = 0
    for r in attempt.responses:
        if r.marks_awarded is not None:
            provisional += r.marks_awarded
        if r.grading_status == "pending":
            pending_count += 1
            
    attempt.provisional_score = provisional
    if pending_count > 0:
        attempt.status = "partially_graded"
        
    db.commit()

def finalize_attempt_grading(attempt: Attempt, db: Session):
    """
    Finalizes grading for an attempt once all descriptive answers have been graded.
    """
    for r in attempt.responses:
        if r.grading_status == "pending" or r.marks_awarded is None:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot finalize: One or more descriptive responses have not been graded yet."
            )
            
    final_score = sum(r.marks_awarded or 0.0 for r in attempt.responses)
    attempt.final_score = final_score
    attempt.provisional_score = final_score
    attempt.status = "graded"
    attempt.graded_at = datetime.datetime.utcnow()
    
    # Add notification for student
    notif = Notification(
        user_id=attempt.student_id,
        role="student",
        title="Grading Finalized",
        message=f"Faculty has finalized evaluation for '{attempt.title}'. Final score: {final_score:g} / {attempt.total_possible_marks:g}.",
        link=f"/student/attempt/{attempt.id}/results"
    )
    db.add(notif)
    db.commit()
