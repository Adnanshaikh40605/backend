@echo off
echo Setting up PostgreSQL for Windows...

REM Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    exit /b 1
)

REM Run the setup script
python setup_postgres.py

REM Check if the setup was successful
if %errorlevel% neq 0 (
    echo Setup failed. Please check the error messages above.
    pause
    exit /b 1
)

REM Run migrations
echo Running database migrations...
python manage.py migrate

REM Prompt to create a superuser
echo.
echo Would you like to create a superuser? (Y/N)
set /p create_user=
if /i "%create_user%"=="Y" (
    python manage.py createsuperuser
)

echo.
echo Setup completed successfully!
echo You can now run the server with: python manage.py runserver
echo.
pause 