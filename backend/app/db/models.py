import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON, Index
)
from sqlalchemy.orm import relationship
from app.db.session import Base

class DemoUser(Base):
    __tablename__ = "demo_users"
    
    id = Column(String(50), primary_key=True) # e.g. 'prof_sharma', 'student_aditi'
    name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False) # 'faculty', 'student'
    email = Column(String(100), nullable=False)
    department = Column(String(100), default="Computer Science & Engineering")
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(String(50), primary_key=True) # e.g. 'ITS-401'
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="subject")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(String(50), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    unit_number = Column(Integer, nullable=False)
    unit_name = Column(String(150), nullable=False)
    topic_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    subject = relationship("Subject", back_populates="topics")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String(50), primary_key=True) # UUID or doc_xxx
    title = Column(String(200), nullable=False)
    subject_id = Column(String(50), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    unit_number = Column(Integer, nullable=True)
    original_filename = Column(String(255), nullable=False)
    safe_filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False) # 'pdf', 'docx'
    file_size = Column(Integer, nullable=False) # in bytes
    extraction_status = Column(String(50), default="pending") # 'pending', 'completed', 'failed', 'scanned_ocr_unsupported'
    error_message = Column(Text, nullable=True)
    detected_headings = Column(JSON, default=list) # List of extracted section titles/headings
    is_demo_seed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    subject = relationship("Subject", back_populates="documents")
    content = relationship("DocumentContent", back_populates="document", uselist=False, cascade="all, delete-orphan")

class DocumentContent(Base):
    __tablename__ = "document_contents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(50), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True)
    full_text = Column(Text, nullable=False)
    page_count = Column(Integer, default=1)
    cleaned_text = Column(Text, nullable=True)
    topics_json = Column(JSON, default=list) # Extracted key topics/keywords
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    document = relationship("Document", back_populates="content")

class GenerationJob(Base):
    __tablename__ = "generation_jobs"
    
    id = Column(String(50), primary_key=True)
    subject_id = Column(String(50), nullable=True)
    document_id = Column(String(50), nullable=True)
    prompt_summary = Column(Text, nullable=True)
    question_types = Column(JSON, default=list) # ['mcq', 'short_answer', 'long_answer']
    difficulty = Column(String(20), default="mixed") # 'easy', 'medium', 'hard', 'mixed'
    requested_count = Column(Integer, default=5)
    marks_per_question = Column(Float, default=2.0)
    blueprint_json = Column(JSON, nullable=True)
    status = Column(String(30), default="pending") # 'pending', 'in_progress', 'completed', 'failed'
    error_message = Column(Text, nullable=True)
    raw_ai_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    generated_questions = relationship("GeneratedQuestion", back_populates="job", cascade="all, delete-orphan")

