Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting ExamForge Frontend (Vite + React)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\frontend"
npm run dev
