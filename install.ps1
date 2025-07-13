# Installation and Environment Check Script

Write-Host "=== Proxy Service Management Platform Installation ===" -ForegroundColor Green

# Check system requirements
Write-Host "`nChecking system requirements..." -ForegroundColor Yellow

# Check PowerShell version
$psVersion = $PSVersionTable.PSVersion
Write-Host "PowerShell Version: $psVersion" -ForegroundColor Cyan
if ($psVersion.Major -lt 5) {
    Write-Host "Warning: PowerShell 5.0 or higher is recommended" -ForegroundColor Red
}

# Check Python
Write-Host "`nChecking Python..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
    
    # Check Python version
    $version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ([version]$version -lt [version]"3.8") {
        Write-Host "Error: Python 3.8 or higher is required" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✗ Python not found" -ForegroundColor Red
    Write-Host "Please download and install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Check pip
Write-Host "`nChecking pip..." -ForegroundColor Yellow
if (Get-Command pip -ErrorAction SilentlyContinue) {
    $pipVersion = pip --version
    Write-Host "✓ $pipVersion" -ForegroundColor Green
} else {
    Write-Host "✗ pip not found" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "`nChecking Node.js..." -ForegroundColor Yellow
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "✓ Node.js $nodeVersion" -ForegroundColor Green
    
    # Check version
    $version = node -p "process.version.slice(1).split('.')[0]"
    if ([int]$version -lt 16) {
        Write-Host "Warning: Node.js 16 or higher is recommended" -ForegroundColor Red
    }
} else {
    Write-Host "✗ Node.js not found" -ForegroundColor Red
    Write-Host "Please download and install Node.js 16+ from https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

# Check npm
Write-Host "`nChecking npm..." -ForegroundColor Yellow
if (Get-Command npm -ErrorAction SilentlyContinue) {
    $npmVersion = npm --version
    Write-Host "✓ npm $npmVersion" -ForegroundColor Green
} else {
    Write-Host "✗ npm not found" -ForegroundColor Red
    exit 1
}

# Check Docker (optional)
Write-Host "`nChecking Docker (optional)..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $dockerVersion = docker --version
    Write-Host "✓ $dockerVersion" -ForegroundColor Green
    
    # Check Docker Compose
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        $composeVersion = docker-compose --version
        Write-Host "✓ $composeVersion" -ForegroundColor Green
    } else {
        Write-Host "○ Docker Compose not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "○ Docker not found (optional component)" -ForegroundColor Yellow
}

# Check kubectl (optional)
Write-Host "`nChecking kubectl (optional)..." -ForegroundColor Yellow
if (Get-Command kubectl -ErrorAction SilentlyContinue) {
    $kubectlVersion = kubectl version --client --short 2>$null
    Write-Host "✓ $kubectlVersion" -ForegroundColor Green
} else {
    Write-Host "○ kubectl not found (optional component)" -ForegroundColor Yellow
}

Write-Host "`n=== Environment Check Complete ===" -ForegroundColor Green

# Ask if user wants to continue with installation
$response = Read-Host "`nContinue with dependency installation? (y/N)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "`nStarting dependency installation..." -ForegroundColor Green
    
    # Create Python virtual environment
    if (!(Test-Path "venv")) {
        Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to create virtual environment!" -ForegroundColor Red
            exit 1
        }
    }
    
    # Activate virtual environment and install dependencies
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Python dependency installation failed!" -ForegroundColor Red
        exit 1
    }
    
    # Install frontend dependencies
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Frontend dependency installation failed!" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
    
    Set-Location ..
    
    Write-Host "`n=== Installation Complete ===" -ForegroundColor Green
    Write-Host "Run './start-dev.ps1' to start development environment" -ForegroundColor Cyan
    Write-Host "Run './deploy.ps1 -Environment local' for Docker deployment" -ForegroundColor Cyan
} else {
    Write-Host "Installation cancelled" -ForegroundColor Yellow
}
