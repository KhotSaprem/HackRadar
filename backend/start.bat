@echo off
echo Starting HackRadar Python Backend...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Copy database from Go backend if it exists and Python db doesn't
if exist "..\backend-go\hackradar.db" (
    if not exist "hackradar.db" (
        echo Copying database from Go backend...
        copy "..\backend-go\hackradar.db" "hackradar.db"
    )
)

REM Start the server
echo.
echo Starting FastAPI server on http://localhost:8000
echo.
python main.py
