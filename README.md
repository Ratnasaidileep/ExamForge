# ExamForge — AI-Powered Question Paper Generation & Assessment Platform

**ExamForge** is a full-stack, AI-driven examination paper generation and student assessment system engineered specifically for colleges and academic departments.

It provides an end-to-end workflow: faculty upload curriculum notes, generate source-grounded questions using the Google GenAI SDK (Gemini), review citations and edit rubrics, assemble blueprint-validated examination papers, and export separate official Question Paper and Answer Key PDFs. Students take timed assessments in a distraction-free environment with instant objective scoring, while descriptive answers route to a dedicated faculty grading queue for manual evaluation.

---

## 1. System Architecture & Tech Stack

### Frontend
- **Framework:** React 18 with TypeScript
- **Tooling:** Vite 5
- **Styling:** Tailwind CSS with custom design tokens
- **Routing:** React Router v6
- **Charts:** Recharts
- **Icons:** Lucide React

### Backend
- **Framework:** FastAPI with Python 3.11
- **Validation:** Pydantic v2
- **ORM & Database:** SQLAlchemy with SQLite (`PRAGMA foreign_keys = ON;`)
- **AI Integration:** Official Google GenAI Python SDK (`google-genai`) with Gemini models
- **Document Extraction:** `pypdf` (PDF extraction & scanned image detection) and `python-docx` (Word notes)
- **PDF Generation:** ReportLab (academic question papers and separate faculty answer keys)

---

## 2. Design Tokens & Visual Direction

ExamForge combines a clean indigo SaaS navigation shell with a dedicated AI Question Generation Studio:

| Token Name | Hex Code | Visual Application |
|---|---|---|
| **Primary Indigo** | `#3730A3` | Primary brand actions, active headers, sidebar brand |
| **Teal Accent** | `#0F766E` | AI generation buttons, student portal theme |
| **Background** | `#F8FAFC` | Light neutral page surface |
| **Dark Surface** | `#1E293B` | Sidebar navigation, dark cards |
| **Main Text** | `#0F172A` | Primary typography |
| **Secondary Text** | `#64748B` | Subheadings, metadata labels |
| **Borders** | `#E2E8F0` | Clean dividers and cards |
| **Success** | `#15803D` | Approved questions, high mastery, valid blueprint |
| **Warning** | `#B45309` | Draft questions, blueprint warnings, grading queue |
| **Error** | `#B91C1C` | Validation errors, publication blockers, expired tests |

---

## 3. Core Features & Workflows

### Faculty Module
- **Faculty Dashboard (`/faculty/dashboard`):** Real database-backed metrics (uploaded notes, approved questions, published papers, student attempts) and recent student submission activity.
- **Document Library (`/faculty/documents`):** Upload PDF and DOCX course notes (up to 15 MB). Extracts text, detects chapter headings and key topics. Gracefully detects scanned image PDFs without selectable text and alerts that OCR is not supported.
- **AI Question Studio (`/faculty/generate`):** Multi-modal question generation supporting Multiple Choice (MCQ), Short Answer, Long Answer, or Mixed mode. Validates source grounding citations against document text. Shows setup guidance if Gemini API key is missing.
- **Generation Review (`/faculty/generation/:generationId`):** Inspect AI-generated questions alongside exact curriculum excerpts. Edit questions, change marks and rubrics, and approve individual or batch questions into the Question Bank.
- **Central Question Bank (`/faculty/questions`):** Searchable, paginated question bank with multi-dimensional filtering (unit, difficulty, question type, approval status). Edits generate immutable revisions (`Rev 2`) requiring re-approval before inclusion in new published exams.
- **Interactive Paper Builder (`/faculty/papers/new` & `/faculty/papers/:paperId`):**
  - **Left Panel:** Paper metadata, duration, marks, and auto-assembly controls.
  - **Center Panel:** Sections (Sections A, B, C), item reordering, and mark adjusters.
  - **Right Panel:** Live printable question paper preview and real-time blueprint validation.
- **Dual PDF Export:**
  - **Question Paper PDF:** Clean academic layout with college header, instructions, and marks (answers hidden).
  - **Answer Key PDF:** Faculty-only document with correct MCQ choices, model answers, rubric criteria, and curriculum grounding quotes.
- **Manual Grading Queue & Workspace (`/faculty/grading` & `/faculty/grading/:attemptId`):**
  - Evaluates short and long descriptive answers against faculty model answers and rubrics.
  - Server-side validation enforces marks between `0` and maximum allowed marks.
  - Finalization is strictly blocked until all descriptive questions are graded.

### Student Module
- **Student Dashboard (`/student/dashboard`):** Available exams, recent score trends, and topic accuracy breakdown.
- **Practice Library (`/student/practice`):** Browse published formal exams and practice sets. Confirmation modal with duration and test rules before starting.
- **Assessment Taking Interface (`/student/attempt/:attemptId`):**
  - Distraction-free exam room.
  - Countdown timer synchronized with server-enforced deadline.
  - Instant auto-save on navigation.
  - Question status navigator (Answered, Marked for Review, Unanswered).
  - **Strict Security:** Active-attempt APIs never return correct answers or model answers.
