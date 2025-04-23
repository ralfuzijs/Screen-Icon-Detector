@echo off
echo Screen Icon Detector - Setup
echo ============================
echo.

:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python installation found.
echo.

:: Create a temporary directory for downloading
if not exist temp mkdir temp

:: Install required packages for setup
echo Installing required packages for setup...
python -m pip install --upgrade pip
python -m pip install requests

:: Download project files from GitHub repository
echo Downloading project files...
python -c "import requests; import os; import zipfile; url = 'https://github.com/yourusername/screen-icon-detector/archive/main.zip'; r = requests.get(url, stream=True); open('temp/main.zip', 'wb').write(r.content); print('Download complete'); zip = zipfile.ZipFile('temp/main.zip'); zip.extractall('temp'); zip.close()"

if %errorlevel% neq 0 (
    echo.
    echo Error downloading project files. Please check your internet connection.
    pause
    exit /b 1
)

:: Copy files from the downloaded package
echo Moving project files to current directory...
xcopy /s /e /y "temp\screen-icon-detector-main\*" "."
rmdir /s /q temp

:: Create necessary directories if they don't exist
if not exist templates mkdir templates
if not exist screenshots mkdir screenshots

echo Directories checked/created.
echo.

:: Install required packages
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Error installing packages. Please check if requirements.txt exists.
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo You can now run the program using:
echo   - editor.bat : To configure the automation
echo   - run.bat    : To run the automation with current settings
echo.
pause
