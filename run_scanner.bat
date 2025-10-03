@echo off
echo ========================================
echo    EOL Scanner - Easy Run Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if input directory exists
if not exist "input" (
    echo Creating input directory...
    mkdir input
)

REM Check if output directory exists
if not exist "output" (
    echo Creating output directory...
    mkdir output
)

REM Check for CSV files in input directory
dir /b input\*.csv >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: No CSV files found in 'input' directory
    echo Please place your CSV files in the 'input' folder
    echo.
    echo Example CSV format:
    echo package_name,version
    echo python,3.8
    echo nodejs,14.21.3
    echo java,8
    echo.
    pause
    exit /b 1
)

echo Found CSV files in input directory:
dir /b input\*.csv

echo.
echo Starting EOL scan...
echo.

REM Install requirements if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install requirements
call venv\Scripts\activate.bat
pip install -r requirements.txt

REM Run the scanner
python eol_scanner.py -i input -o output

echo.
echo ========================================
echo    Scan completed!
echo ========================================
echo.
echo Results are in the 'output' directory:
dir /b output\

echo.
echo Press any key to exit...
pause >nul
