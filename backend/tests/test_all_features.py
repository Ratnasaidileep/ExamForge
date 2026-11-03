import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.config import settings
from app.db.session import Base, get_db
from app.db.models import Question, QuestionRevision, Paper, Attempt, Response, Document
from app.services.seed_service import seed_database
from app.services.gemini_service import verify_grounding

# In-memory or test database
TEST_DB_PATH = Path("./test_examforge.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH.resolve()}"

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    seed_database(db, force=True)
    db.close()
    yield
    # Cleanup
    Base.metadata.drop_all(bind=test_engine)
    if TEST_DB_PATH.exists():
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

client = TestClient(app)

# 1. Application startup and health endpoint
def test_health_endpoint():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["app"] == "ExamForge"

# 2. Seed data and demo reset
def test_seed_and_demo_reset():
    resp = client.get("/api/v1/demo/profiles")
    assert resp.status_code == 200
    profiles = resp.json()
    assert len(profiles) >= 3
    
    # Test reset
    reset_resp = client.post("/api/v1/demo/reset", json={"confirm": True})
    assert reset_resp.status_code == 200
    assert reset_resp.json()["success"] is True

# 3. Document validation and extraction
def test_document_validation_empty_and_invalid():
    # Empty file
    resp = client.post(
        "/api/v1/documents",
        data={"title": "Empty", "subject_id": "ITS-401"},
        files={"file": ("test.pdf", b"", "application/pdf")},
        headers={"X-Demo-Role": "faculty"}
    )
    assert resp.status_code == 400
    
    # Unsupported extension
    resp_txt = client.post(
        "/api/v1/documents",
        data={"title": "Text", "subject_id": "ITS-401"},
        files={"file": ("test.txt", b"Hello text", "text/plain")},
        headers={"X-Demo-Role": "faculty"}
    )
    assert resp_txt.status_code == 400

# 4. Source-evidence validation
def test_source_evidence_grounding():
    source = "Inductive loop detectors embedded beneath pavement detect magnetic field disruptions."
    
    # Exact match
    flag, ratio = verify_grounding("Inductive loop detectors embedded beneath pavement", source)
    assert flag == "grounded"
    assert ratio >= 0.9
    
    # Unsupported
    flag_bad, _ = verify_grounding("Quantum blockchain satellites orbit Mars", source)
    assert flag_bad == "unsupported"

# 5. Question approval and revision history
def test_question_revisions_and_editing():
    # Fetch questions
    resp = client.get("/api/v1/questions?page=1&page_size=10")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) > 0
    q = items[0]
    q_id = q["id"]
    
    # Edit question -> creates revision 2
    patch_resp = client.patch(
        f"/api/v1/questions/{q_id}",
        json={"question_text": "Updated question text for ITS sensor analysis?"},
        headers={"X-Demo-Role": "faculty"}
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["success"] is True
    assert "v2" in data["new_revision_id"]
    assert data["status"] == "draft" # Requires re-approval!

# 6. Draft questions cannot be used in formal publication
def test_draft_question_blocks_publication():
    db = TestingSessionLocal()
    # Create a draft paper containing a draft question
    draft_q = db.query(Question).filter(Question.status == "draft").first()
    if draft_q:
        paper = Paper(
            id="test_paper_draft_block",
            title="Integrity Test Paper",
            subject_id="ITS-401",
            status="draft",
            total_marks=2.0
        )
        db.add(paper)
        db.flush()
        
        from app.db.models import PaperSection, PaperItem
        sec = PaperSection(id="t_sec_1", paper_id=paper.id, name="Sec 1", total_marks=2.0)
        db.add(sec)
        db.flush()
        
        item = PaperItem(
            id="t_item_1",
            paper_id=paper.id,
            section_id=sec.id,
            question_revision_id=draft_q.current_revision_id,
            marks=2.0
        )
        db.add(item)
        db.commit()
        db.close()
        
        # Try to publish -> Must fail!
        pub_resp = client.post(
            f"/api/v1/papers/test_paper_draft_block/publish",
            headers={"X-Demo-Role": "faculty"}
        )
        assert pub_resp.status_code == 400
        assert "draft/unapproved" in pub_resp.json()["detail"] or "Cannot publish" in pub_resp.json()["detail"]

# 7. Paper blueprint validation and warnings
def test_paper_validation_endpoint():
    resp = client.post("/api/v1/papers/paper_its_midterm_2026/validate")
    assert resp.status_code == 200
    val = resp.json()
    assert "can_publish" in val
    assert "warnings" in val
    assert "errors" in val

# 8. Paper export generates valid PDFs
def test_paper_pdf_exports():
    # Export question paper
    qp_resp = client.get("/api/v1/papers/paper_its_midterm_2026/export")
    assert qp_resp.status_code == 200
    assert qp_resp.headers["content-type"] == "application/pdf"
    assert len(qp_resp.content) > 1000
    
    # Export answer key (faculty only)
    ak_resp = client.get(
        "/api/v1/papers/paper_its_midterm_2026/answer-key",
        headers={"X-Demo-Role": "faculty"}
    )
    assert ak_resp.status_code == 200
    assert ak_resp.headers["content-type"] == "application/pdf"
    assert len(ak_resp.content) > 1000

# 9. Active student attempts DO NOT expose answer keys
def test_active_attempt_security_no_answer_leak():
    # Start attempt
    start_resp = client.post(
        "/api/v1/attempts",
        json={"paper_id": "paper_its_midterm_2026", "mode": "assessment"},
        headers={"X-Demo-Role": "student", "X-Demo-User-Id": "student_aditi"}
    )
    assert start_resp.status_code == 200
    att_id = start_resp.json()["attempt_id"]
    
    # Fetch active attempt
    att_resp = client.get(
        f"/api/v1/attempts/{att_id}",
        headers={"X-Demo-Role": "student", "X-Demo-User-Id": "student_aditi"}
    )
    assert att_resp.status_code == 200
    att_data = att_resp.json()
    
    for q in att_data["questions"]:
        # Verify no correct answer or model answer fields exist in schema
        assert "correct_answer" not in q or q.get("correct_answer") is None
        assert "model_answer" not in q or q.get("model_answer") is None
        assert "rubric_json" not in q or q.get("rubric_json") is None

# 10. MCQ automatic grading & descriptive answers to grading queue
def test_mcq_auto_grading_and_descriptive_queue():
    # Start attempt
    start_resp = client.post(
        "/api/v1/attempts",
        json={"paper_id": "paper_its_midterm_2026", "mode": "assessment"},
        headers={"X-Demo-Role": "student", "X-Demo-User-Id": "student_karthik"}
    )
    att_id = start_resp.json()["attempt_id"]
    
    # Fetch active questions to get revision ids
    att_data = client.get(f"/api/v1/attempts/{att_id}").json()
    first_mcq = next(q for q in att_data["questions"] if q["question_type"] == "mcq")
    first_desc = next(q for q in att_data["questions"] if q["question_type"] != "mcq")
    
    # Save MCQ answer (correct answer)
    client.put(
        f"/api/v1/attempts/{att_id}/responses/{first_mcq['question_revision_id']}",
        json={"submitted_answer": "Inductive loop detectors"},
        headers={"X-Demo-Role": "student"}
    )
    
    # Save descriptive answer
    client.put(
        f"/api/v1/attempts/{att_id}/responses/{first_desc['question_revision_id']}",
        json={"submitted_answer": "Physical, logical, and communication layers coordinate traffic data."},
        headers={"X-Demo-Role": "student"}
    )
    
    # Submit attempt
    sub_resp = client.post(
        f"/api/v1/attempts/{att_id}/submit",
        headers={"X-Demo-Role": "student"}
    )
    assert sub_resp.status_code == 200
    sub_data = sub_resp.json()
    assert sub_data["status"] == "awaiting_grading"
    assert sub_data["objective_score"] >= 2.0
    assert sub_data["final_score"] is None # UNGRADED descriptive answer keeps final_score null!
    
    # Check grading queue as faculty
    queue_resp = client.get("/api/v1/grading/queue", headers={"X-Demo-Role": "faculty"})
    assert queue_resp.status_code == 200
    q_items = queue_resp.json()
    assert any(item["attempt_id"] == att_id for item in q_items)

# 11. Finalization blocked while required grading incomplete
def test_finalization_blocked_when_pending():
    # Use att_seed_karthik_pending which has ungraded responses
    fin_resp = client.post(
        "/api/v1/grading/attempts/att_seed_karthik_pending/finalize",
        headers={"X-Demo-Role": "faculty"}
    )
    assert fin_resp.status_code == 400
    assert "not been graded yet" in fin_resp.json()["detail"]

# 12. Idempotent submission
def test_idempotent_submission():
    sub1 = client.post("/api/v1/attempts/att_seed_aditi_graded/submit")
    assert sub1.status_code == 200
    assert sub1.json()["status"] == "graded"

# 13. Role restrictions: Student blocked from faculty-only endpoints
def test_role_enforcement():
    # Student tries to access grading queue
    grad_resp = client.get("/api/v1/grading/queue", headers={"X-Demo-Role": "student"})
    assert grad_resp.status_code == 403
    
    # Student tries to export confidential answer key
    ak_resp = client.get("/api/v1/papers/paper_its_midterm_2026/answer-key", headers={"X-Demo-Role": "student"})
    assert ak_resp.status_code == 403

# 14. Offline demo question generation
def test_offline_demo_generation():
    doc_resp = client.get("/api/v1/documents", headers={"X-Demo-Role": "faculty"})
    assert doc_resp.status_code == 200
    docs = doc_resp.json()
    assert len(docs) > 0
    doc_id = docs[0]["id"]

    gen_resp = client.post(
        "/api/v1/generations",
        json={
            "document_id": doc_id,
            "subject_id": "ITS-401",
            "question_types": ["mcq", "short_answer"],
            "difficulty": "medium",
            "requested_count": 2,
            "use_offline_demo": True
        },
        headers={"X-Demo-Role": "faculty"}
    )
    assert gen_resp.status_code == 200
    gen_data = gen_resp.json()
    assert gen_data["success"] is True
    assert gen_data["generated_count"] >= 1
    job_id = gen_data["job_id"]

    # Verify generated questions
    job_resp = client.get(f"/api/v1/generations/{job_id}", headers={"X-Demo-Role": "faculty"})
    assert job_resp.status_code == 200
    job_info = job_resp.json()
    g_questions = job_info["generated_questions"]
    assert len(g_questions) >= 1
    first_gq = g_questions[0]

    # Test Duplicate generated question
    dup_resp = client.post(
        f"/api/v1/generations/questions/{first_gq['id']}/duplicate",
        headers={"X-Demo-Role": "faculty"}
    )
    assert dup_resp.status_code == 200
    dup_gq = dup_resp.json()
    assert "(Copy)" in dup_gq["question_text"]

    # Test Discard generated question
    del_resp = client.delete(
        f"/api/v1/generations/questions/{dup_gq['id']}",
        headers={"X-Demo-Role": "faculty"}
    )
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

# 15. Question duplication in central question bank
def test_question_bank_duplication():
    # List questions
    q_resp = client.get("/api/v1/questions?page_size=1")
    assert q_resp.status_code == 200
    q_items = q_resp.json()["items"]
    assert len(q_items) > 0
    target_q = q_items[0]

    # Duplicate question
    dup_resp = client.post(
        f"/api/v1/questions/{target_q['id']}/duplicate",
        headers={"X-Demo-Role": "faculty"}
    )
    assert dup_resp.status_code == 200
    dup_data = dup_resp.json()
    assert dup_data["success"] is True
    new_q_id = dup_data["question_id"]

    # Check new question
    detail_resp = client.get(f"/api/v1/questions/{new_q_id}")
    assert detail_resp.status_code == 200
    q_detail = detail_resp.json()
    assert q_detail["status"] == "draft"
    assert "(Copy)" in q_detail["current_revision"]["question_text"]

# 16. Paper section custom addition and deletion
def test_paper_section_controls():
    # Create draft paper
    p_resp = client.post(
        "/api/v1/papers",
        json={"title": "Test Section Controls Paper", "total_marks": 40.0, "duration_minutes": 60},
        headers={"X-Demo-Role": "faculty"}
    )
    assert p_resp.status_code == 200
    paper_id = p_resp.json()["id"]

    # Add custom Section D
    p_detail = client.get(f"/api/v1/papers/{paper_id}").json()
    current_sections = p_detail["sections"]
    new_sec = {
        "id": "sec_custom_case_study",
        "name": "Section D: Case Study Analysis",
        "total_marks": 10.0,
        "section_order": len(current_sections) + 1,
        "items": []
    }
    current_sections.append(new_sec)

    patch_resp = client.patch(
        f"/api/v1/papers/{paper_id}",
        json={"sections": current_sections},
        headers={"X-Demo-Role": "faculty"}
    )
    assert patch_resp.status_code == 200

    # Verify updated section list
    updated_p = client.get(f"/api/v1/papers/{paper_id}").json()
    assert any(s["name"] == "Section D: Case Study Analysis" for s in updated_p["sections"])

# 17. LaTeX / KaTeX equation PDF formatting and generation
def test_latex_pdf_formatting():
    from app.services.pdf_export import format_latex_for_pdf, generate_question_paper_pdf, generate_answer_key_pdf
    
    # Check equation conversion
    raw_latex = "Calculate the energy $E = mc^2$ and the ratio $$\\frac{a + b}{c}$$ when $\\alpha = 0.05$."
    formatted = format_latex_for_pdf(raw_latex)
    assert "mc<sup>2</sup>" in formatted
    assert "(a + b / c)" in formatted
    assert "α" in formatted
    assert "$" not in formatted

    # Test PDF generation with LaTeX content
    sample_paper = {
        "id": "test_latex_paper",
        "title": "STEM Exam: Modern Physics $E = mc^2$",
        "subject_id": "PHY-101",
        "duration_minutes": 60,
        "total_marks": 20.0
    }
    sample_sections = [
        {
            "name": "Section A: Quantum Mechanics",
            "total_marks": 20.0,
            "items": [
                {
                    "marks": 5.0,
                    "question_text": "Derive the wave equation $$\\frac{\\partial^2 \\psi}{\\partial x^2} = \\frac{1}{v^2} \\frac{\\partial^2 \\psi}{\\partial t^2}$$",
                    "revision": {
                        "question_text": "Derive the wave equation $$\\frac{\\partial^2 \\psi}{\\partial x^2} = \\frac{1}{v^2} \\frac{\\partial^2 \\psi}{\\partial t^2}$$",
                        "question_type": "short_answer",
                        "marks": 5.0,
                        "model_answer": "By separating variables $\\psi(x,t) = X(x)T(t)$...",
                        "rubric_json": [{"criteria": "Derivation", "marks": 5.0}],
                        "explanation": "Fundamental wave mechanics equation."
                    }
                }
            ]
        }
    ]
    
    paper_pdf_path = generate_question_paper_pdf(sample_paper, sample_sections)
    assert os.path.exists(paper_pdf_path)
    assert os.path.getsize(paper_pdf_path) > 1000

    key_pdf_path = generate_answer_key_pdf(sample_paper, sample_sections)
    assert os.path.exists(key_pdf_path)
    assert os.path.getsize(key_pdf_path) > 1000

# 18. Scheduled Window Examinations
def test_scheduled_window_examinations():
    import datetime
    now = datetime.datetime.utcnow()

    # 1. Create paper
    p_resp = client.post(
        "/api/v1/papers",
        json={"title": "Scheduled Finals Exam", "total_marks": 30.0, "duration_minutes": 45},
        headers={"X-Demo-Role": "faculty"}
    )
    assert p_resp.status_code == 200
    paper_id = p_resp.json()["id"]

    # Assemble questions into paper
    asm_resp = client.post(
        f"/api/v1/papers/{paper_id}/assemble",
        json={
            "blueprint": {
                "target_marks": 30.0,
                "duration_minutes": 45,
                "difficulty_target": {"easy": 40, "medium": 40, "hard": 20},
                "type_target": {"mcq": 5, "short_answer": 2, "long_answer": 1}
            }
        },
        headers={"X-Demo-Role": "faculty"}
    )
    assert asm_resp.status_code == 200

    # Publish paper
    pub_resp = client.post(f"/api/v1/papers/{paper_id}/publish", headers={"X-Demo-Role": "faculty"})
    assert pub_resp.status_code == 200

    # 2. Set window in future (starts 2 hours from now)
    future_start = (now + datetime.timedelta(hours=2)).isoformat()
    future_end = (now + datetime.timedelta(hours=4)).isoformat()
    patch_resp = client.patch(
        f"/api/v1/papers/{paper_id}",
        json={"window_start": future_start, "window_end": future_end},
        headers={"X-Demo-Role": "faculty"}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["window_start"] is not None

    # Student attempts before window opens -> BLOCKED
    att_resp_early = client.post(
        "/api/v1/attempts",
        json={"paper_id": paper_id, "mode": "assessment"},
        headers={"X-Demo-Role": "student"}
    )
    assert att_resp_early.status_code == 400
    assert "Exam window has not opened yet" in att_resp_early.json()["error"]

    # 3. Set window in past (closed 1 hour ago)
    past_start = (now - datetime.timedelta(hours=3)).isoformat()
    past_end = (now - datetime.timedelta(hours=1)).isoformat()
    patch_resp2 = client.patch(
        f"/api/v1/papers/{paper_id}",
        json={"window_start": past_start, "window_end": past_end},
        headers={"X-Demo-Role": "faculty"}
    )
    assert patch_resp2.status_code == 200

    # Student attempts after window closed -> BLOCKED
    att_resp_late = client.post(
        "/api/v1/attempts",
        json={"paper_id": paper_id, "mode": "assessment"},
        headers={"X-Demo-Role": "student"}
    )
    assert att_resp_late.status_code == 400
    assert "Exam window has closed" in att_resp_late.json()["error"]

    # 4. Set window currently active (opened 10 mins ago, closes in 1 hour)
    active_start = (now - datetime.timedelta(minutes=10)).isoformat()
    active_end = (now + datetime.timedelta(hours=1)).isoformat()
    patch_resp3 = client.patch(
        f"/api/v1/papers/{paper_id}",
        json={"window_start": active_start, "window_end": active_end},
        headers={"X-Demo-Role": "faculty"}
    )
    assert patch_resp3.status_code == 200

    # Student attempts within active window -> SUCCESS
    att_resp_active = client.post(
        "/api/v1/attempts",
        json={"paper_id": paper_id, "mode": "assessment"},
        headers={"X-Demo-Role": "student"}
    )
    assert att_resp_active.status_code == 200
    att_data = att_resp_active.json()
    assert att_data["status"] == "in_progress"
    assert att_data["remaining_seconds"] > 0

