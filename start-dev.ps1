# Maccall Platform - Development Server Launcher
Write-Host "==========================================================" -ForegroundColor DarkYellow
Write-Host "   MACCALL — LUXURY AI CREATOR MARKETPLACE & ATELIER      " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor DarkYellow

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start Backend
Write-Host "`n[1/2] Starting FastAPI Backend (Port 8000)..." -ForegroundColor Cyan
$BackendDir = Join-Path $ScriptDir "backend"
$PythonExe = Join-Path $BackendDir "venv\Scripts\python.exe"

Start-Process -FilePath $PythonExe -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -WorkingDirectory $BackendDir

# Start Frontend
Write-Host "[2/2] Starting Vite React Frontend (Port 5173)..." -ForegroundColor Cyan
$FrontendDir = Join-Path $ScriptDir "frontend"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c npx vite --port 5173 --host 127.0.0.1" -WorkingDirectory $FrontendDir

Write-Host "`n✓ Services launched successfully!" -ForegroundColor Green
Write-Host "  - Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  - Swagger Docs: http://localhost:8000/docs`n" -ForegroundColor White
Write-Host "Press any key to exit launcher..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
