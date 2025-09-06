# PowerShell script to build LeadSieveX standalone executable
Write-Host "Building LeadSieveX standalone executable..." -ForegroundColor Green
Write-Host

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Clean previous build
Write-Host "Cleaning previous build..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

# Build the executable
Write-Host "Building executable with PyInstaller..." -ForegroundColor Yellow
& ".\venv\Scripts\pyinstaller.exe" --clean build_exe.spec

# Check if build was successful
if (Test-Path "dist\LeadSieveX.exe") {
    Write-Host
    Write-Host "✅ BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host
    Write-Host "The executable has been created at: dist\LeadSieveX.exe" -ForegroundColor Cyan
    
    $fileInfo = Get-Item "dist\LeadSieveX.exe"
    $fileSizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
    Write-Host "File size: $fileSizeMB MB" -ForegroundColor Cyan
    
    Write-Host
    Write-Host "You can now distribute this single .exe file to run LeadSieveX" -ForegroundColor White
    Write-Host "without requiring Python installation on the target machine." -ForegroundColor White
    Write-Host
    
    # Ask if user wants to test the executable
    $test = Read-Host "Would you like to test the executable now? (y/n)"
    if ($test -eq "y" -or $test -eq "Y") {
        Write-Host "Starting LeadSieveX.exe..." -ForegroundColor Yellow
        Start-Process "dist\LeadSieveX.exe"
    }
} else {
    Write-Host
    Write-Host "❌ BUILD FAILED!" -ForegroundColor Red
    Write-Host "Check the output above for error messages." -ForegroundColor Red
    Write-Host
}

Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
