# EV Infotainment System - Run Script
# Quick launcher for the ADAS Dashboard

param(
    [switch]$SkipCarlaCheck,
    [switch]$StartCarla
)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "EV Infotainment System - ADAS Dashboard" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if CARLA exists in local directory
$carlaPath = ".\CARLA_0.9.15\WindowsNoEditor\CarlaUE4.exe"
if (-not (Test-Path $carlaPath)) {
    Write-Host "⚠️  CARLA Simulator not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Expected location: $carlaPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please download CARLA 0.9.15 from:" -ForegroundColor White
    Write-Host "https://github.com/carla-simulator/carla/releases/tag/0.9.15" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Extract the contents to: .\CARLA_0.9.15\WindowsNoEditor\" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Activate virtual environment if it exists
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

# Check if CARLA is running (unless skipped)
if (-not $SkipCarlaCheck) {
    Write-Host "Checking if CARLA is running..." -ForegroundColor Yellow
    $carlaRunning = Get-Process -Name "CarlaUE4-Win64-Shipping" -ErrorAction SilentlyContinue
    
    if (-not $carlaRunning) {
        Write-Host "WARNING: CARLA Simulator is not running!" -ForegroundColor Red
        Write-Host ""
        
        if ($StartCarla) {
            Write-Host "Starting CARLA from: $carlaPath" -ForegroundColor Green
            Start-Process -FilePath $carlaPath -WorkingDirectory (Split-Path $carlaPath)
            Write-Host "Waiting 15 seconds for CARLA to initialize..." -ForegroundColor Yellow
            Start-Sleep -Seconds 15
        } else {
            Write-Host "To start CARLA automatically, run: .\run.ps1 -StartCarla" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Or manually start CARLA:" -ForegroundColor Yellow
            Write-Host "  cd CARLA_0.9.15\WindowsNoEditor" -ForegroundColor White
            Write-Host "  .\CarlaUE4.exe" -ForegroundColor White
            Write-Host ""
            $continue = Read-Host "Press Enter when CARLA is running, or Ctrl+C to cancel"
        }
    } else {
        Write-Host "CARLA is running!" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Starting ADAS Dashboard..." -ForegroundColor Green
Write-Host ""
Write-Host "Controls:" -ForegroundColor Yellow
Write-Host "  W - Throttle | S - Brake | A/D - Steer" -ForegroundColor White
Write-Host "  SPACE - Reverse | ESC - Exit" -ForegroundColor White
Write-Host ""

# Run the dashboard
python src\adas_dashboard.py

Write-Host ""
Write-Host "ADAS Dashboard stopped." -ForegroundColor Cyan
