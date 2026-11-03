from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.session import get_db
from app.db.models import DemoUser, Document, Question, Paper, Attempt, Response, AuditEvent, Notification
from app.schemas.user import DemoUserResponse, DemoSwitchRequest
from app.services.seed_service import reset_demo_workspace
from app.api.deps import get_current_user_and_role, require_faculty

router = APIRouter(prefix="/demo", tags=["Demo & System"])

@router.get("/profiles", response_model=List[DemoUserResponse])
def get_demo_profiles(db: Session = Depends(get_db)):
    """Returns available demo user profiles (faculty & student)."""
    users = db.query(DemoUser).all()
    return users

@router.post("/switch")
def switch_demo_role(
    payload: DemoSwitchRequest,
    db: Session = Depends(get_db)
):
    """Switches active demo user/role without resetting the database."""
    user = db.query(DemoUser).filter(DemoUser.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Demo profile not found.")
    return {
        "success": True,
        "message": f"Switched to {user.name} ({user.role})",
        "user": {
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "email": user.email,
            "department": user.department,
            "avatar_url": user.avatar_url
        }
    }

@router.post("/reset")
def reset_workspace(
    confirm: bool = Body(False, embed=True),
    db: Session = Depends(get_db)
):
    """
    Resets the demo workspace to clean initial seed data upon explicit confirmation.
    """
    if not confirm:
        raise HTTPException(status_code=400, detail="Explicit confirmation (confirm: true) is required to reset the demo workspace.")
    
    reset_demo_workspace(db)
    return {
        "success": True,
        "message": "Demo workspace successfully restored to initial seeded state."
    }

# Dashboard routes
dash_router = APIRouter(prefix="/dashboard", tags=["Dashboards"])

@dash_router.get("/faculty")
def get_faculty_dashboard(
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    """Returns real database-backed faculty metrics."""
    doc_count = db.query(Document).count()
    total_questions = db.query(Question).count()
    pending_questions = db.query(Question).filter(Question.status == "draft").count()
    approved_questions = db.query(Question).filter(Question.status == "approved").count()
    
    draft_papers = db.query(Paper).filter(Paper.status == "draft").count()
    published_papers = db.query(Paper).filter(Paper.status == "published").count()
    
    total_attempts = db.query(Attempt).count()
    pending_grading_attempts = db.query(Attempt).filter(Attempt.status.in_(["awaiting_grading", "partially_graded"])).count()
    
    # Recent activity
    recent_attempts = (
        db.query(Attempt)
        .order_by(Attempt.started_at.desc())
        .limit(5)
        .all()
    )
    
    activity = []
    for att in recent_attempts:
        student = db.query(DemoUser).filter(DemoUser.id == att.student_id).first()
        activity.append({
            "id": att.id,
            "title": att.title,
            "student_name": student.name if student else "Student",
            "status": att.status,
            "submitted_at": att.submitted_at.isoformat() if att.submitted_at else None,
            "score": att.final_score if att.final_score is not None else att.provisional_score,
            "max_score": att.total_possible_marks
        })
        
    return {
        "metrics": {
            "uploaded_documents": doc_count,
            "total_questions": total_questions,
            "questions_awaiting_review": pending_questions,
            "approved_questions": approved_questions,
            "draft_papers": draft_papers,
            "published_papers": published_papers,
            "student_assessment_attempts": total_attempts,
            "pending_grading_count": pending_grading_attempts
        },
        "recent_activity": activity,
        "is_demo_seed": True
    }

@dash_router.get("/student")
def get_student_dashboard(
    db: Session = Depends(get_db),
    user: DemoUser = Depends(get_current_user_and_role)
):
    """Returns real database-backed student metrics for active student."""
    # Available papers
    available_assessments = (
        db.query(Paper)
        .filter(Paper.status.in_(["published", "practice"]))
        .all()
    )
    
    assessments_list = []
    for p in available_assessments:
        q_count = len(p.items) if p.items else 0
        assessments_list.append({
            "id": p.id,
            "title": p.title,
            "subject_id": p.subject_id,
            "duration_minutes": p.duration_minutes,
            "total_marks": p.total_marks,
            "question_count": q_count,
            "status": p.status
        })
        
    # Student attempts
    student_attempts = (
        db.query(Attempt)
        .filter(Attempt.student_id == user.id)
        .order_by(Attempt.started_at.desc())
        .all()
    )
    
    attempts_list = []
    for att in student_attempts:
        attempts_list.append({
            "id": att.id,
            "title": att.title,
            "status": att.status,
            "started_at": att.started_at.isoformat() if att.started_at else None,
            "submitted_at": att.submitted_at.isoformat() if att.submitted_at else None,
            "objective_score": att.objective_score,
            "provisional_score": att.provisional_score,
            "final_score": att.final_score,
            "total_possible_marks": att.total_possible_marks
        })
        
    # Topic accuracies
    # Query student's responses
    student_responses = (
        db.query(Response)
        .join(Attempt, Response.attempt_id == Attempt.id)
        .filter(Attempt.student_id == user.id)
        .all()
    )
    
    topic_stats: Dict[str, Dict[str, Any]] = {}
    for r in student_responses:
        # Find item snapshot
        item = db.query(AttemptItem).filter(
            AttemptItem.attempt_id == r.attempt_id,
            AttemptItem.question_revision_id == r.question_revision_id
        ).first()
        if item:
            t_name = item.question_snapshot_json.get("topic_name") or "General"
            if t_name not in topic_stats:
                topic_stats[t_name] = {"total": 0, "correct": 0}
            topic_stats[t_name]["total"] += 1
            if r.is_correct:
                topic_stats[t_name]["correct"] += 1
                
    topic_accuracies = []
    recommended_topics = []
    for t_name, s in topic_stats.items():
        acc = (s["correct"] / s["total"] * 100) if s["total"] > 0 else 0
        # Rule: Recommend topics below 60% accuracy only after at least 5 answered questions
        is_weak = (s["total"] >= 5 and acc < 60)
        if is_weak:
            recommended_topics.append(t_name)
        topic_accuracies.append({
            "topic_name": t_name,
            "total_questions": s["total"],
            "correct_count": s["correct"],
            "accuracy_percentage": round(acc, 1),
            "is_weak_area": is_weak,
            "evidence_count": s["total"],
            "rule_note": "Identified as weak topic (accuracy < 60% with >= 5 questions answered)" if is_weak else "Sufficient proficiency"
        })
        
    return {
        "available_assessments": assessments_list,
        "recent_attempts": attempts_list,
        "topic_accuracies": topic_accuracies,
        "recommended_topics": recommended_topics,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }
