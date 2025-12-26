@echo off
setlocal EnableDelayedExpansion

REM Star Scout Bot - Startup Script for Windows

echo.
echo ==========================================
echo      Star Scout Bot - Starting Up
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)
for /f "delims=" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found %PYTHON_VERSION%

REM Check ADB
where adb >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] ADB is not installed or not in PATH.
    echo Please install Android Platform Tools and add to PATH.
    echo https://developer.android.com/tools/releases/platform-tools
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('adb --version ^| findstr "Version"') do set ADB_VERSION=%%i
echo [OK] Found ADB %ADB_VERSION%

REM Check Tesseract
where tesseract >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Tesseract OCR is not installed or not in PATH.
    echo Please install Tesseract OCR and add to PATH.
    echo https://github.com/UB-Mannheim/tesseract/wiki
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('tesseract --version 2^>^&1 ^| findstr "tesseract"') do set TESS_VERSION=%%i
echo [OK] Found %TESS_VERSION%

REM Setup Virtual Environment
if not exist ".venv" (
    echo.
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate Virtual Environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo [OK] Virtual environment activated
) else (
    echo [ERROR] Virtual environment scripts not found!
    pause
    exit /b 1
)

REM Check Dependencies
echo.
echo Checking dependencies...
python -c "import cv2, PIL, pytesseract" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing missing dependencies...
    pip install -r requirements.txt
) else (
    echo [OK] Python dependencies installed
)

REM Check ADB Device
echo.
echo Checking ADB device connection...
adb devices > adb_devices.tmp
findstr /C:"device" adb_devices.tmp | findstr /V "List" >nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] No ADB device connected!
    echo.
    echo Please connect your Android device and enable USB debugging.
    echo Or connect wirelessly:
    echo   adb tcpip 5555
    echo   adb connect ^<device-ip^>:5555
    del adb_devices.tmp
    pause
    exit /b 1
)
del adb_devices.tmp
echo [OK] Device connected

echo.
echo All checks passed! Starting bot...
echo ==========================================
echo.

python -m scout

pause
