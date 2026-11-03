import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db.models import Paper, PaperSection, PaperItem, Question, QuestionRevision
from app.schemas.paper import BlueprintRule, ValidationResult

def validate_paper_integrity(paper: Paper, db: Session) -> ValidationResult:
    """
    Validates paper structure, blueprint conformance, and publication readiness.
    """
    errors: List[str] = []
    warnings: List[str] = []
    
    sections = paper.sections or []
    items = paper.items or []
    
    if not sections:
        errors.append("Paper has no sections defined. At least one section is required.")
    if not items:
        errors.append("Paper contains no questions. Add questions before publishing.")
        
    actual_marks = sum(item.marks for item in items)
    expected_marks = paper.total_marks or 50.0
    
    if abs(actual_marks - expected_marks) > 0.01:
        errors.append(f"Total marks mismatch: Allocated marks ({actual_marks:g}) do not match target marks ({expected_marks:g}).")
        
    diff_counts = {"easy": 0, "medium": 0, "hard": 0}
    type_counts = {"mcq": 0, "short_answer": 0, "long_answer": 0}
    topic_counts: Dict[str, int] = {}
    unit_counts: Dict[str, int] = {}
    
    for item in items:
        rev = db.query(QuestionRevision).filter(QuestionRevision.id == item.question_revision_id).first()
        if not rev:
            errors.append(f"Question item {item.id} references missing revision {item.question_revision_id}.")
            continue
            
        parent_q = db.query(Question).filter(Question.id == rev.question_id).first()
        if not parent_q or parent_q.status != "approved":
            errors.append(f"Question '{rev.question_text[:40]}...' is in draft/unapproved status. Only approved questions can be published.")
            
        diff = (rev.difficulty or "medium").lower()
        diff_counts[diff] = diff_counts.get(diff, 0) + 1
        
        q_type = (rev.question_type or "short_answer").lower()
        type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        if rev.topic_name:
            topic_counts[rev.topic_name] = topic_counts.get(rev.topic_name, 0) + 1
        if rev.unit_number:
            u_str = f"Unit {rev.unit_number}"
            unit_counts[u_str] = unit_counts.get(u_str, 0) + 1
            
    # Blueprint validation
    bp = paper.blueprint_json or {}
    if bp:
        diff_target = bp.get("difficulty_target") or {}
        if diff_target and len(items) > 0:
            for d_name, target_pct in diff_target.items():
                actual_pct = (diff_counts.get(d_name, 0) / len(items)) * 100
                if abs(actual_pct - float(target_pct)) > 20:
                    warnings.append(f"Difficulty target for '{d_name}' is {target_pct}%, actual is {actual_pct:.1f}%.")
                    
        type_target = bp.get("type_target") or {}
        if type_target:
            for t_name, target_count in type_target.items():
                actual_c = type_counts.get(t_name, 0)
                if actual_c < int(target_count):
                    warnings.append(f"Type target for '{t_name}' requested {target_count} questions, actual has {actual_c}.")
                    
        required_units = bp.get("required_units") or []
        for u in required_units:
            u_key = f"Unit {u}"
            if unit_counts.get(u_key, 0) == 0:
                warnings.append(f"Blueprint specifies coverage for Unit {u}, but no questions are included from it.")
                
    can_publish = (len(errors) == 0)
    is_valid = can_publish and (len(warnings) == 0 or paper.warnings_acknowledged)
    
    return ValidationResult(
        is_valid=is_valid,
        can_publish=can_publish,
        total_marks_expected=expected_marks,
        total_marks_actual=actual_marks,
        questions_count=len(items),
        difficulty_breakdown=diff_counts,
        type_breakdown=type_counts,
        topic_breakdown=topic_counts,
        unit_breakdown=unit_counts,
        warnings=warnings,
        errors=errors
    )

