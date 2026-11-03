from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.db.session import get_db
from app.db.models import (
    Document, Question, QuestionRevision, Paper, Attempt,
    Response, AttemptItem, DemoUser
)
from app.schemas.analytics import (
    FacultyAnalyticsResponse, StudentAnalyticsResponse,
    ScoreBucket, TopicAccuracyStat, PerformanceTrendPoint
)
from app.api.deps import get_current_user_and_role, require_faculty

router = APIRouter(prefix="/analytics", tags=["Analytics & Insights"])

@router.get("/faculty", response_model=FacultyAnalyticsResponse)
def get_faculty_analytics(
    db: Session = Depends(get_db),
    user: DemoUser = Depends(require_faculty)
):
    total_docs = db.query(Document).count()
    total_q = db.query(Question).count()
    app_q = db.query(Question).filter(Question.status == "approved").count()
    pend_q = db.query(Question).filter(Question.status == "draft").count()
    total_p = db.query(Paper).count()
    pub_p = db.query(Paper).filter(Paper.status == "published").count()
    total_att = db.query(Attempt).count()
    
    # Grading workload: pending descriptive responses
    pending_responses = (
        db.query(Response)
        .filter(Response.grading_status == "pending")
        .count()
    )
    
    # Question composition
    revisions = db.query(QuestionRevision).filter(QuestionRevision.is_current == True).all()
    q_types: Dict[str, int] = {}
    q_diffs: Dict[str, int] = {}
    q_topics: Dict[str, int] = {}
    
    for r in revisions:
        t = r.question_type or "short_answer"
        q_types[t] = q_types.get(t, 0) + 1
        
        d = r.difficulty or "medium"
        q_diffs[d] = q_diffs.get(d, 0) + 1
        
        tp = r.topic_name or "General Topic"
        q_topics[tp] = q_topics.get(tp, 0) + 1
        
    # Score distribution of graded attempts
    completed_attempts = db.query(Attempt).filter(Attempt.status.in_(["graded", "partially_graded"])).all()
    buckets = {
        "0 - 40%": 0,
        "41 - 60%": 0,
        "61 - 80%": 0,
        "81 - 100%": 0
    }
    
    for att in completed_attempts:
        score = att.final_score if att.final_score is not None else att.provisional_score
        if score is not None and att.total_possible_marks > 0:
            pct = (score / att.total_possible_marks) * 100
            if pct <= 40:
                buckets["0 - 40%"] += 1
            elif pct <= 60:
                buckets["41 - 60%"] += 1
            elif pct <= 80:
                buckets["61 - 80%"] += 1
            else:
                buckets["81 - 100%"] += 1
                
    score_dist = [ScoreBucket(range_label=k, count=v) for k, v in buckets.items()]
    
    # Topic accuracies across all students
    all_responses = db.query(Response).all()
    topic_map: Dict[str, Dict[str, int]] = {}
    for r in all_responses:
        item = db.query(AttemptItem).filter(
            AttemptItem.attempt_id == r.attempt_id,
            AttemptItem.question_revision_id == r.question_revision_id
        ).first()
        if item:
            t_name = item.question_snapshot_json.get("topic_name") or "General"
            if t_name not in topic_map:
                topic_map[t_name] = {"total": 0, "correct": 0}
            topic_map[t_name]["total"] += 1
            if r.is_correct or (r.marks_awarded and r.marks_awarded >= (item.marks_allocated * 0.5)):
                topic_map[t_name]["correct"] += 1
                
    topic_accs = []
    for t_k, t_v in topic_map.items():
        pct = (t_v["correct"] / t_v["total"] * 100) if t_v["total"] > 0 else 0
        topic_accs.append(TopicAccuracyStat(
            topic_name=t_k,
            total_questions=t_v["total"],
            correct_count=t_v["correct"],
            accuracy_percentage=round(pct, 1),
            is_weak_area=(t_v["total"] >= 5 and pct < 60),
            evidence_count=t_v["total"],
            rule_note="Topic performance aggregated across all student attempts."
        ))
        
    return FacultyAnalyticsResponse(
        total_documents=total_docs,
        total_questions=total_q,
        approved_questions=app_q,
        pending_questions=pend_q,
        total_papers=total_p,
        published_papers=pub_p,
        total_attempts=total_att,
        pending_grading_count=pending_responses,
        questions_by_type=q_types,
        questions_by_difficulty=q_diffs,
        questions_by_topic=q_topics,
        score_distribution=score_dist,
        topic_accuracies=topic_accs,
        is_demo_data=True
    )

