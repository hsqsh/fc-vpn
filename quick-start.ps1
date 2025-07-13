# Complete Project Startup Script

Write-Host "=== Proxy Service Management Platform ===" -ForegroundColor Green
Write-Host "Complete startup and testing script" -ForegroundColor Cyan

# Function to check if port is available
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

# Function to wait for service
function Wait-ForService {
    param([string]$Url, [string]$ServiceName, [int]$MaxAttempts = 30)
    
    Write-Host "Waiting for $ServiceName to start..." -ForegroundColor Yellow
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✓ $ServiceName is ready!" -ForegroundColor Green
                return $true
            }
        } catch {
            # Service not ready yet
        }
        
        Write-Host "Attempt $i/$MaxAttempts..." -ForegroundColor Gray
        Start-Sleep 2
    }
    
    Write-Host "✗ $ServiceName failed to start within timeout" -ForegroundColor Red
    return $false
}

# Check prerequisites
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow

if (!(Test-Path "venv")) {
    Write-Host "✗ Virtual environment not found" -ForegroundColor Red
    Write-Host "Please run 'install.ps1' first" -ForegroundColor Yellow
    exit 1
}

if (!(Test-Path "frontend/node_modules")) {
    Write-Host "✗ Frontend dependencies not found" -ForegroundColor Red
    Write-Host "Please run 'install.ps1' first" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Prerequisites check passed" -ForegroundColor Green

# Kill existing processes on our ports
Write-Host "`nCleaning up existing processes..." -ForegroundColor Yellow
$ports = @(3000, 3001, 5000, 8888)
foreach ($port in $ports) {
    if (Test-Port $port) {
        Write-Host "Port $port is in use, attempting to free it..." -ForegroundColor Yellow
        try {
            $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
            foreach ($conn in $connections) {
                Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
            }
        } catch {
            Write-Host "Could not free port $port" -ForegroundColor Yellow
        }
    }
}

# Start backend service
Write-Host "`nStarting backend service..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $args[0]
    .\venv\Scripts\Activate.ps1
    python app.py
} -ArgumentList (Get-Location).Path

Start-Sleep 3

# Check if backend started
if (Wait-ForService "http://localhost:5000/health" "Backend API") {
    Write-Host "Backend API: http://localhost:5000" -ForegroundColor Cyan
} else {
    Write-Host "Failed to start backend service" -ForegroundColor Red
    Stop-Job $backendJob -Force
    Remove-Job $backendJob -Force
    exit 1
}

# Start frontend service
Write-Host "`nStarting frontend service..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "$($args[0])\frontend"
    npm run dev -- --port 3000
} -ArgumentList (Get-Location).Path

Start-Sleep 5

# Check frontend (try both 3000 and 3001)
$frontendPort = 3000
if (!(Test-Port 3000) -and (Test-Port 3001)) {
    $frontendPort = 3001
}

Write-Host "`n=== Services Status ===" -ForegroundColor Green
Write-Host "✓ Backend API: http://localhost:5000" -ForegroundColor Cyan
Write-Host "✓ Frontend UI: http://localhost:$frontendPort" -ForegroundColor Cyan
Write-Host "✓ SOCKS5 Proxy: localhost:8888 (when started via UI)" -ForegroundColor Cyan

# Test API endpoints
Write-Host "`nTesting API endpoints..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method GET
    Write-Host "✓ Health check passed" -ForegroundColor Green
    
    $statusResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/proxy/status" -Method GET
    Write-Host "✓ Proxy status API working" -ForegroundColor Green
} catch {
    Write-Host "⚠ Some API endpoints may not be responding" -ForegroundColor Yellow
}

# Open browser
Write-Host "`nOpening web browser..." -ForegroundColor Yellow
Start-Process "http://localhost:$frontendPort"

# Instructions
Write-Host "`n=== Usage Instructions ===" -ForegroundColor Green
Write-Host "1. Use the web interface to start/stop the SOCKS5 proxy" -ForegroundColor White
Write-Host "2. Monitor real-time connections and traffic" -ForegroundColor White
Write-Host "3. Test proxy connections through the UI" -ForegroundColor White
Write-Host "4. Configure proxy settings in the Settings tab" -ForegroundColor White

# Wait for user input
Write-Host "`nPress 'q' to stop all services, or any other key to show logs..." -ForegroundColor Yellow
$key = Read-Host

if ($key -eq 'q') {
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    Stop-Job $backendJob -Force
    Stop-Job $frontendJob -Force
    Remove-Job $backendJob -Force
    Remove-Job $frontendJob -Force
    Write-Host "All services stopped" -ForegroundColor Green
} else {
    Write-Host "`nShowing recent logs..." -ForegroundColor Yellow
    Write-Host "Backend logs:" -ForegroundColor Cyan
    Receive-Job $backendJob | Select-Object -Last 10
    
    Write-Host "`nFrontend logs:" -ForegroundColor Cyan
    Receive-Job $frontendJob | Select-Object -Last 10
    
    Write-Host "`nServices are still running. Use stop.ps1 to stop them." -ForegroundColor Green
}
