# CARLA Directory Migration Guide
# This script helps you understand what needs to be moved out of the repository

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CARLA Directory Migration Guide" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$carlaDirectories = @('CarlaUE4', 'Engine', 'HDMaps', 'Plugins', 'PythonAPI', 'Co-Simulation')
$carlaFiles = @('CarlaUE4.exe', 'CHANGELOG', 'README', 'Dockerfile')

Write-Host "⚠️  WARNING: The following CARLA files are currently in your repository:" -ForegroundColor Yellow
Write-Host ""

# Check directories
$totalSize = 0
foreach ($dir in $carlaDirectories) {
    if (Test-Path $dir) {
        $size = (Get-ChildItem $dir -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
        $totalSize += $size
        Write-Host "  📁 $dir - $([math]::Round($size, 2)) MB" -ForegroundColor Red
    }
}

# Check files
foreach ($file in $carlaFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file -ErrorAction SilentlyContinue).Length / 1MB
        $totalSize += $size
        Write-Host "  📄 $file - $([math]::Round($size, 2)) MB" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "  Total Size: $([math]::Round($totalSize, 2)) MB (~$([math]::Round($totalSize/1024, 2)) GB)" -ForegroundColor Magenta
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 MIGRATION STEPS:" -ForegroundColor Green
Write-Host ""
Write-Host "These files belong to CARLA Simulator and should NOT be in this repository." -ForegroundColor Yellow
Write-Host ""

Write-Host "Option 1: Use .gitignore (RECOMMENDED)" -ForegroundColor Green
Write-Host "-----------------------------------------" -ForegroundColor Gray
Write-Host "The files are already in .gitignore, so they won't be committed to future changes." -ForegroundColor White
Write-Host "1. Make sure you have downloaded CARLA 0.9.15 separately to C:\CARLA_0.9.15\" -ForegroundColor White
Write-Host "2. These directories are already ignored by .gitignore" -ForegroundColor White
Write-Host "3. On your next commit, only your application files will be tracked" -ForegroundColor White
Write-Host ""

Write-Host "Option 2: Clean Repository (If you want to remove them locally)" -ForegroundColor Green
Write-Host "-----------------------------------------" -ForegroundColor Gray
Write-Host "⚠️  IMPORTANT: First make sure you have CARLA 0.9.15 downloaded separately!" -ForegroundColor Red
Write-Host ""
Write-Host "If you already have CARLA installed elsewhere (e.g., C:\CARLA_0.9.15\), you can" -ForegroundColor White
Write-Host "safely delete these directories from your project folder:" -ForegroundColor White
Write-Host ""

foreach ($dir in $carlaDirectories) {
    if (Test-Path $dir) {
        Write-Host "  Remove-Item -Path '$dir' -Recurse -Force" -ForegroundColor Cyan
    }
}

foreach ($file in $carlaFiles) {
    if (Test-Path $file) {
        Write-Host "  Remove-Item -Path '$file' -Force" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📁 CORRECT STRUCTURE:" -ForegroundColor Green
Write-Host ""
Write-Host "Your Project Repository (ev-infotainment-system):" -ForegroundColor Yellow
Write-Host "  ├── src/" -ForegroundColor White
Write-Host "  ├── assets/" -ForegroundColor White
Write-Host "  ├── logs/" -ForegroundColor White
Write-Host "  ├── docs/" -ForegroundColor White
Write-Host "  ├── requirements.txt" -ForegroundColor White
Write-Host "  ├── setup.ps1" -ForegroundColor White
Write-Host "  ├── run.ps1" -ForegroundColor White
Write-Host "  └── README.md" -ForegroundColor White
Write-Host ""

Write-Host "CARLA Installation (Separate Directory):" -ForegroundColor Yellow
Write-Host "  C:\CARLA_0.9.15\WindowsNoEditor\" -ForegroundColor White
Write-Host "  ├── CarlaUE4.exe" -ForegroundColor White
Write-Host "  ├── CarlaUE4/" -ForegroundColor White
Write-Host "  ├── Engine/" -ForegroundColor White
Write-Host "  ├── PythonAPI/" -ForegroundColor White
Write-Host "  └── ..." -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "❓ Do you have CARLA 0.9.15 installed separately?" -ForegroundColor Yellow
Write-Host ""
Write-Host "If NO  -> Download from: https://github.com/carla-simulator/carla/releases/tag/0.9.15" -ForegroundColor White
Write-Host "If YES -> You can clean up these directories from your project" -ForegroundColor White
Write-Host ""

Write-Host "For more information, see:" -ForegroundColor Cyan
Write-Host "  docs\DIRECTORY_STRUCTURE.md" -ForegroundColor White
Write-Host "  docs\INSTALLATION.md" -ForegroundColor White
Write-Host ""
