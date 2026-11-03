import os
import sys
import datetime
import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def api_call(path, method="GET", data=None, role="faculty"):
    url = f"{BASE_URL}{path}"
    headers = {
        "Content-Type": "application/json",
        "X-Demo-Role": role
    }
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            try:
                return resp.status, json.loads(content.decode("utf-8"))
            except Exception:
                return resp.status, content
    except urllib.error.HTTPError as e:
        error_content = e.read().decode("utf-8")
        try:
            return e.code, json.loads(error_content)
        except Exception:
            return e.code, error_content

def run():
    print("=" * 60)
    print("  VERIFYING SCHEDULED EXAMS & LATEX / KATEX CAPABILITIES")
    print("=" * 60)

    # 1. Health check
    status, body = api_call("/health")
    assert status == 200, f"Health check failed: {body}"
    print(f"[PASS] 1. Live API responsive: {body['app']}")

    # 2. LaTeX STEM Equation Paper & PDF Export
    print("\n--- Testing LaTeX STEM Equation Export ---")
    status, new_paper = api_call("/papers", method="POST", data={
        "title": "STEM Advanced Physics: $E = mc^2$ and $$\\frac{\\partial \\psi}{\\partial t}$$",
        "subject_id": "ITS-401",
        "total_marks": 25.0,
        "duration_minutes": 60
    })
    assert status == 200, f"Create paper failed: {new_paper}"
    paper_id = new_paper["id"]
    print(f"[PASS] 2. Created LaTeX Exam Paper: {paper_id}")

    # Auto-assemble questions into paper
    status, asm = api_call(f"/papers/{paper_id}/assemble", method="POST", data={
        "blueprint": {
            "target_marks": 25.0,
            "duration_minutes": 60,
            "difficulty_target": {"easy": 40, "medium": 40, "hard": 20},
            "type_target": {"mcq": 5, "short_answer": 2}
        }
    })
    assert status == 200, f"Assemble failed: {asm}"
    print(f"[PASS] 3. Assembled paper layout with blueprint.")

    # Export PDF question paper
    status, pdf_bytes = api_call(f"/papers/{paper_id}/export")
    assert status == 200, f"PDF export failed: {pdf_bytes}"
    assert len(pdf_bytes) > 2000, f"PDF export too small: {len(pdf_bytes)} bytes"
    assert pdf_bytes.startswith(b"%PDF"), "Exported file is not a valid PDF"
    print(f"[PASS] 4. Exported official question paper PDF ({len(pdf_bytes)} bytes).")

    # Export PDF answer key
    status, key_bytes = api_call(f"/papers/{paper_id}/answer-key")
    assert status == 200, f"Key export failed: {key_bytes}"
    assert len(key_bytes) > 2000, f"Key export too small: {len(key_bytes)} bytes"
    assert key_bytes.startswith(b"%PDF"), "Exported key is not a valid PDF"
    print(f"[PASS] 5. Exported faculty evaluation key & rubric PDF ({len(key_bytes)} bytes).")

    # 3. Scheduled Window Examinations
    print("\n--- Testing Scheduled Window Examinations ---")
    # Publish paper first
    status, pub = api_call(f"/papers/{paper_id}/publish", method="POST")
    assert status == 200, f"Publish failed: {pub}"
    print(f"[PASS] 6. Paper published as formal examination.")

    now = datetime.datetime.utcnow()
    # Scenario A: Future scheduled window (Starts 2 hours from now)
    future_start = (now + datetime.timedelta(hours=2)).isoformat()
    future_end = (now + datetime.timedelta(hours=4)).isoformat()
    status, patch1 = api_call(f"/papers/{paper_id}", method="PATCH", data={
        "window_start": future_start,
        "window_end": future_end
    })
    assert status == 200
    print(f"[PASS] 7. Scheduled future exam window: {future_start} -> {future_end}")

    # Student attempts early -> MUST BE BLOCKED
    status, att_early = api_call("/attempts", method="POST", data={
        "paper_id": paper_id,
        "mode": "assessment"
    }, role="student")
    assert status == 400, f"Expected 400 for early attempt, got {status}: {att_early}"
    assert "Exam window has not opened yet" in att_early.get("error", att_early.get("detail", ""))
    print(f"[PASS] 8. Early student attempt correctly blocked: '{att_early.get('error')}'")

    # Scenario B: Past scheduled window (Closed 1 hour ago)
    past_start = (now - datetime.timedelta(hours=3)).isoformat()
    past_end = (now - datetime.timedelta(hours=1)).isoformat()
    status, patch2 = api_call(f"/papers/{paper_id}", method="PATCH", data={
        "window_start": past_start,
        "window_end": past_end
    })
    assert status == 200
    print(f"[PASS] 9. Scheduled past closed exam window: {past_start} -> {past_end}")

    # Student attempts late -> MUST BE BLOCKED
    status, att_late = api_call("/attempts", method="POST", data={
        "paper_id": paper_id,
        "mode": "assessment"
    }, role="student")
    assert status == 400, f"Expected 400 for late attempt, got {status}: {att_late}"
    assert "Exam window has closed" in att_late.get("error", att_late.get("detail", ""))
    print(f"[PASS] 10. Late student attempt correctly blocked: '{att_late.get('error')}'")

    # Scenario C: Currently active window (Opened 10 mins ago, closes in 1 hour)
    active_start = (now - datetime.timedelta(minutes=10)).isoformat()
    active_end = (now + datetime.timedelta(hours=1)).isoformat()
    status, patch3 = api_call(f"/papers/{paper_id}", method="PATCH", data={
        "window_start": active_start,
        "window_end": active_end
    })
    assert status == 200
    print(f"[PASS] 11. Scheduled active exam window: {active_start} -> {active_end}")

    # Student attempts within window -> MUST SUCCEED
    status, att_active = api_call("/attempts", method="POST", data={
        "paper_id": paper_id,
        "mode": "assessment"
    }, role="student")
    assert status == 200, f"Expected 200 for active attempt, got {status}: {att_active}"
    att_id = att_active["attempt_id"]
    print(f"[PASS] 12. Student attempt successfully started within window: {att_id}")

    # Verify attempt questions & timer
    status, att_detail = api_call(f"/attempts/{att_id}", role="student")
    assert status == 200
    assert att_detail["remaining_seconds"] > 0
    print(f"[PASS] 13. Active attempt verified with {len(att_detail['questions'])} questions and {att_detail['remaining_seconds']}s remaining.")

    print("\n" + "=" * 60)
    print("  ALL 13 VERIFICATION CHECKS PASSED WITH FLYING COLORS!")
    print("=" * 60)

if __name__ == "__main__":
    run()
