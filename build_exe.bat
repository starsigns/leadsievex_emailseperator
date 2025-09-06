@echo off
echo Building LeadSieveX standalone executable...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Clean previous build
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Build the executable
echo Building executable with PyInstaller...
pyinstaller --clean build_exe.spec

REM Check if build was successful
if exist "dist\LeadSieveX.exe" (
    echo.
    echo ✅ BUILD SUCCESSFUL!
    echo.
    echo The executable has been created at: dist\LeadSieveX.exe
    echo File size: 
    dir "dist\LeadSieveX.exe" | find ".exe"
    echo.
    echo You can now distribute this single .exe file to run LeadSieveX
    echo without requiring Python installation on the target machine.
    echo.
    pause
) else (
    echo.
    echo ❌ BUILD FAILED!
    echo Check the output above for error messages.
    echo.
    pause
)
