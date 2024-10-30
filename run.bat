@echo off
REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python to run this script.
    pause
    exit /b
)

REM Install pip if not present
python -m ensurepip --upgrade >nul 2>&1

REM Upgrade pip and install required packages
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install pillow
python -m pip install pygame

REM Run the Python script in a new window and close this batch window
echo Starting the script...
start "" python main.py
exit
