# Quick Start Script for Orbis
# Starts both backend and frontend

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Orbis - Starting Services" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (!(Test-Path "venv\Scripts\activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "WARNING: .env not found. Copying from archives..." -ForegroundColor Yellow
    Copy-Item "archives\.env" ".env" -Force
    Write-Host "Created .env file" -ForegroundColor Green
}

Write-Host "Starting Backend..." -ForegroundColor Green
Write-Host "Opening in new window..." -ForegroundColor Yellow

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\activate; Write-Host 'Backend Starting...' -ForegroundColor Green; uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

Write-Host ""
Write-Host "Waiting 5 seconds for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Starting Frontend..." -ForegroundColor Green
Write-Host "Opening in new window..." -ForegroundColor Yellow

# Start frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host 'Frontend Starting...' -ForegroundColor Green; npm run dev"

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "  Services Started!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "To stop: Close the terminal windows" -ForegroundColor Yellow
Write-Host ""
