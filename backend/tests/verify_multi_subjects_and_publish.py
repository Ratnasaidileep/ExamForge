import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def api_get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"X-Demo-Role": "faculty", "X-Demo-User-ID": "prof_sharma"})
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode())

def api_post(endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    payload = json.dumps(data or {}).encode("utf-8") if data is not None else b""
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Demo-Role": "faculty",
            "X-Demo-User-ID": "prof_sharma"
        }
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode())

def main():
    print("=================================================================")
    print("EXAMFORGE: MULTI-SUBJECTS & PAPER PUBLICATION VERIFICATION SUITE")
    print("=================================================================")

    # 1. Reset Workspace to fresh seeded state
    print("\n[Step 1] Resetting demo workspace...")
    status, reset_res = api_post("/demo/reset", {"confirm": True})
    assert status == 200, f"Reset failed: {reset_res}"
    print(f"  [OK] Workspace reset successful: {reset_res['message']}")

    # 2. Verify Preloaded Subjects
    print("\n[Step 2] Verifying preloaded subjects...")
    status, subjects = api_get("/subjects")
    assert status == 200, f"Failed to get subjects: {subjects}"
    expected_codes = {"ITS-401", "CS-301", "AI-402", "CY-201", "DS-202"}
    actual_codes = {s["code"] for s in subjects}
    print(f"Found {len(subjects)} subjects: {sorted(list(actual_codes))}")
    assert expected_codes.issubset(actual_codes), f"Missing expected subjects! Got {actual_codes}"
    for s in subjects:
        print(f"  * {s['code']}: {s['name']} ({len(s['topics'])} topics)")
        assert len(s["topics"]) >= 4, f"Subject {s['code']} has fewer than 4 topics"
    print("  [OK] All 5 preloaded subjects verified with topics!")

    # 3. Verify Documents
    print("\n[Step 3] Verifying preloaded curriculum documents...")
    status, docs = api_get("/documents")
    assert status == 200
    doc_subjects = {d["subject_id"] for d in docs}
    print(f"Found {len(docs)} curriculum documents across subjects: {doc_subjects}")
    assert expected_codes.issubset(doc_subjects), f"Documents missing for subjects: {expected_codes - doc_subjects}"
    print("  [OK] All 5 subjects have lecture notes documents loaded!")

    # 4. Verify Question Bank
    print("\n[Step 4] Verifying question bank...")
    status, q_data = api_get("/questions?page_size=100")
    assert status == 200
    all_qs = q_data["items"]
    print(f"Total questions in bank: {len(all_qs)}")
    assert len(all_qs) >= 40, f"Expected at least 40 approved questions, got {len(all_qs)}"
    q_subjects = {q["subject_id"] for q in all_qs}
    print(f"Questions distributed across subjects: {q_subjects}")
    assert expected_codes.issubset(q_subjects)
    print("  [OK] All 40 approved questions verified across 5 subjects!")

    # 5. Verify Examination Papers
    print("\n[Step 5] Verifying examination papers and ready-to-publish drafts...")
    status, papers = api_get("/papers")
    assert status == 200
    print(f"Total papers in library: {len(papers)}")
    assert len(papers) >= 6, f"Expected 6 papers, got {len(papers)}"

    draft_papers = [p for p in papers if p["status"] == "draft"]
    published_papers = [p for p in papers if p["status"] == "published"]
    print(f"Published papers: {len(published_papers)}")
    print(f"Draft (Ready to Publish) papers: {len(draft_papers)}")
    assert len(draft_papers) >= 5, f"Expected at least 5 ready-to-publish draft papers, got {len(draft_papers)}"

    # 6. Test Publishing each of the 5 Ready-to-Publish Draft Papers
    print("\n[Step 6] Testing formal publication for each draft paper...")
    for dp in draft_papers:
        paper_id = dp["id"]
        title = dp["title"]
        subject = dp["subject_id"]
        print(f"\n  Validating & Publishing: [{subject}] {paper_id} ('{title}')...")

        # Validate paper first
        v_status, val_res = api_post(f"/papers/{paper_id}/validate")
        assert v_status == 200
        print(f"    - Validation Result: is_valid={val_res['is_valid']}, can_publish={val_res['can_publish']}")
        assert val_res["can_publish"] is True, f"Paper cannot publish! Errors: {val_res['errors']}"
        assert len(val_res["errors"]) == 0, f"Blocking errors found: {val_res['errors']}"
        assert val_res["total_marks_actual"] == val_res["total_marks_expected"], "Marks mismatch"

        # Publish paper
        p_status, pub_res = api_post(f"/papers/{paper_id}/publish")
        assert p_status == 200, f"Publish failed for {paper_id}: {pub_res}"
        assert pub_res["success"] is True
        print(f"    [OK] Successfully published! Message: '{pub_res['message']}'")

    # 7. Verify All Papers are Now Published & Available for Students
    print("\n[Step 7] Verifying all papers are now published & in student dashboard...")
    status, updated_papers = api_get("/papers?status=published")
    assert status == 200
    print(f"Total officially published papers: {len(updated_papers)}")
    assert len(updated_papers) >= 6, "Expected at least 6 published papers after publishing drafts"

    status, student_dash = api_get("/dashboard/student")
    assert status == 200
    available_to_students = student_dash["available_assessments"]
    print(f"Assessments available to students: {len(available_to_students)}")
    assert len(available_to_students) >= 6, "Students should see all newly published papers"
    print("  [OK] All 6 papers verified accessible in student portal!")

    # 8. Reset Workspace back to fresh draft state for user
    print("\n[Step 8] Resetting demo workspace back to pristine draft state for user demonstration...")
    api_post("/demo/reset", {"confirm": True})
    status, final_papers = api_get("/papers")
    draft_count = sum(1 for p in final_papers if p["status"] == "draft")
    pub_count = sum(1 for p in final_papers if p["status"] == "published")
    print(f"Pristine state restored: {pub_count} published paper + {draft_count} ready-to-publish draft papers.")
    print("\n=================================================================")
    print("ALL VERIFICATION CHECKS PASSED WITH 100% SUCCESS (0 ERRORS)!")
    print("=================================================================")

if __name__ == "__main__":
    main()
