Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting ExamForge Backend (FastAPI + Uvicorn)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\backend"
& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