class GeneratedQuestion(Base):
    __tablename__ = "generated_questions"
    
    id = Column(String(50), primary_key=True)
    generation_job_id = Column(String(50), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(50), nullable=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(30), nullable=False) # 'mcq', 'short_answer', 'long_answer'
    options_json = Column(JSON, nullable=True) # list of str for MCQs
    correct_answer = Column(Text, nullable=True) # For MCQs, exact option text or letter
    model_answer = Column(Text, nullable=True) # For short/long descriptive
    rubric_json = Column(JSON, nullable=True) # [{criteria: str, marks: float}]
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(20), default="medium") # 'easy', 'medium', 'hard'
    marks = Column(Float, default=2.0)
    topic_id = Column(Integer, nullable=True)
    topic_name = Column(String(200), nullable=True)
    unit_number = Column(Integer, nullable=True)
    supporting_excerpt = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=True)
    confidence_flag = Column(String(30), default="grounded") # 'grounded', 'partially_grounded', 'unsupported'
    review_status = Column(String(20), default="draft") # 'draft', 'approved', 'rejected'
    approved_question_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    job = relationship("GenerationJob", back_populates="generated_questions")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(String(50), primary_key=True) # Central question ID
    subject_id = Column(String(50), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    current_revision_id = Column(String(50), nullable=True) # FK to QuestionRevision
    status = Column(String(20), default="approved") # 'draft', 'approved', 'archived'
    is_active = Column(Boolean, default=True)
    is_demo_seed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    revisions = relationship("QuestionRevision", back_populates="question", cascade="all, delete-orphan", foreign_keys="QuestionRevision.question_id")

class QuestionRevision(Base):
    __tablename__ = "question_revisions"
    
    id = Column(String(50), primary_key=True) # Unique revision id: q_xxx_v1
    question_id = Column(String(50), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    revision_number = Column(Integer, default=1)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(30), nullable=False) # 'mcq', 'short_answer', 'long_answer'
    options_json = Column(JSON, nullable=True)
    correct_answer = Column(Text, nullable=True)
    model_answer = Column(Text, nullable=True)
    rubric_json = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(20), default="medium")
    marks = Column(Float, default=2.0)
    topic_id = Column(Integer, nullable=True)
    topic_name = Column(String(200), nullable=True)
    unit_number = Column(Integer, nullable=True)
    source_document_id = Column(String(50), nullable=True)
    source_document_title = Column(String(255), nullable=True)
    supporting_excerpt = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=True)
    verified_grounding = Column(Boolean, default=True)
    approved_by = Column(String(50), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    is_current = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    question = relationship("Question", back_populates="revisions", foreign_keys=[question_id])
    evidence = relationship("SourceEvidence", back_populates="revision", cascade="all, delete-orphan")

class SourceEvidence(Base):
    __tablename__ = "source_evidence"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    revision_id = Column(String(50), ForeignKey("question_revisions.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(50), nullable=True)
    document_title = Column(String(255), nullable=True)
    excerpt = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    match_confidence = Column(Float, default=1.0)
    verified_grounding = Column(Boolean, default=True)
    
    revision = relationship("QuestionRevision", back_populates="evidence")

class QuestionTopic(Base):
    __tablename__ = "question_topics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(String(50), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)

class QuestionSet(Base):
    __tablename__ = "question_sets"
    
    id = Column(String(50), primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    subject_id = Column(String(50), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    mode = Column(String(30), default="practice") # 'practice', 'mock_exam'
    duration_minutes = Column(Integer, default=30)
    total_marks = Column(Float, default=20.0)
    is_active = Column(Boolean, default=True)
    is_demo_seed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    items = relationship("QuestionSetItem", back_populates="question_set", cascade="all, delete-orphan")

class QuestionSetItem(Base):
    __tablename__ = "question_set_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_set_id = Column(String(50), ForeignKey("question_sets.id", ondelete="CASCADE"), nullable=False)
    question_revision_id = Column(String(50), ForeignKey("question_revisions.id", ondelete="RESTRICT"), nullable=False)
    order_index = Column(Integer, default=1)
    marks = Column(Float, default=2.0)
    
    question_set = relationship("QuestionSet", back_populates="items")
    revision = relationship("QuestionRevision")

class Paper(Base):
    __tablename__ = "papers"
    
    id = Column(String(50), primary_key=True)
    title = Column(String(200), nullable=False)
    subject_id = Column(String(50), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(30), default="draft") # 'draft', 'practice', 'published', 'archived'
    duration_minutes = Column(Integer, default=60)
    total_marks = Column(Float, default=50.0)
    instructions = Column(Text, nullable=True)
    blueprint_json = Column(JSON, nullable=True)
    validation_results_json = Column(JSON, nullable=True)
    warnings_acknowledged = Column(Boolean, default=False)
    is_demo_seed = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    sections = relationship("PaperSection", back_populates="paper", cascade="all, delete-orphan", order_by="PaperSection.section_order")
    items = relationship("PaperItem", back_populates="paper", cascade="all, delete-orphan", order_by="PaperItem.item_order")

class PaperSection(Base):
    __tablename__ = "paper_sections"
    
    id = Column(String(50), primary_key=True)
    paper_id = Column(String(50), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False) # e.g. "Section A: Multiple Choice Questions"
    description = Column(Text, nullable=True)
    section_order = Column(Integer, default=1)
    total_marks = Column(Float, default=20.0)
    instructions = Column(Text, nullable=True)
    
    paper = relationship("Paper", back_populates="sections")
    items = relationship("PaperItem", back_populates="section", cascade="all, delete-orphan")

class PaperItem(Base):
    __tablename__ = "paper_items"
    
    id = Column(String(50), primary_key=True)
    paper_id = Column(String(50), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(String(50), ForeignKey("paper_sections.id", ondelete="CASCADE"), nullable=True)
    question_revision_id = Column(String(50), ForeignKey("question_revisions.id", ondelete="RESTRICT"), nullable=False)
    item_order = Column(Integer, default=1)
    marks = Column(Float, default=2.0)
    
    paper = relationship("Paper", back_populates="items")
    section = relationship("PaperSection", back_populates="items")
    revision = relationship("QuestionRevision")

class Attempt(Base):
    __tablename__ = "attempts"
    
    id = Column(String(50), primary_key=True)
    student_id = Column(String(50), ForeignKey("demo_users.id", ondelete="CASCADE"), nullable=False)
    paper_id = Column(String(50), ForeignKey("papers.id", ondelete="SET NULL"), nullable=True)
    question_set_id = Column(String(50), ForeignKey("question_sets.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    subject_id = Column(String(50), nullable=True)
    mode = Column(String(30), default="assessment") # 'assessment', 'practice', 'mock'
    status = Column(String(30), default="in_progress") # 'in_progress', 'submitted', 'awaiting_grading', 'partially_graded', 'graded', 'expired'
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    deadline_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    graded_at = Column(DateTime, nullable=True)
    total_possible_marks = Column(Float, default=0.0)
    objective_score = Column(Float, nullable=True)
    provisional_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    is_demo_seed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    student = relationship("DemoUser")
    items = relationship("AttemptItem", back_populates="attempt", cascade="all, delete-orphan", order_by="AttemptItem.order_index")
    responses = relationship("Response", back_populates="attempt", cascade="all, delete-orphan")

class AttemptItem(Base):
    __tablename__ = "attempt_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    attempt_id = Column(String(50), ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False)
    question_revision_id = Column(String(50), nullable=False)
    order_index = Column(Integer, default=1)
    marks_allocated = Column(Float, default=2.0)
    question_snapshot_json = Column(JSON, nullable=False) # Immutable snapshot for student taking the test!
    
    attempt = relationship("Attempt", back_populates="items")

class Response(Base):
    __tablename__ = "responses"
    
    id = Column(String(50), primary_key=True)
    attempt_id = Column(String(50), ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False)
    question_revision_id = Column(String(50), nullable=False)
    submitted_answer = Column(Text, nullable=True)
    is_marked_for_review = Column(Boolean, default=False)
    is_correct = Column(Boolean, nullable=True)
    marks_awarded = Column(Float, nullable=True) # Null until graded!
    grading_status = Column(String(30), default="pending") # 'pending', 'auto_graded', 'manually_graded'
    faculty_feedback = Column(Text, nullable=True)
    grader_id = Column(String(50), nullable=True)
    graded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    attempt = relationship("Attempt", back_populates="responses")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=True)
    role = Column(String(20), default="all") # 'faculty', 'student', 'all'
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=True)
    details_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DemoSeedVersion(Base):
    __tablename__ = "demo_seed_version"
    
    version = Column(String(20), primary_key=True)
    seeded_at = Column(DateTime, default=datetime.datetime.utcnow)
    description = Column(Text, nullable=True)
