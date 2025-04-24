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

:: Check if project is already set up by looking for key directories/files
if exist src\main.py (
    echo Project already appears to be set up.
    choice /C YN /M "Do you want to reinstall? (Y/N)"
    if errorlevel 2 goto SkipDownload
    echo.
    echo Performing clean reinstall...
    if exist temp rmdir /s /q temp
)

:: Create a temporary directory for downloading
if not exist temp mkdir temp

:: Create a temporary Python script to handle downloading
echo import requests > temp\download.py
echo import os >> temp\download.py
echo import sys >> temp\download.py
echo import zipfile >> temp\download.py
echo. >> temp\download.py
echo url = 'https://github.com/ralfuzijs/Screen-Icon-Detector/archive/main.zip' >> temp\download.py
echo print("Downloading from:", url) >> temp\download.py
echo try: >> temp\download.py
echo     r = requests.get(url, stream=True) >> temp\download.py
echo     if r.status_code != 200: >> temp\download.py
echo         print(f'Error: Server returned status code {r.status_code}') >> temp\download.py
echo         sys.exit(1) >> temp\download.py
echo     with open('temp/main.zip', 'wb') as f: >> temp\download.py
echo         f.write(r.content) >> temp\download.py
echo     print('Download complete') >> temp\download.py
echo     try: >> temp\download.py
echo         with zipfile.ZipFile('temp/main.zip') as zip_ref: >> temp\download.py
echo             zip_ref.extractall('temp') >> temp\download.py
echo         print('Extraction complete') >> temp\download.py
echo     except zipfile.BadZipFile: >> temp\download.py
echo         print('Error: Downloaded file is not a valid ZIP file') >> temp\download.py
echo         sys.exit(1) >> temp\download.py
echo     except Exception as e: >> temp\download.py
echo         print(f'Error extracting ZIP: {e}') >> temp\download.py
echo         sys.exit(1) >> temp\download.py
echo except Exception as e: >> temp\download.py
echo     print(f'Error downloading: {e}') >> temp\download.py
echo     sys.exit(1) >> temp\download.py

:: Install required packages for setup
echo Installing required packages for setup...
python -m pip install --upgrade pip
python -m pip install requests

:: Download project files from GitHub repository
echo Downloading project files...
echo This may take a moment, please wait...

:: Run the download script
python temp\download.py

if %errorlevel% neq 0 (
    echo.
    echo Error downloading or extracting project files.
    echo You may want to try again later or download manually from:
    echo https://github.com/ralfuzijs/Screen-Icon-Detector/
    pause
    exit /b 1
)

:: Copy files from the downloaded package
echo Moving project files to current directory...
:: First check which directory was extracted
dir temp /b > temp\dir_list.txt
:: Skip the download.py and main.zip files when looking for the directory
findstr /v /i "download.py main.zip dir_list.txt" temp\dir_list.txt > temp\filtered_list.txt
set /p EXTRACTED_DIR=<temp\filtered_list.txt
if not exist "temp\%EXTRACTED_DIR%" (
    echo Error: Could not find extracted directory.
    pause
    exit /b 1
)

xcopy /s /e /y "temp\%EXTRACTED_DIR%\*" "." > nul
rmdir /s /q temp

:SkipDownload
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