@router.get("/student", response_model=StudentAnalyticsResponse)
def get_student_analytics(
    db: Session = Depends(get_db),
    user: DemoUser = Depends(get_current_user_and_role)
):
    attempts = (
        db.query(Attempt)
        .filter(Attempt.student_id == user.id)
        .order_by(Attempt.started_at.asc())
        .all()
    )
    
    trends = []
    total_score_pct = 0.0
    graded_count = 0
    
    for a in attempts:
        score = a.final_score if a.final_score is not None else a.provisional_score
        pct = (score / a.total_possible_marks * 100) if score is not None and a.total_possible_marks > 0 else 0.0
        if a.status in ["graded", "partially_graded"]:
            total_score_pct += pct
            graded_count += 1
            
        trends.append(PerformanceTrendPoint(
            attempt_id=a.id,
            title=a.title,
            date=a.started_at.strftime("%b %d"),
            score_percentage=round(pct, 1),
            status=a.status
        ))
        
    avg_score = round(total_score_pct / graded_count, 1) if graded_count > 0 else 0.0
    
    # Topic accuracies for this student
    student_responses = (
        db.query(Response)
        .join(Attempt, Response.attempt_id == Attempt.id)
        .filter(Attempt.student_id == user.id)
        .all()
    )
    
    topic_map: Dict[str, Dict[str, int]] = {}
    for r in student_responses:
        item = db.query(AttemptItem).filter(
            AttemptItem.attempt_id == r.attempt_id,
            AttemptItem.question_revision_id == r.question_revision_id
        ).first()
        if item:
            t_name = item.question_snapshot_json.get("topic_name") or "General"
            if t_name not in topic_map:
                topic_map[t_name] = {"total": 0, "correct": 0}
            topic_map[t_name]["total"] += 1
            if r.is_correct or (r.marks_awarded and r.marks_awarded >= (item.marks_allocated * 0.5)):
                topic_map[t_name]["correct"] += 1
                
    topic_accs = []
    recommended = []
    
    for t_k, t_v in topic_map.items():
        pct = (t_v["correct"] / t_v["total"] * 100) if t_v["total"] > 0 else 0
        # RULE: Recommend topics below 60% accuracy only after at least 5 answered questions
        is_weak = (t_v["total"] >= 5 and pct < 60)
        if is_weak:
            recommended.append(t_k)
            
        rule_msg = "Sufficient confidence."
        if t_v["total"] < 5:
            rule_msg = f"Insufficient sample size ({t_v['total']}/5 questions answered to determine weak area rule)."
        elif is_weak:
            rule_msg = "Weak area flagged: Accuracy < 60% with >= 5 questions attempted."
            
        topic_accs.append(TopicAccuracyStat(
            topic_name=t_k,
            total_questions=t_v["total"],
            correct_count=t_v["correct"],
            accuracy_percentage=round(pct, 1),
            is_weak_area=is_weak,
            evidence_count=t_v["total"],
            rule_note=rule_msg
        ))
        
    rationale = (
        "Recommendations require at least 5 questions answered per topic to avoid spurious conclusions. "
        "Topics under 60% accuracy with >= 5 questions are prioritized for review."
    )
    
    return StudentAnalyticsResponse(
        student_id=user.id,
        student_name=user.name,
        total_attempts=len(attempts),
        completed_attempts=graded_count,
        average_score_percentage=avg_score,
        trends=trends,
        topic_accuracies=topic_accs,
        recommended_topics=recommended,
        recommendation_rationale=rationale,
        is_demo_data=True
    )
