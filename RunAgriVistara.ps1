# AgriVistara - Unified Flask Server Launcher
# This script starts the backend and frontend seamlessly on port 8000.

Write-Host "--- 🚀 Starting AgriVistara Project ---" -ForegroundColor Cyan

# 1. Start Backend in a new window
Write-Host "Starting Unified AI Server on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory "D:\tamilarasu\project" -ArgumentList "-NoExit", "-Command", "& '.\.venv\Scripts\Activate.ps1'; python backend/app.py"

# 2. Wait a moment for server to initialize
Start-Sleep -Seconds 3

# 3. Open the browser
Write-Host "Opening AgriVistara in your default browser..." -ForegroundColor Yellow
Start-Process "http://localhost:8000"

Write-Host "--- ✅ All systems are running! ---" -ForegroundColor Cyan
