@echo off
REM USB Forensics Tool - Professional Edition Launcher
REM ===================================================
REM Developed by: Srirevanth A, Naghul Pranav C B, Deeekshitha
REM Version: 2.0 (December 2025)

echo.
echo ==========================================
echo USB Forensics Tool - Professional Edition
echo ==========================================
echo Developed by:
echo   * Srirevanth A
echo   * Naghul Pranav C B
echo   * Deeekshitha
echo.
echo Version: 2.0 (December 2025)
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import win32com.client" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing missing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Check Pillow
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing Pillow...
    pip install Pillow
    echo.
)

echo All dependencies OK!
echo.
echo Starting USB Forensics Tool - Professional Edition...
echo.
echo TIP: For full functionality, run as Administrator
echo.

REM Launch the unified main entry point
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application
    echo Check the error messages above
    pause
)

