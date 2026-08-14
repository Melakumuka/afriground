param (
    [switch]$InstallDeps = $false
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "    AfriGround GSaaS - Startup Script    " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

if ($InstallDeps) {
    Write-Host "[1/4] Installing dependencies..." -ForegroundColor Yellow
    
    Write-Host "-> Installing Python backend requirements..."
    cd apps\api
    if (-Not (Test-Path .venv)) {
        python -m venv .venv
    }
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    cd ..\..

    Write-Host "-> Installing Node frontend requirements..."
    cd apps\web
    npm install
    cd ..\..
}

Write-Host "[2/4] Starting Docker infrastructure (PostgreSQL, Redis, MinIO)..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "[3/4] Starting FastAPI Backend on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd apps\api; .\.venv\Scripts\Activate.ps1; uvicorn main:app --reload --port 8000"

Write-Host "[4/4] Starting Next.js Frontend on port 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd apps\web; npm run dev"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host " All systems are initializing! " -ForegroundColor Green
Write-Host " Backend: http://localhost:8000 " -ForegroundColor Green
Write-Host " Frontend: http://localhost:3000 " -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Give servers a few seconds to boot before opening the browser
Start-Sleep -Seconds 5
Start-Process "http://localhost:3000/en/station"
