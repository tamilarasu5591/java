# This script will FORCE STOP any old servers running on Port 8000 and start the deep AI backend cleanly!

Write-Host "--- Stopping old static servers... ---" -ForegroundColor Yellow
$proc = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "Found old Python processes. Closing them..." -ForegroundColor Red
    Stop-Process -Name "python" -Force
    Start-Sleep -Seconds 2
} else {
    Write-Host "No old pythons running. Port is clear!" -ForegroundColor Green
}

Write-Host "--- Activating Environment & Starting AI Server ---" -ForegroundColor Cyan
& ".\.venv\Scripts\Activate.ps1"
python backend/app.py