def assemble_paper_automatically(paper: Paper, blueprint: BlueprintRule, db: Session):
    """
    Selects approved questions deterministically from the question bank to satisfy blueprint rules.
    """
    # 1. Fetch available approved question revisions
    approved_questions = (
        db.query(Question)
        .filter(Question.subject_id == paper.subject_id, Question.status == "approved")
        .all()
    )
    
    eligible_revisions: List[QuestionRevision] = []
    for q in approved_questions:
        curr_rev = db.query(QuestionRevision).filter(QuestionRevision.id == q.current_revision_id).first()
        if curr_rev:
            eligible_revisions.append(curr_rev)
            
    # Clear existing sections and items
    for item in paper.items:
        db.delete(item)
    for sec in paper.sections:
        db.delete(sec)
    db.flush()
    
    # Organize revisions by question type
    mcqs = [r for r in eligible_revisions if r.question_type == "mcq"]
    shorts = [r for r in eligible_revisions if r.question_type == "short_answer"]
    longs = [r for r in eligible_revisions if r.question_type == "long_answer"]
    
    # Blueprint target counts
    type_target = blueprint.type_target or {"mcq": 5, "short_answer": 4, "long_answer": 2}
    
    sec_a = PaperSection(
        id=f"sec_{uuid.uuid4().hex[:10]}",
        paper_id=paper.id,
        name="Section A: Multiple Choice Questions",
        description="Answer all questions. Each question carries 2 marks.",
        section_order=1,
        total_marks=0.0,
        instructions="Choose the single best alternative for each question."
    )
    sec_b = PaperSection(
        id=f"sec_{uuid.uuid4().hex[:10]}",
        paper_id=paper.id,
        name="Section B: Short Answer Questions",
        description="Answer all questions with concise explanations.",
        section_order=2,
        total_marks=0.0,
        instructions="Answer briefly in 50-100 words."
    )
    sec_c = PaperSection(
        id=f"sec_{uuid.uuid4().hex[:10]}",
        paper_id=paper.id,
        name="Section C: Long Answer Questions",
        description="Detailed analytical and architectural questions.",
        section_order=3,
        total_marks=0.0,
        instructions="Answer in detail with system architectural diagrams."
    )
    
    db.add_all([sec_a, sec_b, sec_c])
    db.flush()
    
    item_order = 1
    selected_mcqs = mcqs[:type_target.get("mcq", 5)]
    sec_a_marks = 0.0
    for r in selected_mcqs:
        m = r.marks or 2.0
        pi = PaperItem(
            id=f"pi_{uuid.uuid4().hex[:10]}",
            paper_id=paper.id,
            section_id=sec_a.id,
            question_revision_id=r.id,
            item_order=item_order,
            marks=m
        )
        db.add(pi)
        sec_a_marks += m
        item_order += 1
    sec_a.total_marks = sec_a_marks
    
    selected_shorts = shorts[:type_target.get("short_answer", 4)]
    sec_b_marks = 0.0
    for r in selected_shorts:
        m = r.marks or 5.0
        pi = PaperItem(
            id=f"pi_{uuid.uuid4().hex[:10]}",
            paper_id=paper.id,
            section_id=sec_b.id,
            question_revision_id=r.id,
            item_order=item_order,
            marks=m
        )
        db.add(pi)
        sec_b_marks += m
        item_order += 1
    sec_b.total_marks = sec_b_marks
    
    selected_longs = longs[:type_target.get("long_answer", 2)]
    sec_c_marks = 0.0
    for r in selected_longs:
        m = r.marks or 10.0
        pi = PaperItem(
            id=f"pi_{uuid.uuid4().hex[:10]}",
            paper_id=paper.id,
            section_id=sec_c.id,
            question_revision_id=r.id,
            item_order=item_order,
            marks=m
        )
        db.add(pi)
        sec_c_marks += m
        item_order += 1
    sec_c.total_marks = sec_c_marks
    
    paper.total_marks = sec_a_marks + sec_b_marks + sec_c_marks
    paper.blueprint_json = blueprint.model_dump()
    db.commit()
