@echo off
echo ========================================
echo SkillMatchHub Backend Setup
echo ========================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo Step 4: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo Step 5: Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo .env file created. Please edit it with your settings.
) else (
    echo .env file already exists
)

echo Step 6: Running migrations...
python manage.py migrate
if errorlevel 1 (
    echo Error: Failed to run migrations
    pause
    exit /b 1
)

echo Step 7: Loading sample skills...
python manage.py load_sample_skills

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create a superuser: python manage.py createsuperuser
echo 2. Start the server: python manage.py runserver
echo 3. Visit http://localhost:8000/admin/
echo.
echo For background tasks (optional):
echo - Start Celery worker: celery -A config worker -l info
echo - Start Celery beat: celery -A config beat -l info
echo.
pause
