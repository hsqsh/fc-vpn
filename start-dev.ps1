# Start Development Environment

Write-Host "Starting Proxy Service Management Platform..." -ForegroundColor Green

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "Virtual environment not found. Please run install.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Start backend service in background
Write-Host "Starting backend service..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\venv\Scripts\Activate.ps1; python app.py" -WindowStyle Minimized

# Wait for backend to start
Start-Sleep 3

# Start frontend development server
Write-Host "Starting frontend development server..." -ForegroundColor Yellow
cd frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"
cd ..

Write-Host "Services started!" -ForegroundColor Green
Write-Host "Web Interface: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API Endpoint: http://localhost:5000" -ForegroundColor Cyan
Write-Host "SOCKS5 Proxy: localhost:8888" -ForegroundColor Cyan

Write-Host "Press any key to continue..."
Read-Host
