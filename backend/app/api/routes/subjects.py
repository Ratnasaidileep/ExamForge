from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models import Subject, Topic, DemoUser
from app.schemas.subject import SubjectResponse, TopicResponse
from app.api.deps import require_faculty

router = APIRouter(prefix="/subjects", tags=["Subjects & Curriculum"])

@router.get("", response_model=List[SubjectResponse])
def list_subjects(db: Session = Depends(get_db)):
    """
    Returns all preloaded subjects and their curriculum topics.
    """
    subjects = db.query(Subject).order_by(Subject.code).all()
    return subjects

@router.get("/{id_or_code}", response_model=SubjectResponse)
def get_subject(id_or_code: str, db: Session = Depends(get_db)):
    """
    Returns detailed curriculum topics for a specific subject by ID or Code.
    """
    subject = (
        db.query(Subject)
        .filter((Subject.id == id_or_code) | (Subject.code == id_or_code))
        .first()
    )
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found.")
    return subject
