# AgriVistara - Fix & Start Server
# This script installs/updates dependencies and starts the backend.

Write-Host "--- AgriVistara Server Fix & Start ---" -ForegroundColor Cyan

# 1. Activate virtual environment
Write-Host "[1/4] Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# 2. Uninstall old deprecated package (may or may not exist)
Write-Host "[2/4] Removing deprecated google-generativeai package..." -ForegroundColor Yellow
pip uninstall google-generativeai -y 2>$null

# 3. Install/update all dependencies
Write-Host "[3/4] Installing/updating all dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# 4. Start the server
Write-Host "[4/4] Starting AgriVistara Server on http://localhost:8000..." -ForegroundColor Green
Write-Host ""
python backend/app.py
