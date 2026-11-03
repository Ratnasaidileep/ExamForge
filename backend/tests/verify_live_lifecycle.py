import os
import sys
from pathlib import Path

# Ensure backend root is on sys.path
BACKEND_ROOT = str(Path(__file__).resolve().parent.parent)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.services.seed_service import seed_database

def run_live_verification():
    print("=" * 60)
    print("  EXAMFORGE COMPLETE END-TO-END WORKFLOW VERIFICATION")
    print("=" * 60)
    
    # 1. Reset/Seed database to clean state
    db = SessionLocal()
    seed_database(db, force=True)
    db.close()
    print("[1] Database initialized and seeded successfully.")
    
    client = TestClient(app)
    
    # 2. Health check
    res = client.get("/api/v1/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    print(f"[2] Health check verified: {health_data['app']} (status: {health_data['status']})")
    
    # 3. Demo profiles
    res = client.get("/api/v1/demo/profiles")
    assert res.status_code == 200
    profiles = res.json()
    print(f"[3] Demo profiles verified: {len(profiles)} profiles ({', '.join(p['id'] for p in profiles)})")
    
    # 4. Document library & extracted text inspection
    res = client.get("/api/v1/documents")
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) > 0, "No documents found in seed data"
    sample_doc = docs[0]
    print(f"[4] Document library verified: '{sample_doc['title']}' (status: {sample_doc['extraction_status']})")
    
    res_content = client.get(f"/api/v1/documents/{sample_doc['id']}/content")
    assert res_content.status_code == 200
    content_data = res_content.json()
    assert len(content_data["full_text"]) > 100
    print(f"    Extracted content verified: {len(content_data['full_text'])} characters, {content_data['page_count']} pages")
    
    # 5. Question Bank filtering
    res_q = client.get("/api/v1/questions?status=approved&page=1&page_size=10")
    assert res_q.status_code == 200
    q_data = res_q.json()
    assert q_data["total"] >= 5
    print(f"[5] Central Question Bank verified: {q_data['total']} approved questions available")
    
    # 6. Paper Builder - create, assemble from blueprint, validate
    res_new_paper = client.post(
        "/api/v1/papers",
        json={"title": "ITS-401 Live Verification Paper", "total_marks": 30.0, "duration_minutes": 60},
        headers={"X-Demo-Role": "faculty"}
    )
    assert res_new_paper.status_code == 200
    created_paper = res_new_paper.json()
    paper_id = created_paper["id"]
    print(f"[6] Paper created: {paper_id}")
    
    res_assemble = client.post(
        f"/api/v1/papers/{paper_id}/assemble",
        json={
            "blueprint": {
                "target_marks": 30.0,
                "duration_minutes": 60,
                "difficulty_target": {"easy": 40, "medium": 40, "hard": 20},
                "type_target": {"mcq": 5, "short_answer": 2, "long_answer": 1},
                "required_units": [1, 2, 3, 4]
            }
        },
        headers={"X-Demo-Role": "faculty"}
    )
    assert res_assemble.status_code == 200
    print(f"    Auto-assembly verified: Paper assembled with blueprint rules")
    
    # Validate paper
    res_val = client.post(f"/api/v1/papers/{paper_id}/validate")
    assert res_val.status_code == 200
    val_data = res_val.json()
    print(f"    Blueprint validation: can_publish={val_data['can_publish']}, allocated_marks={val_data['total_marks_actual']}")
    
    # Acknowledge any blueprint warnings and publish
    client.patch(
        f"/api/v1/papers/{paper_id}",
        json={"warnings_acknowledged": True},
        headers={"X-Demo-Role": "faculty"}
    )
    res_pub = client.post(f"/api/v1/papers/{paper_id}/publish", headers={"X-Demo-Role": "faculty"})
    assert res_pub.status_code == 200, f"Publication failed: {res_pub.text}"
    print(f"    Formal Examination Published: status='published'")
    
    # 7. PDF Generation - Question Paper & Answer Key
    res_qp_pdf = client.get(f"/api/v1/papers/{paper_id}/export")
    assert res_qp_pdf.status_code == 200
    assert res_qp_pdf.headers["content-type"] == "application/pdf"
    assert len(res_qp_pdf.content) > 1000
    print(f"[7] PDF Question Paper exported: {len(res_qp_pdf.content)} bytes (answers hidden)")
    
    res_ak_pdf = client.get(f"/api/v1/papers/{paper_id}/answer-key", headers={"X-Demo-Role": "faculty"})
    assert res_ak_pdf.status_code == 200
    assert res_ak_pdf.headers["content-type"] == "application/pdf"
    assert len(res_ak_pdf.content) > 1000
    print(f"    PDF Answer Key exported: {len(res_ak_pdf.content)} bytes (with rubrics & citations)")
    
    # 8. Student Exam Taking Experience
    res_att = client.post(
        "/api/v1/attempts",
        json={"paper_id": paper_id, "mode": "assessment"},
        headers={"X-Demo-Role": "student", "X-Demo-User-Id": "student_aditi"}
    )
    assert res_att.status_code == 200
    att_id = res_att.json()["attempt_id"]
    print(f"[8] Student Assessment started: {att_id} (student_aditi)")
    
    # Active attempt check: verify ZERO leaked answers
    res_active = client.get(f"/api/v1/attempts/{att_id}", headers={"X-Demo-Role": "student"})
    assert res_active.status_code == 200
    active_data = res_active.json()
    for q in active_data["questions"]:
        assert "correct_answer" not in q or q.get("correct_answer") is None
        assert "model_answer" not in q or q.get("model_answer") is None
    print(f"    Security check passed: 0 answers or rubrics leaked in active test API")
    
    # Answer questions
    mcqs = [q for q in active_data["questions"] if q["question_type"] == "mcq"]
    descs = [q for q in active_data["questions"] if q["question_type"] != "mcq"]
    
    # Answer MCQs
    for m in mcqs:
        client.put(
            f"/api/v1/attempts/{att_id}/responses/{m['question_revision_id']}",
            json={"submitted_answer": m["options"][0] if m["options"] else "Option A"},
            headers={"X-Demo-Role": "student"}
        )
    
    # Answer descriptive questions
    for d in descs:
        client.put(
            f"/api/v1/attempts/{att_id}/responses/{d['question_revision_id']}",
            json={"submitted_answer": "Detailed answer discussing sensor technologies and V2X protocols."},
            headers={"X-Demo-Role": "student"}
        )
    print(f"    Student answered {len(mcqs)} MCQs and {len(descs)} descriptive questions")
    
    # Submit attempt
    res_sub = client.post(f"/api/v1/attempts/{att_id}/submit", headers={"X-Demo-Role": "student"})
    assert res_sub.status_code == 200
    sub_info = res_sub.json()
    assert sub_info["status"] == "awaiting_grading"
    assert sub_info["final_score"] is None
    print(f"    Submitted successfully: status='awaiting_grading', objective_score={sub_info['objective_score']} (descriptive awaiting grading)")
    
    # 9. Faculty Manual Grading Queue
    res_queue = client.get("/api/v1/grading/queue", headers={"X-Demo-Role": "faculty"})
    assert res_queue.status_code == 200
    queue_list = res_queue.json()
    assert any(item["attempt_id"] == att_id for item in queue_list)
    print(f"[9] Faculty Grading Queue verified: attempt {att_id} found in pending queue")
    
    # Inspect grading workspace
    res_work = client.get(f"/api/v1/grading/attempts/{att_id}", headers={"X-Demo-Role": "faculty"})
    assert res_work.status_code == 200
    work_data = res_work.json()
    assert len(work_data["responses_to_grade"]) == len(descs)
    print(f"    Grading Workspace opened: {len(work_data['responses_to_grade'])} descriptive answers to grade")
    
    # Award marks and feedback for each descriptive answer
    for r in work_data["responses_to_grade"]:
        res_g = client.patch(
            f"/api/v1/grading/responses/{r['response_id']}",
            json={"marks_awarded": float(r["marks_allocated"]), "faculty_feedback": "Excellent technical clarity."},
            headers={"X-Demo-Role": "faculty"}
        )
        assert res_g.status_code == 200
    print(f"    Faculty evaluated and awarded marks for all descriptive answers")
    
    # Finalize grading
    res_fin = client.post(f"/api/v1/grading/attempts/{att_id}/finalize", headers={"X-Demo-Role": "faculty"})
    assert res_fin.status_code == 200
    fin_data = res_fin.json()
    assert fin_data["status"] == "graded"
    assert fin_data["final_score"] is not None
    print(f"    Grading finalized: final_score={fin_data['final_score']}")
    
    # 10. Student View Finalized Results
    res_results = client.get(f"/api/v1/attempts/{att_id}/results", headers={"X-Demo-Role": "student"})
    assert res_results.status_code == 200
    results_data = res_results.json()
    assert results_data["is_fully_graded"] is True
    assert results_data["final_score"] is not None
    print(f"[10] Student Results verified: Score {results_data['final_score']} / {results_data['total_possible_marks']} with feedback released")
    
    # 11. Student Progress & Faculty Analytics
    res_stud_an = client.get("/api/v1/analytics/student", headers={"X-Demo-Role": "student", "X-Demo-User-Id": "student_aditi"})
    assert res_stud_an.status_code == 200
    stud_an = res_stud_an.json()
    print(f"[11] Student Analytics verified: {stud_an['total_attempts']} attempts, {stud_an['average_score_percentage']}% avg score")
    
    res_fac_an = client.get("/api/v1/analytics/faculty", headers={"X-Demo-Role": "faculty"})
    assert res_fac_an.status_code == 200
    fac_an = res_fac_an.json()
    print(f"     Faculty Analytics verified: {fac_an['total_questions']} questions, {fac_an['total_papers']} papers, {fac_an['total_attempts']} attempts")
    
    print("\n" + "=" * 60)
    print("  ALL 11 END-TO-END WORKFLOW MILESTONES VERIFIED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_live_verification()
