# EV Infotainment System - Setup Script
# This script helps verify and set up your environment

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "EV Infotainment System - Setup Wizard" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/5] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green

if ($pythonVersion -notmatch "Python 3\.[78]") {
    Write-Host "WARNING: CARLA 0.9.15 requires Python 3.7 or 3.8" -ForegroundColor Red
    Write-Host "You may encounter compatibility issues." -ForegroundColor Red
}
Write-Host ""

# Check if virtual environment exists
Write-Host "[2/5] Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path ".\venv") {
    Write-Host "Virtual environment found!" -ForegroundColor Green
} else {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created!" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "[3/5] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Install requirements
Write-Host "[4/5] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "Dependencies installed!" -ForegroundColor Green
Write-Host ""

# Check for CARLA
Write-Host "[5/5] Checking CARLA installation..." -ForegroundColor Yellow

$carlaPath = ".\CARLA_0.9.15\WindowsNoEditor\CarlaUE4.exe"
$carlaApiPath = ".\CARLA_0.9.15\WindowsNoEditor\PythonAPI\carla\dist"

if (Test-Path $carlaPath) {
    Write-Host "✓ CARLA executable found at: $carlaPath" -ForegroundColor Green
    
    # Check for Python API
    if (Test-Path $carlaApiPath) {
        Write-Host "✓ CARLA Python API available" -ForegroundColor Green
        
        # Try to find .whl files
        $whlFiles = Get-ChildItem -Path $carlaApiPath -Filter "*.whl"
        if ($whlFiles) {
            Write-Host ""
            Write-Host "Available CARLA Python API wheels:" -ForegroundColor Cyan
            foreach ($whl in $whlFiles) {
                Write-Host "  - $($whl.Name)" -ForegroundColor White
            }
            Write-Host ""
            Write-Host "To install, run:" -ForegroundColor Yellow
            Write-Host "  pip install $carlaApiPath\<wheel-file-for-your-python-version>.whl" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "✗ CARLA not found at: $carlaPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download CARLA 0.9.15:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://github.com/carla-simulator/carla/releases/tag/0.9.15" -ForegroundColor White
    Write-Host "2. Extract to: .\CARLA_0.9.15\WindowsNoEditor\" -ForegroundColor White
    Write-Host ""
}

# Check if CARLA API is installed
try {
    python -c "import carla; print(f'CARLA version: {carla.__version__}')" 2>&1 | Out-Null
    $carlaInstalled = $?
} catch {
    $carlaInstalled = $false
}

if ($carlaInstalled) {
    Write-Host "✓ CARLA Python API is installed!" -ForegroundColor Green
    $carlaVersion = python -c "import carla; print(carla.__version__)"
    Write-Host "  Version: $carlaVersion" -ForegroundColor Green
} else {
    Write-Host "✗ CARLA Python API not installed" -ForegroundColor Red
    if (Test-Path $carlaApiPath) {
        Write-Host ""
        Write-Host "Install with:" -ForegroundColor Yellow
        Write-Host "  pip install $carlaApiPath\carla-0.9.15-cp38-cp38-win_amd64.whl" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Note: Choose the .whl file matching your Python version (cp37 for 3.7, cp38 for 3.8)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. If CARLA is not installed, download and extract it to .\CARLA_0.9.15\WindowsNoEditor\" -ForegroundColor White
Write-Host "2. Install CARLA Python API: pip install .\CARLA_0.9.15\WindowsNoEditor\PythonAPI\carla\dist\<wheel-file>.whl" -ForegroundColor White
Write-Host "3. Start CARLA: cd CARLA_0.9.15\WindowsNoEditor && .\CarlaUE4.exe" -ForegroundColor White
Write-Host "4. Run the dashboard: .\run.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Or use: .\run.ps1 -StartCarla (to auto-start CARLA)" -ForegroundColor Cyan