- **Assessment Results (`/student/attempt/:attemptId/results`):**
  - Instant objective scoring for MCQs upon submission.
  - Provisional score when descriptive answers are pending faculty grading.
  - Final score released once professor finalizes evaluation.
  - Per-question review with model answers, explanations, and professor feedback.
- **Progress & Insights (`/student/progress`):**
  - Score trajectory trends over time.
  - Evidence-based topic recommendation rule: flags weak topics (<60% accuracy) only after at least 5 questions attempted to prevent small-sample noise.

---

## 4. Quick Start (Windows)

### Prerequisites
- Python 3.11+
- Node.js 18+ (tested with Node v22.20.0 and npm 10.9.3)

### Step 1: Clone and Configure Environment
Copy `.env.example` to `backend/.env`:
```powershell
Copy-Item .env.example backend\.env
```
To enable live AI generation with Gemini, open `backend\.env` and set your API key:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```
*(If no API key is provided, the application will display a setup alert and allow using pre-seeded ITS-401 questions).*

### Step 2: Start the Backend Server
Option A: Double click `run_backend.bat`  
Option B: Run via PowerShell:
```powershell
.\run_backend.ps1
```
The FastAPI server will start at `http://127.0.0.1:8000`.  
API Documentation (Swagger UI) is available at `http://127.0.0.1:8000/docs`.

### Step 3: Start the Frontend Application
Option A: Double click `run_frontend.bat`  
Option B: Run via PowerShell:
```powershell
.\run_frontend.ps1
```
The Vite development server will open at `http://localhost:5173`.

---

## 5. Seeded Course & Demo Roles

ExamForge comes pre-seeded with curriculum data for:
- **Course Subject:** `ITS-401: Intelligent Transport Systems`
- **Units Covered:**
  - Unit 1: Introduction to ITS, Inductive Loops & Radar Sensors
  - Unit 2: Advanced Traffic Management Systems (ATMS), SCATS/SCOOT, Ramp Metering
  - Unit 3: Advanced Traveler Information Systems (ATIS) & FASTag RFID Toll Collection
  - Unit 4: Connected & Autonomous Vehicles (CAV), DSRC vs C-V2X, CACC Platooning
- **Demo Users:**
  - **Faculty:** Dr. R. Sharma (`prof_sharma`)
  - **Student 1:** Aditi Rao (`student_aditi`)
  - **Student 2:** Karthik Nair (`student_karthik`)

### Role Switching
Switch between **Faculty Demo** and **Student Demo** in the top navigation bar anytime. Switching roles preserves shared database state.

### Reset Demo Workspace
To return the application to its initial clean state, click **Reset Demo Workspace** in the sidebar. Requires explicit confirmation and restores seed data without deleting application configuration or API keys.

---

## 6. Automated Testing & Verification

Comprehensive automated tests verify the 18 requirements:
```powershell
cd backend
.\.venv\Scripts\pytest.exe -v
```

### Verified Test Suite (13/13 Passed):
- `test_health_endpoint`: Verifies application startup and health telemetry.
- `test_seed_and_demo_reset`: Verifies deterministic seed data and workspace reset.
- `test_document_validation_empty_and_invalid`: Rejects empty files and invalid extensions.
- `test_source_evidence_grounding`: Verifies exact, fuzzy, and unsupported excerpt checks.
- `test_question_revisions_and_editing`: Verifies that edits create new revisions requiring re-approval.
- `test_draft_question_blocks_publication`: Confirms that unapproved questions block exam publication.
- `test_paper_validation_endpoint`: Validates blueprint constraints and warnings.
- `test_paper_pdf_exports`: Confirms generation of separate Question Paper and Answer Key PDFs.
- `test_active_attempt_security_no_answer_leak`: Confirms active attempt API never leaks correct answers or rubrics.
- `test_mcq_auto_grading_and_descriptive_queue`: Verifies MCQ auto-scoring and descriptive queue routing.
- `test_finalization_blocked_when_pending`: Prevents finalizing attempts with ungraded questions.
- `test_idempotent_submission`: Guarantees submission idempotency without duplicate scoring.
- `test_role_enforcement`: Confirms backend 403 Forbidden checks for role violations.

### Frontend TypeScript & Production Build:
```powershell
cd frontend
npm run build
```
Result: 0 errors; production bundle built cleanly into `frontend/dist/`.

---

## 7. Security & Limitations Notice
- **Educational Demo:** This platform is designed for college demonstration and evaluation workflows. Demo role switching is an interface convenience and does not replace production JWT/OAuth authentication.
- **Local Storage:** Files and SQLite database reside locally under `data/` and `storage/`.
