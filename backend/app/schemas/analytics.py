from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class TopicAccuracyStat(BaseModel):
    topic_name: str
    total_questions: int
    correct_count: int
    accuracy_percentage: float
    is_weak_area: bool = False
    evidence_count: int = 0
    rule_note: Optional[str] = None

class ScoreBucket(BaseModel):
    range_label: str
    count: int

class FacultyAnalyticsResponse(BaseModel):
    total_documents: int
    total_questions: int
    approved_questions: int
    pending_questions: int
    total_papers: int
    published_papers: int
    total_attempts: int
    pending_grading_count: int
    questions_by_type: Dict[str, int]
    questions_by_difficulty: Dict[str, int]
    questions_by_topic: Dict[str, int]
    score_distribution: List[ScoreBucket]
    topic_accuracies: List[TopicAccuracyStat]
    is_demo_data: bool = True

class PerformanceTrendPoint(BaseModel):
    attempt_id: str
    title: str
    date: str
    score_percentage: float
    status: str

class StudentAnalyticsResponse(BaseModel):
    student_id: str
    student_name: str
    total_attempts: int
    completed_attempts: int
    average_score_percentage: float
    trends: List[PerformanceTrendPoint]
    topic_accuracies: List[TopicAccuracyStat]
    recommended_topics: List[str]
    recommendation_rationale: str
    is_demo_data: bool = True
