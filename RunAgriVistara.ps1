# AgriVistara - Multi-Service Launcher
# This script starts the Backend (Flask) and Frontend (HTTP Server) simultaneously

Write-Host "--- 🚀 Starting AgriVistara Project ---" -ForegroundColor Cyan

# 1. Start Backend in a new window
Write-Host "Starting AI Backend on http://localhost:5000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python backend/app.py"

# 2. Wait a moment for backend to initialize
Start-Sleep -Seconds 2

# 3. Start Frontend in a new window
Write-Host "Starting Frontend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m http.server 8000"

# 4. Open the browser
Write-Host "Opening AgriVistara in your default browser..." -ForegroundColor Yellow
Start-Process "http://localhost:8000"

Write-Host "--- ✅ All systems are running! ---" -ForegroundColor Cyan
