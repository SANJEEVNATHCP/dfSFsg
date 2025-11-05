@echo off
REM Quick deployment script for Windows

echo ====================================
echo   AgroMitra - Quick Deploy Script
echo ====================================
echo.

REM Check if .env exists
if not exist .env (
    echo WARNING: .env file not found. Creating from template...
    copy .env.example .env
    echo Please edit .env file with your configuration
    pause
    exit /b 1
)

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Initialize database
echo.
echo Initializing database...
python -c "from working_app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"

REM Start server
echo.
echo ====================================
echo   Starting Production Server
echo ====================================
echo Server will run on: http://0.0.0.0:5000
echo Press Ctrl+C to stop
echo.

REM Check if Gunicorn is available (Windows alternative: waitress)
pip show gunicorn >nul 2>&1
if %ERRORLEVEL% == 0 (
    gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app
) else (
    echo Gunicorn not available on Windows. Using Flask development server.
    echo For production, consider using waitress-serve:
    echo   pip install waitress
    echo   waitress-serve --port=5000 wsgi:app
    echo.
    python working_app.py
)

pause
